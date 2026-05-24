"""
Snapshot de features as-of (Fase 2) para equipos del Mundial 2026.
Construye vectores alineados con el orden alfabético de columnas del modelo.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.feature_engineering import (
    asof_join_all,
    compute_elo_history,
    compute_fifa_rank_proxy,
    compute_goals_rolling,
    compute_squad_indices,
    compute_win_ratio_50,
    impute_by_confederation_year,
    load_intl_results_resolved,
)
from src.preprocessing import _known_codes_from_mapping
from src.utils import EXTERNAL_DIR, normalize_text, set_seed, setup_logging

logger = logging.getLogger(__name__)

# Orden alfabético = infer_feature_columns en train.py (debe coincidir con el .pkl)
MODEL_FEATURE_COLUMNS: list[str] = [
    "diff_elo",
    "diff_fifa_rank",
    "diff_top5_ratio",
    "diff_win_ratio",
    "diff_xg",
    "elo_A",
    "elo_B",
    "fifa_rank_A",
    "fifa_rank_B",
    "is_neutral",
    "squad_value_A",
    "squad_value_B",
    "squad_value_ratio",
    "top5_ratio_A",
    "top5_ratio_B",
    "tournament_weight",
    "win_ratio_50_A",
    "win_ratio_50_B",
    "xg_computed_A",
    "xg_computed_B",
]

DEFAULT_TEAM_FEATURES: dict[str, float] = {
    "elo": 1500.0,
    "fifa_rank": 100.0,
    "squad_value": 0.0,
    "top5_ratio": 0.0,
    "win_ratio_50": 0.5,
    "xg_computed": 1.0,
}

TOURNAMENT_WEIGHT_WC: int = 5


def ensure_teams_in_snapshot(snap: FeatureSnapshot, team_codes: list[str]) -> None:
    """Añade equipos ausentes con defaults (misma filosofía que imputación Fase 2)."""
    added: list[str] = []
    for t in team_codes:
        if t not in snap.team_features:
            snap.team_features[t] = dict(DEFAULT_TEAM_FEATURES)
            added.append(t)
    if added:
        preview = ", ".join(added[:30])
        more = " ..." if len(added) > 30 else ""
        logger.warning("Defaults as-of para %d equipos sin histórico previo: %s%s", len(added), preview, more)


@dataclass
class FeatureSnapshot:
    """Features por equipo (post-imputación) en la fecha de simulación."""

    sim_date: pd.Timestamp
    hosts: frozenset[str]
    team_features: dict[str, dict[str, float]] = field(default_factory=dict)

    def elo(self, team: str) -> float:
        return float(self.team_features[team]["elo"])

    def fifa_rank(self, team: str) -> float:
        return float(self.team_features[team]["fifa_rank"])


def _load_mapping_tuple() -> tuple[dict[str, str], set[str]]:
    mapping_path = EXTERNAL_DIR / "countries_mapping.json"
    if not mapping_path.exists():
        raise FileNotFoundError(f"Falta {mapping_path}. Ejecuta: python -m src.preprocessing")
    import json

    with mapping_path.open(encoding="utf-8") as f:
        raw = json.load(f)
    mapping = {normalize_text(k): str(v).strip().upper() for k, v in raw.items()}
    known = _known_codes_from_mapping(mapping)
    return mapping, known


def build_team_snapshot(sim_date: str | pd.Timestamp, seed: int = 42, hosts: frozenset[str] | None = None) -> FeatureSnapshot:
    """
    Calcula ELO, rank proxy, ratios y proxies de plantilla para todos los equipos
    presentes en international_results hasta sim_date (merge_asof con fecha-1 día).
    """
    setup_logging()
    set_seed(seed)
    sim_dt = pd.to_datetime(sim_date)
    mapping, known_codes = _load_mapping_tuple()
    intl = load_intl_results_resolved(mapping, known_codes)
    intl = intl[intl["date"] < sim_dt].copy()
    if intl.empty:
        raise ValueError(f"No hay partidos internacionales con date < {sim_dt}.")

    elo_hist = compute_elo_history(intl)
    wr_hist = compute_win_ratio_50(intl)
    xg_hist = compute_goals_rolling(intl, window_days=365)
    rank_hist = compute_fifa_rank_proxy(elo_hist)
    squad_idx = compute_squad_indices()

    teams = sorted(set(intl["home_team"]).union(set(intl["away_team"])))
    matches = pd.DataFrame(
        {
            "match_id": [f"_snap_{t}" for t in teams],
            "date": [sim_dt] * len(teams),
            "team_A": teams,
            "team_B": teams,
            "is_neutral": [1] * len(teams),
            "tournament_type": ["friendly"] * len(teams),
            "source": ["snapshot"] * len(teams),
            "result": [1] * len(teams),
        }
    )
    enriched = asof_join_all(matches, elo_hist, wr_hist, xg_hist, rank_hist, squad_idx)
    enriched = impute_by_confederation_year(enriched)

    out: dict[str, dict[str, float]] = {}
    for _, row in enriched.iterrows():
        t = str(row["team_A"])
        out[t] = {
            "elo": float(row["elo_A"]),
            "fifa_rank": float(row["fifa_rank_A"]),
            "squad_value": float(row["squad_value_A"]),
            "top5_ratio": float(row["top5_ratio_A"]),
            "win_ratio_50": float(row["win_ratio_50_A"]),
            "xg_computed": float(row["xg_computed_A"]),
        }
    return FeatureSnapshot(sim_date=sim_dt, hosts=hosts or frozenset(), team_features=out)


def subset_feature_snapshot(full: FeatureSnapshot, teams: list[str]) -> FeatureSnapshot:
    """Restringe un snapshot ya construido (p. ej. tras ensure_teams_in_snapshot) a 48 equipos."""
    missing = [t for t in teams if t not in full.team_features]
    if missing:
        logger.warning(
            "Equipos ausentes en snapshot al filtrar (defaults): %s",
            ", ".join(missing[:25]) + (" ..." if len(missing) > 25 else ""),
        )
    sub: dict[str, dict[str, float]] = {}
    for t in teams:
        sub[t] = dict(full.team_features[t]) if t in full.team_features else dict(DEFAULT_TEAM_FEATURES)
    return FeatureSnapshot(sim_date=full.sim_date, hosts=full.hosts, team_features=sub)


def build_team_snapshot_for_list(
    teams: list[str],
    sim_date: str | pd.Timestamp,
    hosts: frozenset[str] | None = None,
    seed: int = 42,
) -> FeatureSnapshot:
    """Compatibilidad: construye snapshot global y filtra a `teams`."""
    full = build_team_snapshot(sim_date, seed=seed, hosts=hosts)
    ensure_teams_in_snapshot(full, teams)
    return subset_feature_snapshot(full, teams)


def is_neutral_match(team_a: str, team_b: str, hosts: frozenset[str]) -> int:
    """1 neutral puro; 0 si al menos uno es anfitrión (ventaja local simplificada)."""
    if team_a in hosts or team_b in hosts:
        return 0
    return 1


def build_matchup_feature_row(
    team_a: str,
    team_b: str,
    snap: FeatureSnapshot,
    *,
    is_neutral: int,
    tournament_weight: int = TOURNAMENT_WEIGHT_WC,
) -> np.ndarray:
    """Vector 1 x n_features en orden MODEL_FEATURE_COLUMNS."""
    fa = snap.team_features[team_a]
    fb = snap.team_features[team_b]
    row: dict[str, float] = {
        "elo_A": fa["elo"],
        "elo_B": fb["elo"],
        "fifa_rank_A": fa["fifa_rank"],
        "fifa_rank_B": fb["fifa_rank"],
        "squad_value_A": fa["squad_value"],
        "squad_value_B": fb["squad_value"],
        "top5_ratio_A": fa["top5_ratio"],
        "top5_ratio_B": fb["top5_ratio"],
        "win_ratio_50_A": fa["win_ratio_50"],
        "win_ratio_50_B": fb["win_ratio_50"],
        "xg_computed_A": fa["xg_computed"],
        "xg_computed_B": fb["xg_computed"],
        "diff_elo": fa["elo"] - fb["elo"],
        "diff_fifa_rank": fb["fifa_rank"] - fa["fifa_rank"],
        "squad_value_ratio": fa["squad_value"] / (fb["squad_value"] + 1e-5),
        "diff_top5_ratio": fa["top5_ratio"] - fb["top5_ratio"],
        "diff_win_ratio": fa["win_ratio_50"] - fb["win_ratio_50"],
        "diff_xg": fa["xg_computed"] - fb["xg_computed"],
        "is_neutral": float(is_neutral),
        "tournament_weight": float(tournament_weight),
    }
    vec = np.array([row[c] for c in MODEL_FEATURE_COLUMNS], dtype=np.float64).reshape(1, -1)
    return vec


def build_probability_tensor(
    teams: list[str],
    snap: FeatureSnapshot,
    model: Any,
    hosts: frozenset[str],
) -> np.ndarray:
    """
    Tensor simétrico P[i,j,:] con probs [P(A), P(E), P(B)] para teams[i] vs teams[j], i<j.
    Diagonal NaN; P[j,i] es el espejo (intercambia clases 0 y 2).
    """
    n = len(teams)
    P = np.full((n, n, 3), np.nan, dtype=np.float64)
    rows: list[np.ndarray] = []
    ij: list[tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            ia, ib = teams[i], teams[j]
            neu = is_neutral_match(ia, ib, hosts)
            rows.append(build_matchup_feature_row(ia, ib, snap, is_neutral=neu)[0])
            ij.append((i, j))
    if not rows:
        return P
    X = np.vstack(rows)
    probs = model.predict_proba(X)
    for k, (i, j) in enumerate(ij):
        p = probs[k].astype(np.float64)
        P[i, j] = p
        P[j, i] = np.array([p[2], p[1], p[0]], dtype=np.float64)
    return P


def validate_model_feature_order(model: Any) -> None:
    """Comprueba alineación con feature_names_in_ del XGB base o n_features_in_."""
    base = getattr(model, "base_estimator", model)
    names = getattr(base, "feature_names_in_", None)
    if names is None:
        n_in = getattr(base, "n_features_in_", None)
        if n_in is not None and int(n_in) != len(MODEL_FEATURE_COLUMNS):
            raise ValueError(
                f"n_features_in_={n_in} no coincide con {len(MODEL_FEATURE_COLUMNS)} columnas esperadas."
            )
        logger.warning("El modelo base no expone feature_names_in_; validación por n_features_in_ solamente.")
        return
    got = [str(x) for x in names]
    if got != MODEL_FEATURE_COLUMNS:
        raise ValueError(
            "Orden/nombre de features del modelo no coincide con MODEL_FEATURE_COLUMNS.\n"
            f" modelo: {got}\n esperado: {MODEL_FEATURE_COLUMNS}"
        )
