"""Guardado de figuras generadas en notebooks (matplotlib) bajo ``reports/figures/``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = _PROJECT_ROOT / "reports" / "figures"

NOTEBOOK_FIGURE_DIRS: dict[str, Path] = {
    "01_eda": FIGURES_DIR / "01_eda",
    "02_training": FIGURES_DIR / "02_training",
    "03_simulation": FIGURES_DIR / "03_simulation",
}


def save_notebook_figure(
    fig: Any,
    *,
    notebook: str,
    index: int,
    name: str,
    dpi: int = 150,
) -> Path:
    """
    Guarda una figura matplotlib en ``reports/figures/<notebook>/``.

    ``name`` debe ser un slug sin extensión (se añade ``.png``).
    ``dpi`` por defecto 150 (informes); subir a 300 si hace falta impresión.
    """
    try:
        out_dir = NOTEBOOK_FIGURE_DIRS[notebook]
    except KeyError as e:
        raise KeyError(
            f"notebook debe ser una de {sorted(NOTEBOOK_FIGURE_DIRS)}; recibido {notebook!r}"
        ) from e
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = name.strip().removesuffix(".png")
    path = out_dir / f"{index:02d}_{slug}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    return path
