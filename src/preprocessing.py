"""
Pipeline Fase 1: ingesta multifuente, resolución de entidades, deduplicación,
filtro temporal (>=2000), esquema maestro con placeholders y exportación.
El mirroring A/B se aplica en Fase 2 (src.feature_engineering).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

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

# Aliases manuales: variantes frecuentes en martj42 / medios -> código FIFA (teams.csv)
MANUAL_TEAM_ALIASES: dict[str, str] = {
    "usa": "USA",
    "united_states": "USA",
    "ussr": "SUN",
    "soviet_union": "SUN",
    "west_germany": "DEU",
    "east_germany": "DDR",
    "germany_fr": "DEU",
    "czechoslovakia": "CSK",
    "yugoslavia": "YUG",
    "serbia_and_montenegro": "SCG",
    "zaire": "COD",
    "ivory_coast": "CIV",
    "cote_d_ivoire": "CIV",
    "cote_divoire": "CIV",
    "dr_congo": "COD",
    "congo_dr": "COD",
    "democratic_republic_of_congo": "COD",
    "congo_kinshasa": "COD",
    "republic_of_congo": "CGO",
    "congo_brazzaville": "CGO",
    "cape_verde": "CPV",
    "cabo_verde": "CPV",
    "eswatini": "SWZ",
    "swaziland": "SWZ",
    "south_korea": "KOR",
    "korea_republic": "KOR",
    "korea_south": "KOR",
    "north_korea": "PRK",
    "korea_dpr": "PRK",
    "korea_democratic_peoples_republic": "PRK",
    "iran": "IRN",
    "china_pr": "CHN",
    "china": "CHN",
    "chinese_taipei": "TWN",
    "taipei": "TWN",
    "uae": "ARE",
    "united_arab_emirates": "ARE",
    "timor_leste": "TLS",
    "east_timor": "TLS",
    "brunei": "BRU",
    "macau": "MAC",
    "hong_kong": "HKG",
    "laos": "LAO",
    "myanmar": "MYA",
    "burma": "MYA",
    "siam": "THA",
    "holland": "NLD",
    "netherlands": "NLD",
    "bosnia_herzegovina": "BIH",
    "bosnia_and_herzegovina": "BIH",
    "north_macedonia": "MKD",
    "macedonia": "MKD",
    "fyrom": "MKD",
    "england": "ENG",
    "scotland": "SCO",
    "wales": "WAL",
    "northern_ireland": "NIR",
    "republic_of_ireland": "IRL",
    "ireland": "IRL",
    "russia": "RUS",
    "serbia": "SRB",
    "montenegro": "MNE",
    "slovakia": "SVK",
    "czech_republic": "CZE",
    "czechia": "CZE",
    "kosovo": "KOS",
    "gibraltar": "GIB",
    "andorra": "AND",
    "malta": "MLT",
    "luxembourg": "LUX",
    "liechtenstein": "LIE",
    "san_marino": "SMR",
    "faroe_islands": "FRO",
    "greenland": "GRL",
    "curacao": "CUW",
    "anguilla": "AIA",
    "bermuda": "BER",
    "montserrat": "MSR",
    "cayman_islands": "CAY",
    "british_virgin_islands": "VGB",
    "us_virgin_islands": "VIR",
    "puerto_rico": "PUR",
    "guam": "GUM",
    "american_samoa": "ASA",
    "cook_islands": "COK",
    "samoa": "SAM",
    "tonga": "TGA",
    "fiji": "FIJ",
    "vanuatu": "VAN",
    "papua_new_guinea": "PNG",
    "solomon_islands": "SOL",
    "palau": "PLW",
    "micronesia": "FSM",
    "marshall_islands": "MHL",
    "nauru": "NRU",
    "tuvalu": "TUV",
    "kiribati": "KIR",
    "new_caledonia": "NCL",
    "tahiti": "TAH",
    "french_guiana": "GUF",
    "guadeloupe": "GLP",
    "martinique": "MTQ",
    "reunion": "REU",
    "mayotte": "MYT",
    "saint_martin": "SMN",
    "sint_maarten": "SXM",
    "south_africa": "ZAF",
    "south_sudan": "SSD",
    "zambia": "ZMB",
    "trinidad_tobago": "TTO",
    "trinidad_and_tobago": "TTO",
    "afghanistan": "AFG",
    "albania": "ALB",
    "armenia": "ARM",
    "azerbaijan": "AZE",
    "bahamas": "BAH",
    "bahrain": "BHR",
    "bangladesh": "BAN",
    "barbados": "BRB",
    "belarus": "BLR",
    "belize": "BLZ",
    "benin": "BEN",
    "bhutan": "BHU",
    "botswana": "BOT",
    "burkina_faso": "BFA",
    "burundi": "BDI",
    "cambodia": "CAM",
    "central_african_republic": "CAF",
    "chad": "CHA",
    "india": "IND",
    "indonesia": "IDN",
    "kazakhstan": "KAZ",
    "kenya": "KEN",
    "kyrgyzstan": "KGZ",
    "latvia": "LVA",
    "lebanon": "LBN",
    "liberia": "LBR",
    "libya": "LBY",
    "lithuania": "LTU",
    "madagascar": "MAD",
    "malaysia": "MAS",
    "maldives": "MDV",
    "mali": "MLI",
    "mauritania": "MTN",
    "mauritius": "MRI",
    "moldova": "MDA",
    "mongolia": "MGL",
    "mozambique": "MOZ",
    "namibia": "NAM",
    "nepal": "NEP",
    "nicaragua": "NCA",
    "niger": "NIG",
    "oman": "OMA",
    "pakistan": "PAK",
    "palestine": "PLE",
    "philippines": "PHI",
    "rwanda": "RWA",
    "sierra_leone": "SLE",
    "somalia": "SOM",
    "sri_lanka": "SRI",
    "sudan": "SDN",
    "suriname": "SUR",
    "syria": "SYR",
    "tajikistan": "TJK",
    "tanzania": "TAN",
    "turkmenistan": "TKM",
    "uganda": "UGA",
    "venezuela": "VEN",
    "vietnam": "VIE",
    "yemen": "YEM",
    "zimbabwe": "ZIM",
    "abkhazia": "ABK",
    "aland_islands": "ALA",
    "alderney": "ALD",
    "ambazonia": "AMB",
    "andalusia": "AND",
    "antigua_and_barbuda": "ATG",
    "arameans_suryoye": "ASY",
    "artsakh": "ART",
    "aruba": "ARU",
    "asturias": "AST",
    "aymara": "AYM",
    "barawa": "BRW",
    "basque_country": "BSQ",
    "biafra": "BIA",
    "bonaire": "BES",
    "brittany": "BRT",
    "canary_islands": "CNR",
    "cascadia": "CSC",
    "central_spain": "CSP",
    "chagos_islands": "IOT",
    "chameria": "CHM",
    "catalonia": "CAT",
        "chechnya": "CHE",
    "cilento": "CIL",
    "comoros": "COM",
    "congo": "CGO",
    "corsica": "COR",
    "county_of_nice": "NCE",
    "crimea": "CRI",
    "cyprus": "CYP",
    "darfur": "DAR",
    "delvidek": "DLV",
    "djibouti": "DJI",
    "dominica": "DMA",
    "dominican_republic": "DOM",
    "donetsk_pr": "DPR",
    "east_turkestan": "ETR",
    "elba_island": "ELB",
    "ellan_vannin": "EVM",
    "eritrea": "ERI",
    "estonia": "EST",
    "ethiopia": "ETH",
    "falkland_islands": "FLK",
    "felvidek": "FLV",
    "finland": "FIN",
    "franconia": "FRA",
    "frya": "FRY",
    "gabon": "GAB",
    "gagauzia": "GAG",
    "galicia": "GAL",
    "gambia": "GAM",
    "georgia": "GEO",
    "german_dr": "DDR",
    "gotland": "GTL",
    "gozo": "GOZ",
    "grenada": "GRN",
    "guatemala": "GUA",
    "guernsey": "GGY",
    "guinea": "GUI",
    "guinea_bissau": "GNB",
    "guyana": "GUY",
    "hitra": "HIT",
        "hmong": "HMO",
    "iraqi_kurdistan": "IKD",
    "isle_of_man": "IOM",
    "isle_of_wight": "IOW",
    "jersey": "JEY",
    "jordan": "JOR",
    "kabylia": "KAB",
    "karpatalja": "KRP",
    "kernow": "KER",
    "kurdistan": "KRD",
    "lesotho": "LES",
    "luhansk_pr": "LPR",
    "madrid": "MAD",
    "malawi": "MWI",
    "manchukuo": "MCH",
    "mapuche": "MAP",
    "matabeleland": "MTB",
    "maule_sur": "MSR",
    "menorca": "MEN",
    "monaco": "MCO",
    "niue": "NIU",
    "north_vietnam": "VNM",
    "northern_cyprus": "NCP",
    "northern_mariana_islands": "MNP",
    "occitania": "OCC",
    "orkney": "ORK",
    "padania": "PAD",
    "panjab": "PNJ",
    "parishes_of_jersey": "PRJ",
    "provence": "PRV",
    "quebec": "QBC",
    "raetia": "RAE",
    "republic_of_st_pauli": "RSP",
    "rhodes": "RHO",
    "romani_people": "ROM",
    "ryukyu": "RYU",
    "saare_county": "SAR",
    "saarland": "SAA",
    "saint_barthelemy": "BLM",
    "saint_helena": "SHN",
    

    # aliases corruptos
    "cte_d_ivoire": "CIV",
    "ir_iran": "IRN",
}

# Pares de columnas a intercambiar en el mirroring (orden: A primero, B segundo)
MIRROR_SWAP_PAIRS: list[tuple[str, str]] = [
    ("team_A", "team_B"),
    ("elo_A", "elo_B"),
    ("fifa_rank_A", "fifa_rank_B"),
    ("squad_value_A", "squad_value_B"),
    ("top5_ratio_A", "top5_ratio_B"),
    ("win_ratio_50_A", "win_ratio_50_B"),
    ("xg_computed_A", "xg_computed_B"),
]

def build_country_mapping_seed(teams_csv: Path | None = None, output_path: Path | None = None) -> Path:
    """
    Genera (o regenera) `data/external/countries_mapping.json` desde teams.csv
    más aliases manuales.
    """
    teams_csv = teams_csv or RAW_DIR / "worldcup_data" / "teams.csv"
    output_path = output_path or EXTERNAL_DIR / "countries_mapping.json"
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

    if not teams_csv.exists():
        raise FileNotFoundError(f"No se encuentra {teams_csv}. Ejecuta data_acquisition primero.")

    teams = pd.read_csv(teams_csv)
    mapping: dict[str, str] = {}
    for _, row in teams.iterrows():
        name = row.get("team_name")
        code = str(row.get("team_code", "")).strip().upper()
        if not code or pd.isna(name):
            continue
        key = normalize_text(name)
        if key:
            mapping[key] = code

    for alias_key, code in MANUAL_TEAM_ALIASES.items():
        nk = normalize_text(alias_key)
        if nk:
            mapping[nk] = code.upper()

    # Orden estable para JSON reproducible
    ordered = {k: mapping[k] for k in sorted(mapping.keys())}
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)
    logger.info("Mapeo de países escrito en %s (%d claves)", output_path, len(ordered))
    return output_path


def _known_codes_from_mapping(mapping: dict[str, str]) -> set[str]:
    return {str(v).strip().upper() for v in mapping.values() if str(v).strip()}


def standardize_team_names(
    df: pd.DataFrame,
    columns: list[str],
    mapping: dict[str, str],
    known_codes: set[str],
) -> set[str]:
    """
    Estandariza nombres/códigos de equipo a código FIFA de 3 letras.
    Devuelve el conjunto de claves normalizadas que no se pudieron resolver.
    """
    unmapped: set[str] = set()

    def resolve_one(raw: Any) -> str | float:
        if raw is None or (isinstance(raw, float) and np.isnan(raw)):
            return np.nan
        s = str(raw).strip()
        if not s:
            return np.nan
        if re.fullmatch(r"[A-Za-z]{3}", s):
            c = s.upper()
            if c in known_codes:
                return c
        key = normalize_text(raw)
        if key in mapping:
            return mapping[key]
        unmapped.add(key or s)
        return np.nan

    for col in columns:
        if col not in df.columns:
            continue
        df[col] = df[col].map(resolve_one)

    if unmapped:
        sample = sorted(unmapped)[:40]
        logger.warning(
            "Equipos no mapeados (muestra hasta 40): %s | total claves únicas: %d",
            sample,
            len(unmapped),
        )
    return unmapped


def classify_tournament(name: Any) -> str:
    """Clasifica el nombre de torneo en categorías de la rúbrica."""
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return "other"
    s = str(name).strip()
    if re.search(r"(?i)^FIFA World Cup$", s):
        return "world_cup"
    if re.search(r"(?i)qualification|qualifier", s):
        return "qualifier"
    if re.search(
        r"(?i)UEFA Euro|Copa Am|African Cup|AFC Asian|Asian Cup|Gold Cup|"
        r"OFC Nations|CONCACAF|Nations League|Africa Cup|Caribbean Cup",
        s,
    ):
        return "continental"
    if re.search(r"(?i)^Friendly$", s):
        return "friendly"
    return "other"


def compute_match_key_series(df: pd.DataFrame) -> pd.Series:
    """Clave única: YYYY-MM-DD_codigoMenor_codigoMayor (orden lexicográfico)."""
    h = df["home_team"].astype(str)
    a = df["away_team"].astype(str)
    lo = np.where(h <= a, h, a)
    hi = np.where(h > a, h, a)
    d = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return d + "_" + lo + "_" + hi


def load_martj42(path: Path | None = None) -> pd.DataFrame:
    path = path or RAW_DIR / "international_results.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce")
    df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce")
    df["neutral"] = df["neutral"].map(
        lambda x: str(x).strip().lower() in ("true", "1", "yes") if pd.notna(x) else False
    )
    df["source"] = "martj42"
    return df


def load_jfjelstul(path: Path | None = None) -> pd.DataFrame:
    path = path or RAW_DIR / "worldcup_data" / "matches.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    m = pd.read_csv(path)
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(m["match_date"], errors="coerce"),
            "home_team": m["home_team_code"].astype(str).str.strip().str.upper(),
            "away_team": m["away_team_code"].astype(str).str.strip().str.upper(),
            "home_score": pd.to_numeric(m["home_team_score"], errors="coerce"),
            "away_score": pd.to_numeric(m["away_team_score"], errors="coerce"),
            "tournament": "FIFA World Cup",
            "neutral": _neutral_from_host(
                m["country_name"].astype(str),
                m["home_team_name"].astype(str),
                m["away_team_name"].astype(str),
            ),
            "source": "jfjelstul",
        }
    )
    df["match_key"] = compute_match_key_series(df)
    return df


def _neutral_from_host(country: pd.Series, home_name: pd.Series, away_name: pd.Series) -> pd.Series:
    """True si el país anfitrión del partido no coincide con ninguno de los dos equipos."""

    def row_n(c: str, h: str, a: str) -> bool:
        cn = normalize_text(c)
        hn = normalize_text(h)
        an = normalize_text(a)
        if not cn:
            return True
        return cn not in {hn, an}

    return pd.Series(
        [row_n(c, h, a) for c, h, a in zip(country.tolist(), home_name.tolist(), away_name.tolist())],
        index=country.index,
    )


def load_kaggle_wc(path: Path | None = None) -> pd.DataFrame:
    path = path or RAW_DIR / "fifa-world-cup" / "WorldCupMatches.csv"
    if not path.exists():
        logger.warning("No existe %s; se omite la fuente Kaggle.", path)
        return pd.DataFrame()
    raw = pd.read_csv(path)
    dt = pd.to_datetime(raw["Datetime"].astype(str).str.strip(), format="%d %b %Y - %H:%M", errors="coerce")
    mask_bad = dt.isna()
    if mask_bad.any():
        dt2 = pd.to_datetime(raw.loc[mask_bad, "Datetime"].astype(str).str.strip(), errors="coerce")
        dt = dt.fillna(dt2)

    df = pd.DataFrame(
        {
            "date": dt,
            "home_team": raw["Home Team Name"],
            "away_team": raw["Away Team Name"],
            "home_score": pd.to_numeric(raw["Home Team Goals"], errors="coerce"),
            "away_score": pd.to_numeric(raw["Away Team Goals"], errors="coerce"),
            "tournament": "FIFA World Cup",
            "neutral": True,
            "source": "kaggle",
        }
    )
    return df


def merge_sources(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Concatena fuentes en orden de prioridad de confianza y elimina duplicados por match_key.
    Prioridad: jfjelstul > kaggle > martj42 (primera fila conservada).
    """
    priority = {"jfjelstul": 0, "kaggle": 1, "martj42": 2}
    parts = []
    for d in dfs:
        if d is None or d.empty:
            continue
        d = d.copy()
        d["_prio"] = d["source"].map(priority).fillna(9).astype(int)
        parts.append(d)
    if not parts:
        return pd.DataFrame()
    merged = pd.concat(parts, ignore_index=True)
    merged = merged.sort_values(["match_key", "_prio"], kind="mergesort")
    merged = merged.drop_duplicates(subset=["match_key"], keep="first")
    merged = merged.drop(columns=["_prio"])
    return merged.reset_index(drop=True)


def filter_modern_era(df: pd.DataFrame, cutoff_year: int = 2000) -> pd.DataFrame:
    out = df[df["date"].dt.year >= cutoff_year].copy()
    return out.reset_index(drop=True)


def assign_team_a_b(df: pd.DataFrame) -> pd.DataFrame:
    """
    Asigna team_A / team_B, is_neutral y result (0=gana A, 1=empate, 2=gana B).
    Si neutral: team_A = min(home, away), team_B = max lexicográfico.
    """
    out = df.copy()
    h = out["home_team"].astype(str)
    a = out["away_team"].astype(str)
    hs = out["home_score"].astype(float)
    ha = out["away_score"].astype(float)
    neu = out["neutral"].astype(bool).to_numpy()

    team_a = np.where(neu, np.where(h <= a, h, a), h)
    team_b = np.where(neu, np.where(h > a, h, a), a)
    home_is_a = team_a == h

    goals_a = np.where(home_is_a, hs, ha)
    goals_b = np.where(home_is_a, ha, hs)

    result = np.where(goals_a > goals_b, 0, np.where(goals_a == goals_b, 1, 2))
    out["team_A"] = team_a
    out["team_B"] = team_b
    out["is_neutral"] = neu.astype(np.int8)
    out["result"] = result.astype(np.int8)
    out["tournament_type"] = out["tournament"].map(classify_tournament)
    out["match_id"] = out["match_key"]
    return out


def add_schema_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for suffix in ("A", "B"):
        for base in (
            "elo",
            "fifa_rank",
            "squad_value",
            "top5_ratio",
            "win_ratio_50",
            "xg_computed",
        ):
            col = f"{base}_{suffix}"
            if col not in out.columns:
                out[col] = np.nan
    return out


def mirror_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Duplica filas invirtiendo A/B y el objetivo (0<->2)."""
    base = df.copy()
    mir = df.copy()
    for ca, cb in MIRROR_SWAP_PAIRS:
        if ca in mir.columns and cb in mir.columns:
            tmp = mir[ca].copy()
            mir[ca] = mir[cb]
            mir[cb] = tmp
    flip = {0: 2, 1: 1, 2: 0}
    mir["result"] = mir["result"].map(flip).astype(np.int8)
    mir["match_id"] = mir["match_id"].astype(str) + "_m"
    return pd.concat([base, mir], ignore_index=True)


def validate_and_save(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """Elimina filas inválidas y guarda CSV."""
    out = df.copy()
    before = len(out)
    key_cols = ["date", "team_A", "team_B", "result", "tournament_type", "match_id"]
    out = out.dropna(subset=key_cols)
    out = out.dropna(subset=["home_score", "away_score"])
    dropped = before - len(out)
    if dropped:
        logger.info("Filas descartadas por nulos en clave o marcador: %d", dropped)
    out["date"] = pd.to_datetime(out["date"]).dt.strftime("%Y-%m-%d")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Columnas finales en orden de la rúbrica
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
        if c not in out.columns:
            out[c] = np.nan
    out[final_cols].to_csv(output_path, index=False)
    logger.info("Guardado %s (%d filas)", output_path, len(out))
    return out


def _file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_preprocessing_report(
    path: Path,
    stats: dict[str, Any],
    unmapped: set[str],
    output_csv: Path,
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "=== Resumen preprocessing (Fase 1) ===",
        f"Filas tras merge: {stats.get('rows_after_merge', 'n/a')}",
        f"Filas tras filtro >=2000: {stats.get('rows_after_filter', 'n/a')}",
        f"Filas finales (sin mirror; mirroring en Fase 2): {stats.get('rows_final', 'n/a')}",
        f"Distribución result (final): {stats.get('result_counts', 'n/a')}",
        f"MD5 match_dataset.csv: {_file_md5(output_csv)}",
        f"Equipos no mapeados (únicos): {len(unmapped)}",
    ]
    if unmapped:
        lines.append("Muestra no mapeados: " + ", ".join(sorted(unmapped)[:80]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Reporte escrito en %s", path)


def main() -> None:
    setup_logging()
    set_seed(42)
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    build_country_mapping_seed()
    mapping_path = EXTERNAL_DIR / "countries_mapping.json"
    with mapping_path.open(encoding="utf-8") as f:
        mapping: dict[str, str] = {normalize_text(k): v.upper() for k, v in json.load(f).items()}
    known_codes = _known_codes_from_mapping(mapping)

    stats: dict[str, Any] = {}
    unmapped_all: set[str] = set()

    df_mj = load_martj42()
    unmapped_all |= standardize_team_names(df_mj, ["home_team", "away_team"], mapping, known_codes)
    df_mj["match_key"] = compute_match_key_series(df_mj)

    df_jf = load_jfjelstul()
    bad_jf = set()
    for col in ("home_team", "away_team"):
        for v in df_jf[col].dropna().unique():
            if str(v).upper() not in known_codes:
                bad_jf.add(str(v))
    if bad_jf:
        logger.warning("Códigos en jfjelstul no presentes en teams/mapping: %s", sorted(bad_jf)[:30])

    df_kg = load_kaggle_wc()
    if not df_kg.empty:
        unmapped_all |= standardize_team_names(df_kg, ["home_team", "away_team"], mapping, known_codes)
        df_kg["match_key"] = compute_match_key_series(df_kg)

    for d in (df_mj, df_jf, df_kg):
        if d is not None and not d.empty:
            d.dropna(subset=["home_team", "away_team", "date"], inplace=True)

    merged = merge_sources([df_jf, df_kg, df_mj])
    stats["rows_after_merge"] = len(merged)

    filtered = filter_modern_era(merged, cutoff_year=2000)
    stats["rows_after_filter"] = len(filtered)

    assigned = assign_team_a_b(filtered)
    with_placeholders = add_schema_placeholders(assigned)

    out_path = PROCESSED_DIR / "match_dataset.csv"
    final_df = validate_and_save(with_placeholders, out_path)
    stats["rows_final"] = len(final_df)
    stats["result_counts"] = dict(Counter(final_df["result"].astype(int).tolist()))

    write_preprocessing_report(
        REPORTS_DIR / "preprocessing_summary.txt",
        stats,
        unmapped_all,
        out_path,
    )

    # Confederation map disponible para Fase 2 (solo log de cobertura)
    conf = load_team_confederation()
    logger.info("Códigos con confederación conocida (teams.csv): %d", len(conf))


if __name__ == "__main__":
    main()
