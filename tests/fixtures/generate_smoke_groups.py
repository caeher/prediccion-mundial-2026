"""Genera tests/fixtures/world_cup_2026_smoke.json (48 equipos del CSV de features)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent.parent
FEATURES = REPO / "data" / "processed" / "features_dataset.csv"
OUT = REPO / "tests" / "fixtures" / "world_cup_2026_smoke.json"


def main() -> None:
    df = pd.read_csv(FEATURES)
    u = sorted(set(df["team_A"]) | set(df["team_B"]))
    if len(u) < 48:
        raise SystemExit(f"Se necesitan ≥48 equipos en {FEATURES}; hay {len(u)}.")
    rest = [t for t in u if t not in ("USA", "CAN", "MEX")]
    t48 = ["USA", "CAN", "MEX"] + rest[:45]
    letters = list("ABCDEFGHIJKL")
    groups = {letters[i]: t48[i * 4 : (i + 1) * 4] for i in range(12)}
    cfg = {"sim_date": "2026-06-11", "hosts": ["USA", "CAN", "MEX"], "groups": groups}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
