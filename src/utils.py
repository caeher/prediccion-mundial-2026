"""Utilidades compartidas: rutas, normalización de texto, mapeos y logging."""

from __future__ import annotations

import json
import logging
import random
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Raíz del proyecto (directorio que contiene `data/`, `src/`)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Figuras desde notebooks (implementación en ``notebook_figures`` para imports fiables en Jupyter).
from src.notebook_figures import (  # noqa: E402
    FIGURES_DIR,
    NOTEBOOK_FIGURE_DIRS,
    save_notebook_figure,
)


def setup_logging(level: int = logging.INFO) -> None:
    """Configura logging básico en consola (idempotente si ya hay handlers)."""
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def set_seed(seed: int = 42) -> None:
    """Fija semillas para reproducibilidad."""
    random.seed(seed)
    np.random.seed(seed)


def normalize_text(value: Any) -> str:
    """
    Normaliza texto para claves de mapeo: strip, NFKD, ASCII, minúsculas,
    espacios y puntuación común convertidos a guión bajo.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    s = str(value).strip()
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("utf-8")
    s = s.lower()
    s = re.sub(r"[\s\-'/.,]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def load_country_mapping() -> dict[str, str]:
    """Carga el diccionario {nombre_normalizado: código_FIFA_3letras}."""
    path = EXTERNAL_DIR / "countries_mapping.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. Ejecuta primero el pipeline de preprocessing "
            "(build_country_mapping_seed) o crea el archivo."
        )
    with path.open(encoding="utf-8") as f:
        data: dict[str, str] = json.load(f)
    # Normalizar claves por si el JSON tiene variantes
    return {normalize_text(k): str(v).strip().upper() for k, v in data.items()}


def load_team_confederation() -> dict[str, str]:
    """
    Devuelve {team_code: confederation_code} (UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC).
    """
    teams_path = RAW_DIR / "worldcup_data" / "teams.csv"
    if not teams_path.exists():
        logging.warning("No se encontró teams.csv; load_team_confederation devuelve dict vacío.")
        return {}
    teams = pd.read_csv(teams_path)
    out: dict[str, str] = {}
    for _, row in teams.iterrows():
        code = str(row["team_code"]).strip().upper()
        conf = str(row.get("confederation_code", "")).strip().upper()
        if code and conf:
            out[code] = conf
    return out
