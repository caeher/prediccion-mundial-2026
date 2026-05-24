"""Genera CSV mínimo para smoke test de calibración (splits temporales)."""
from pathlib import Path

import pandas as pd

cols = [
    "match_id",
    "date",
    "team_A",
    "team_B",
    "is_neutral",
    "tournament_type",
    "tournament_weight",
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
    "diff_elo",
    "diff_fifa_rank",
    "squad_value_ratio",
    "diff_top5_ratio",
    "diff_win_ratio",
    "diff_xg",
    "sample_weight",
    "result",
]
rows: list[list[float | int | str]] = []


def add_row(mid: str, d: str, r: int, w: float = 1.0, de: float = 100.0) -> None:
    rows.append(
        [
            mid,
            d,
            "AAA",
            "BBB",
            0,
            "friendly",
            1,
            "smoke",
            1600,
            50,
            0.1,
            0.2,
            0.5,
            1.0,
            1500,
            60,
            0.15,
            0.25,
            0.48,
            1.05,
            de,
            -10,
            1.1,
            -0.05,
            0.02,
            -0.05,
            w,
            r,
        ]
    )


for i in range(12):
    add_row(f"tr_{i}", f"2018-06-{i + 1:02d}", i % 3, w=0.5 + 0.01 * i, de=80.0 + i)
for i in range(18):
    add_row(f"va_{i}", f"2020-01-{i + 1:02d}", (i + 1) % 3, w=1.0, de=50.0 + 0.5 * i)
for i in range(10):
    add_row(f"te_{i}", f"2024-03-{i + 1:02d}", (i + 2) % 3, w=1.0, de=30.0 + i)
add_row("tr_mirror_m", "2018-08-01", 2, w=0.4, de=-120.0)

out = Path(__file__).resolve().parent / "features_calib_smoke.csv"
out.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows, columns=cols).to_csv(out, index=False)
print("wrote", out, "rows", len(rows))
