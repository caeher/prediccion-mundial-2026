"""
Fase 2: enriquecer `match_dataset.csv` con ELO, ratios y proxies usando solo `data/raw/`.
Ejecutar después de `python -m src.preprocessing`.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.preprocessing import (
    _known_codes_from_mapping,
    classify_tournament,
    load_martj42,
    standardize_team_names,
)
from src.utils import (
    EXTERNAL_DIR,
    PROCESSED_DIR,
    RAW_DIR,
    REPORTS_DIR,
    load_team_confederation,
    normalize_text,
    set_seed,
    setup_logging,
)

logger = logging.getLogger(__name__)

K_BY_TYPE: dict[str, int] = {
    "world_cup": 60,
    "continental": 50,
    "qualifier": 40,
    "friendly": 20,
    "other": 30,
}

FEATURE_COLS_A = [
    "elo_A",
    "fifa_rank_A",
    "squad_value_A",
    "top5_ratio_A",
    "win_ratio_50_A",
    "xg_computed_A",
]
FEATURE_COLS_B = [c.replace("_A", "_B") for c in FEATURE_COLS_A]


def _load_mapping() -> tuple[dict[str, str], set[str]]:
    mapping_path = EXTERNAL_DIR / "countries_mapping.json"
    if not mapping_path.exists():
        raise FileNotFoundError(f"Ejecuta preprocessing primero: falta {mapping_path}")
    with mapping_path.open(encoding="utf-8") as f:
        raw = json.load(f)
    mapping = {normalize_text(k): str(v).strip().upper() for k, v in raw.items()}
    known = _known_codes_from_mapping(mapping)
    return mapping, known


def load_intl_results_resolved(
    mapping: dict[str, str],
    known_codes: set[str],
) -> pd.DataFrame:
    """international_results con códigos FIFA-3; todo el histórico (sin filtro de año)."""
    df = load_martj42()
    standardize_team_names(df, ["home_team", "away_team"], mapping, known_codes)
    df["tournament_type"] = df["tournament"].map(classify_tournament)
    df = df.dropna(subset=["home_team", "away_team", "date", "home_score", "away_score"])
    df = df.sort_values(["date", "home_team", "away_team"], kind="mergesort").reset_index(drop=True)
    return df


def _goal_margin_multiplier(home_score: float, away_score: float) -> float:
    margin = abs(int(home_score) - int(away_score))
    if margin <= 1:
        return 1.0
    if margin == 2:
        return 1.5
    return (11.0 + margin) / 8.0


def compute_elo_history(intl: pd.DataFrame) -> pd.DataFrame:
    """
    ELO estilo World Football ELO sobre todo el histórico.
    Devuelve una fila por participación: team, date, elo_before, elo_after.
    """
    ratings: dict[str, float] = defaultdict(lambda: 1500.0)
    rows: list[dict[str, Any]] = []

    for _, r in intl.iterrows():
        home = str(r["home_team"])
        away = str(r["away_team"])
        dt = pd.Timestamp(r["date"])
        hs = float(r["home_score"])
        as_ = float(r["away_score"])
        neutral = bool(r["neutral"])
        k = float(K_BY_TYPE.get(str(r["tournament_type"]), 30))
        g = _goal_margin_multiplier(hs, as_)

        rh = ratings[home] + (0.0 if neutral else 100.0)
        ra = ratings[away]
        we = 1.0 / (1.0 + 10.0 ** ((ra - rh) / 400.0))

        if hs > as_:
            wh, wa = 1.0, 0.0
        elif hs < as_:
            wh, wa = 0.0, 1.0
        else:
            wh, wa = 0.5, 0.5

        elo_bh = ratings[home]
        elo_ba = ratings[away]

        dh = k * g * (wh - we)
        da = k * g * (wa - (1.0 - we))

        ratings[home] = elo_bh + dh
        ratings[away] = elo_ba + da

        rows.append({"team": home, "date": dt, "elo_before": elo_bh, "elo_after": ratings[home]})
        rows.append({"team": away, "date": dt, "elo_before": elo_ba, "elo_after": ratings[away]})

    out = pd.DataFrame(rows)
    out = out.sort_values(["team", "date"], kind="mergesort").reset_index(drop=True)
    return out


def compute_win_ratio_50(intl: pd.DataFrame) -> pd.DataFrame:
    """Últimos 50 partidos con fecha estrictamente menor que el partido actual."""
    appearances: list[tuple[str, pd.Timestamp, int]] = []
    for _, r in intl.iterrows():
        d = pd.Timestamp(r["date"])
        hs, as_ = float(r["home_score"]), float(r["away_score"])
        h, a = str(r["home_team"]), str(r["away_team"])
        if hs > as_:
            appearances.append((h, d, 1))
            appearances.append((a, d, 0))
        elif hs < as_:
            appearances.append((h, d, 0))
            appearances.append((a, d, 1))
        else:
            appearances.append((h, d, 0))
            appearances.append((a, d, 0))

    appearances.sort(key=lambda x: (x[0], x[1]))
    by_team: dict[str, list[tuple[pd.Timestamp, int]]] = defaultdict(list)
    rows: list[dict[str, Any]] = []

    for team, d, win in appearances:
        hist = by_team[team]
        prior = [(dd, w) for dd, w in hist if dd < d]
        last50 = prior[-50:]
        if last50:
            wr = sum(w for _, w in last50) / len(last50)
        else:
            wr = np.nan
        rows.append({"team": team, "date": d, "win_ratio_50": wr})
        hist.append((d, win))
        by_team[team] = hist

    return pd.DataFrame(rows).sort_values(["team", "date"], kind="mergesort").reset_index(drop=True)


def compute_goals_rolling(intl: pd.DataFrame, window_days: int = 365) -> pd.DataFrame:
    """Proxy de xG: media de goles a favor en partidos con fecha en (date-window, date)."""
    appearances: list[tuple[str, pd.Timestamp, float]] = []
    for _, r in intl.iterrows():
        d = pd.Timestamp(r["date"])
        hs, as_ = float(r["home_score"]), float(r["away_score"])
        h, a = str(r["home_team"]), str(r["away_team"])
        appearances.append((h, d, hs))
        appearances.append((a, d, as_))
    appearances.sort(key=lambda x: (x[0], x[1]))

    by_team: dict[str, list[tuple[pd.Timestamp, float]]] = defaultdict(list)
    rows: list[dict[str, Any]] = []
    delta = pd.Timedelta(days=window_days)

    for team, d, gf in appearances:
        hist = by_team[team]
        window = [(dd, g) for dd, g in hist if d - delta <= dd < d]
        if window:
            xg = float(np.mean([g for _, g in window]))
        else:
            xg = np.nan
        rows.append({"team": team, "date": d, "xg_computed": xg})
        hist.append((d, gf))
        by_team[team] = hist

    return pd.DataFrame(rows).sort_values(["team", "date"], kind="mergesort").reset_index(drop=True)


def compute_fifa_rank_proxy(elo_hist: pd.DataFrame) -> pd.DataFrame:
    """
    Ranking mensual (1 = mejor) según elo_after del último partido jugado hasta el cierre de mes.
    """
    hmm = elo_hist.copy()
    hmm["date"] = pd.to_datetime(hmm["date"])
    hmm = hmm.sort_values("date", kind="mergesort")
    min_m = hmm["date"].min().to_period("M")
    max_m = hmm["date"].max().to_period("M")
    month_ends = pd.period_range(min_m, max_m, freq="M").to_timestamp(how="end")

    all_rows = list(hmm.itertuples(index=False))
    idx = 0
    n = len(all_rows)
    last_by_team: dict[str, float] = {}
    rank_rows: list[dict[str, Any]] = []

    for me in month_ends:
        me_ts = pd.Timestamp(me)
        while idx < n and pd.Timestamp(all_rows[idx].date) <= me_ts:
            last_by_team[str(all_rows[idx].team)] = float(all_rows[idx].elo_after)
            idx += 1
        if not last_by_team:
            continue
        ser = pd.Series(last_by_team, dtype=float)
        rk = ser.rank(method="min", ascending=False)
        for team, rkv in rk.items():
            rank_rows.append({"team": str(team), "date": me_ts, "fifa_rank": float(rkv)})

    return pd.DataFrame(rank_rows).sort_values(["team", "date"], kind="mergesort").reset_index(drop=True)


def _parse_tournament_years(list_tournaments: Any) -> list[int]:
    if list_tournaments is None or (isinstance(list_tournaments, float) and np.isnan(list_tournaments)):
        return []
    s = str(list_tournaments).strip()
    if not s or s.lower() in ("nan", "not applicable"):
        return []
    years: list[int] = []
    for part in re.split(r"[,;/]", s):
        part = part.strip()
        if not part:
            continue
        m = re.search(r"(19|20)\d{2}", part)
        if m:
            years.append(int(m.group(0)))
    return years


def compute_squad_indices() -> pd.DataFrame:
    """
    Proxies solo Mundial: top5_ratio = fracción con experiencia previa en WC;
    squad_value = media de mundiales previos por jugador, normalizada [0,1] por torneo.
    """
    squads_path = RAW_DIR / "worldcup_data" / "squads.csv"
    players_path = RAW_DIR / "worldcup_data" / "players.csv"
    tour_path = RAW_DIR / "worldcup_data" / "tournaments.csv"
    if not (squads_path.exists() and players_path.exists() and tour_path.exists()):
        logger.warning("Faltan squads/players/tournaments; squad proxies vacíos.")
        return pd.DataFrame(columns=["team", "date", "top5_ratio", "squad_value"])

    squads = pd.read_csv(squads_path)
    players = pd.read_csv(players_path).drop_duplicates(subset=["player_id"], keep="first")
    tournaments = pd.read_csv(tour_path)

    tmap = tournaments.set_index("tournament_id")["start_date"].to_dict()
    tour_year: dict[str, int] = {}
    for tid, sd in tmap.items():
        try:
            tour_year[str(tid)] = int(str(sd)[:4])
        except (TypeError, ValueError):
            continue

    pinfo = players.set_index("player_id")
    rows_out: list[dict[str, Any]] = []

    for (tid, tcode), g in squads.groupby(["tournament_id", "team_code"]):
        tid_s = str(tid)
        tcode_s = str(tcode).strip().upper()
        if tid_s not in tmap:
            continue
        start = pd.to_datetime(tmap[tid_s], errors="coerce")
        if pd.isna(start):
            continue
        ty = tour_year.get(tid_s)
        if ty is None:
            ty = int(start.year)

        top5_vals: list[float] = []
        squad_vals: list[float] = []

        for pid in g["player_id"].astype(str):
            if pid not in pinfo.index:
                top5_vals.append(0.0)
                squad_vals.append(0.0)
                continue
            row = pinfo.loc[pid]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            try:
                ct = int(float(row.get("count_tournaments", 0)))
            except (TypeError, ValueError):
                ct = 0
            years = _parse_tournament_years(row.get("list_tournaments", np.nan))
            prior_years = [y for y in years if y < ty]
            prior_n = len(prior_years)
            exp_player = 1.0 if (ct >= 2 or prior_n >= 1) else 0.0
            top5_vals.append(exp_player)
            squad_vals.append(float(prior_n))

        raw_top5 = float(np.mean(top5_vals)) if top5_vals else 0.0
        raw_squad = float(np.mean(squad_vals)) if squad_vals else 0.0
        rows_out.append(
            {
                "team": tcode_s,
                "date": pd.Timestamp(start),
                "top5_ratio": raw_top5,
                "squad_value_raw": raw_squad,
                "tournament_id": tid_s,
            }
        )

    if not rows_out:
        return pd.DataFrame(columns=["team", "date", "top5_ratio", "squad_value"])

    df = pd.DataFrame(rows_out)
    max_by_t = df.groupby("tournament_id")["squad_value_raw"].transform("max").replace(0, np.nan)
    df["squad_value"] = (df["squad_value_raw"] / max_by_t).fillna(0.0)
    df = df.drop(columns=["squad_value_raw", "tournament_id"])
    df = df.sort_values(["team", "date"], kind="mergesort").reset_index(drop=True)
    return df


def _merge_asof_team(
    matches: pd.DataFrame,
    feat: pd.DataFrame,
    value_col: str,
    out_col: str,
    team_col: str,
) -> pd.DataFrame:
    """Une features (team, date, value_col) a matches por team_col y fecha as-of."""
    if feat.empty:
        out = matches.copy()
        out[out_col] = np.nan
        return out

    mdt = pd.to_datetime(matches["_merge_date"], errors="coerce")
    left = pd.DataFrame(
        {
            "_ord": np.arange(len(matches), dtype=np.int64),
            "team": matches[team_col].astype(str),
            "_merge_date": mdt,
        }
    )
    right = feat[["team", "date", value_col]].copy()
    right["team"] = right["team"].astype(str)
    right["date"] = pd.to_datetime(right["date"], errors="coerce")
    right = right.rename(columns={value_col: out_col})
    right = right.sort_values(["team", "date"], kind="mergesort")

    out_series = pd.Series(np.nan, index=np.arange(len(matches)), dtype=float)
    for tid in left["team"].unique():
        lg = left[left["team"] == tid].sort_values("_merge_date", kind="mergesort")
        rg = right[right["team"] == tid][["date", out_col]].sort_values("date", kind="mergesort")
        if rg.empty or lg.empty:
            continue
        merged = pd.merge_asof(
            lg,
            rg,
            left_on="_merge_date",
            right_on="date",
            direction="backward",
        )
        out_series.loc[merged["_ord"].to_numpy()] = merged[out_col].to_numpy()

    out = matches.copy()
    out[out_col] = out_series.to_numpy()
    return out


def asof_join_all(
    matches: pd.DataFrame,
    elo_hist: pd.DataFrame,
    wr_hist: pd.DataFrame,
    xg_hist: pd.DataFrame,
    rank_hist: pd.DataFrame,
    squad_idx: pd.DataFrame,
) -> pd.DataFrame:
    m = matches.copy()
    m["_merge_date"] = pd.to_datetime(m["date"]) - pd.Timedelta(days=1)

    elo = elo_hist.rename(columns={"elo_before": "elo"})[["team", "date", "elo"]]
    m = _merge_asof_team(m, elo, "elo", "elo_A", "team_A")
    m = _merge_asof_team(m, elo, "elo", "elo_B", "team_B")

    m = _merge_asof_team(m, wr_hist, "win_ratio_50", "win_ratio_50_A", "team_A")
    m = _merge_asof_team(m, wr_hist, "win_ratio_50", "win_ratio_50_B", "team_B")

    m = _merge_asof_team(m, xg_hist, "xg_computed", "xg_computed_A", "team_A")
    m = _merge_asof_team(m, xg_hist, "xg_computed", "xg_computed_B", "team_B")

    m = _merge_asof_team(m, rank_hist, "fifa_rank", "fifa_rank_A", "team_A")
    m = _merge_asof_team(m, rank_hist, "fifa_rank", "fifa_rank_B", "team_B")

    if not squad_idx.empty:
        m = _merge_asof_team(m, squad_idx, "top5_ratio", "top5_ratio_A", "team_A")
        m = _merge_asof_team(m, squad_idx, "top5_ratio", "top5_ratio_B", "team_B")
        m = _merge_asof_team(m, squad_idx, "squad_value", "squad_value_A", "team_A")
        m = _merge_asof_team(m, squad_idx, "squad_value", "squad_value_B", "team_B")
    else:
        for c in ("top5_ratio_A", "top5_ratio_B", "squad_value_A", "squad_value_B"):
            m[c] = np.nan

    m = m.drop(columns=["_merge_date"], errors="ignore")
    return m


def impute_by_confederation_year(df: pd.DataFrame) -> pd.DataFrame:
    conf = load_team_confederation()
    out = df.copy()
    out["_year"] = pd.to_datetime(out["date"]).dt.year

    defaults: dict[str, float] = {
        "elo": 1500.0,
        "fifa_rank": 100.0,
        "squad_value": 0.0,
        "top5_ratio": 0.0,
        "win_ratio_50": 0.5,
        "xg_computed": 1.0,
    }

    def fill_col(team_col: str, col: str) -> None:
        base = col.rsplit("_", 1)[0]
        fallback = defaults.get(base, 0.0)
        cc = out[team_col].map(conf)
        med_conf_year = (
            out.assign(_conf=cc)
            .groupby(["_conf", "_year"], dropna=False)[col]
            .transform("median")
        )
        m = out[col].isna()
        out.loc[m, col] = med_conf_year[m]

        med_conf = out.assign(_conf=cc).groupby("_conf", dropna=False)[col].transform("median")
        m = out[col].isna()
        out.loc[m, col] = med_conf[m]

        gmed = out[col].median()
        if pd.isna(gmed):
            gmed = fallback
        out[col] = out[col].fillna(gmed)

    for col in FEATURE_COLS_A + FEATURE_COLS_B:
        if col in out.columns:
            fill_col("team_A" if col.endswith("_A") else "team_B", col)

    out = out.drop(columns=["_year"], errors="ignore")
    return out


def _file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_report(
    path: Path,
    nan_before: dict[str, int],
    nan_after: dict[str, int],
    out_csv: Path,
    wr_hist: pd.DataFrame,
    elo_hist: pd.DataFrame,
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "=== Resumen feature_engineering (Fase 2) ===",
        "NaN por columna (antes de imputación):",
    ]
    for k, v in sorted(nan_before.items()):
        lines.append(f"  {k}: {v}")
    lines.append("NaN por columna (después de imputación):")
    for k, v in sorted(nan_after.items()):
        lines.append(f"  {k}: {v}")
    lines.append(f"MD5 match_dataset.csv: {_file_md5(out_csv)}")

    # Equipos sin 50 partidos previos (muestra): win_ratio basado en <50
    wr_nan = wr_hist[wr_hist["win_ratio_50"].isna()]["team"].unique()[:40]
    lines.append("Equipos con al menos una aparición sin partidos previos (win_ratio NaN antes impute): " + ", ".join(map(str, wr_nan)))

    # Distribución ELO por confederación (según último elo_after en intl)
    conf = load_team_confederation()
    last_elo = elo_hist.sort_values("date").groupby("team").last()["elo_after"]
    rows = []
    for team, elo in last_elo.items():
        c = conf.get(str(team), "UNK")
        rows.append((c, float(elo)))
    if rows:
        edf = pd.DataFrame(rows, columns=["conf", "elo"])
        lines.append("ELO final (último partido en intl) por confederación — count / mean / median:")
        for conf_code, g in edf.groupby("conf"):
            lines.append(
                f"  {conf_code}: n={len(g)} mean={g['elo'].mean():.1f} median={g['elo'].median():.1f}"
            )

    lines.append(
        "Auditoría no-leakage: features unidos con merge_asof direction=backward "
        "y fecha_partido - 1 día como clave izquierda."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Reporte escrito en %s", path)


def main() -> None:
    setup_logging()
    set_seed(42)

    mapping, known_codes = _load_mapping()
    intl = load_intl_results_resolved(mapping, known_codes)

    out_path = PROCESSED_DIR / "match_dataset.csv"
    if not out_path.exists():
        raise FileNotFoundError(f"No existe {out_path}. Ejecuta: python -m src.preprocessing")

    matches = pd.read_csv(out_path)
    for c in ("gdp_capita_A", "gdp_capita_B"):
        if c in matches.columns:
            matches = matches.drop(columns=[c])

    feature_cols = [c for c in FEATURE_COLS_A + FEATURE_COLS_B if c in matches.columns]
    nan_before = {c: int(matches[c].isna().sum()) for c in feature_cols}

    elo_hist = compute_elo_history(intl)
    wr_hist = compute_win_ratio_50(intl)
    xg_hist = compute_goals_rolling(intl, window_days=365)
    rank_hist = compute_fifa_rank_proxy(elo_hist)
    squad_idx = compute_squad_indices()

    enriched = asof_join_all(matches, elo_hist, wr_hist, xg_hist, rank_hist, squad_idx)
    enriched = impute_by_confederation_year(enriched)

    nan_after = {c: int(enriched[c].isna().sum()) for c in feature_cols if c in enriched.columns}

    final_cols = [
        "match_id",
        "date",
        "team_A",
        "team_B",
        "is_neutral",
        "tournament_type",
        "source",
        "elo_A",
        "fifa_rank_A",
        "squad_value_A",
        "top5_ratio_A",
        "win_ratio_50_A",
        "xg_computed_A",
        "elo_B",
        "fifa_rank_B",
        "squad_value_B",
        "top5_ratio_B",
        "win_ratio_50_B",
        "xg_computed_B",
        "result",
    ]
    for c in final_cols:
        if c not in enriched.columns:
            enriched[c] = np.nan
    enriched[final_cols].to_csv(out_path, index=False)
    logger.info("Guardado %s (%d filas)", out_path, len(enriched))

    _write_report(
        REPORTS_DIR / "feature_engineering_summary.txt",
        nan_before,
        nan_after,
        out_path,
        wr_hist,
        elo_hist,
    )


if __name__ == "__main__":
    main()
