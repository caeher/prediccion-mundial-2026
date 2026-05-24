"""
Monte Carlo del Mundial 2026: fase de grupos + knockout con bracket FIFA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.simulation.feature_provider import (
    MODEL_FEATURE_COLUMNS,
    build_probability_tensor,
    build_team_snapshot,
    ensure_teams_in_snapshot,
    subset_feature_snapshot,
    validate_model_feature_order,
)
from src.simulation.tournament_rules import (
    DEFAULT_GROUPS_PATH,
    GROUP_LETTERS,
    TBD_RE,
    build_r32_pairs,
    load_groups_config,
    play_bracket_tree,
    read_wc_json,
    resolve_tbd_and_validate,
    simulate_group_stage,
    teams_in_order,
)
from src.utils import PROJECT_ROOT, REPORTS_DIR, set_seed, setup_logging

logger = logging.getLogger(__name__)

DEFAULT_MODEL = PROJECT_ROOT / "models" / "final_xgboost.pkl"


def wilson_ci(p: np.ndarray, n: int, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    """Intervalo de Wilson 95% para proporción binomial (vectorizado)."""
    p = np.clip(p.astype(np.float64), 0.0, 1.0)
    nn = max(int(n), 1)
    zz = z * z
    denom = 1.0 + zz / nn
    centre = (p + zz / (2.0 * nn)) / denom
    margin = z * np.sqrt((p * (1.0 - p) / nn + zz / (4.0 * nn * nn))) / denom
    return np.clip(centre - margin, 0.0, 1.0), np.clip(centre + margin, 0.0, 1.0)


def _file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def simulate_elimination_winner(
    team_a: str,
    team_b: str,
    team_to_idx: dict[str, int],
    P: np.ndarray,
    rng: np.random.Generator,
) -> tuple[str, str]:
    """Eliminación directa: renormaliza sin empate; devuelve (ganador, perdedor)."""
    ia, ib = team_to_idx[team_a], team_to_idx[team_b]
    pr = P[ia, ib]
    p_win_a = float(pr[0] / (pr[0] + pr[2] + 1e-15))
    pick = rng.random()
    if pick < p_win_a:
        return team_a, team_b
    return team_b, team_a


def run_one_iteration(
    groups: dict[str, list[str]],
    P: np.ndarray,
    team_to_idx: dict[str, int],
    snap: Any,
    rng: np.random.Generator,
) -> tuple[str, str, str, frozenset[str]]:
    gout = simulate_group_stage(groups, P, team_to_idx, snap, rng)
    r32 = build_r32_pairs(gout.ordered, gout.annex_slots)

    def sim_ko(a: str, b: str) -> tuple[str, str]:
        return simulate_elimination_winner(a, b, team_to_idx, P, rng)

    return play_bracket_tree(r32, sim_ko)


def execute_monte_carlo(
    groups: dict[str, list[str]],
    snap: Any,
    model: Any,
    hosts: frozenset[str],
    iterations: int = 10_000,
    seed: int = 42,
) -> pd.DataFrame:
    """Ejecuta N simulaciones y devuelve DataFrame ordenado por probabilidad de título."""
    validate_model_feature_order(model)
    teams = teams_in_order(groups)
    team_to_idx = {t: i for i, t in enumerate(teams)}
    P = build_probability_tensor(teams, snap, model, hosts)

    rng_master = np.random.default_rng(seed)
    champs: Counter[str] = Counter()
    finals: Counter[str] = Counter()
    semis: Counter[str] = Counter()

    for it in range(iterations):
        rng = np.random.default_rng(int(rng_master.integers(0, 2**31 - 1)))
        champ, runner_up, _third, semi_teams = run_one_iteration(groups, P, team_to_idx, snap, rng)
        champs[champ] += 1
        finals[champ] += 1
        finals[runner_up] += 1
        for t in semi_teams:
            semis[t] += 1

    all_teams = sorted(set(teams))
    n = iterations
    rows = []
    for t in all_teams:
        pc = champs[t] / n
        pf = finals[t] / n
        ps = semis[t] / n
        lo_c, hi_c = wilson_ci(np.array([pc]), n)
        lo_f, hi_f = wilson_ci(np.array([pf]), n)
        lo_s, hi_s = wilson_ci(np.array([ps]), n)
        rows.append(
            {
                "Selección": t,
                "Victorias_Titulo": champs[t],
                "Probabilidad_Campeón": pc,
                "Probabilidad_Final": pf,
                "Probabilidad_Semi": ps,
                "IC95_Campeon_Lo": float(lo_c[0]),
                "IC95_Campeon_Hi": float(hi_c[0]),
                "IC95_Final_Lo": float(lo_f[0]),
                "IC95_Final_Hi": float(hi_f[0]),
                "IC95_Semi_Lo": float(lo_s[0]),
                "IC95_Semi_Hi": float(hi_s[0]),
            }
        )
    df = pd.DataFrame(rows)
    df = df.sort_values("Probabilidad_Campeón", ascending=False).reset_index(drop=True)
    return df


def _load_groups_and_snapshot(
    groups_path: Path | None,
    sim_date_override: str | None,
    seed: int,
) -> tuple[dict[str, list[str]], Any, frozenset[str], str | None]:
    """Carga/resuelve grupos y construye snapshot de features."""
    rng0 = np.random.default_rng(seed)
    if groups_path and groups_path.exists():
        sim_date, hosts, raw_groups = read_wc_json(groups_path)
        if sim_date_override:
            sim_date = sim_date_override
        snap_full = build_team_snapshot(sim_date, seed=seed, hosts=hosts)
        flat_raw = [t for g in GROUP_LETTERS for t in raw_groups[g] if not TBD_RE.match(str(t).strip().upper())]
        ensure_teams_in_snapshot(snap_full, flat_raw)
        groups = resolve_tbd_and_validate(raw_groups, snap_full, rng0)
        teams = teams_in_order(groups)
        snap = subset_feature_snapshot(snap_full, teams)
        return groups, snap, hosts, sim_date
    sim_date = sim_date_override or "2026-06-11"
    hosts = frozenset(["USA", "CAN", "MEX"])
    snap_full = build_team_snapshot(sim_date, seed=seed, hosts=hosts)
    groups = load_groups_config(None, snap_full, rng0)
    teams = teams_in_order(groups)
    ensure_teams_in_snapshot(snap_full, teams)
    snap = subset_feature_snapshot(snap_full, teams)
    return groups, snap, hosts, sim_date


def write_summary(
    path: Path,
    *,
    iterations: int,
    seed: int,
    model_path: Path,
    groups_path: Path | None,
    sim_date: str | None,
    df: pd.DataFrame,
    groups: dict[str, list[str]],
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "=== Resumen simulación Monte Carlo (Fase 4) ===",
        f"Iteraciones: {iterations}",
        f"Semilla: {seed}",
        f"Modelo: {model_path}",
        f"MD5 modelo: {_file_md5(model_path)}",
        f"Grupos JSON: {groups_path or '(mock snake — sin archivo)'}",
        f"sim_date: {sim_date}",
        "",
        "Grupos resueltos (A–L):",
    ]
    for g in GROUP_LETTERS:
        lines.append(f"  {g}: {', '.join(groups[g])}")
    lines.append("")
    lines.append("Top 10 probabilidad campeón (Wilson 95%):")
    top = df.head(10)
    for _, r in top.iterrows():
        lines.append(
            f"  {r['Selección']}: p={r['Probabilidad_Campeón']:.4f} "
            f"[{r['IC95_Campeon_Lo']:.4f}, {r['IC95_Campeon_Hi']:.4f}]"
        )
    lines.append("")
    lines.append(f"Columnas features modelo ({len(MODEL_FEATURE_COLUMNS)}): " + ", ".join(MODEL_FEATURE_COLUMNS))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Resumen escrito en %s", path)


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Simulación Monte Carlo Mundial 2026 (Fase 4).")
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--groups", type=Path, default=DEFAULT_GROUPS_PATH, help="JSON de grupos o omitir para mock.")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--sim-date", type=str, default=None, help="Sobrescribe sim_date del JSON.")
    parser.add_argument("--out", type=Path, default=REPORTS_DIR / "monte_carlo_top5.csv")
    parser.add_argument("--summary", type=Path, default=REPORTS_DIR / "monte_carlo_summary.txt")
    args = parser.parse_args()

    set_seed(args.seed)
    model = joblib.load(args.model_path)
    groups, snap, hosts, sim_date = _load_groups_and_snapshot(
        args.groups if args.groups.exists() else None,
        args.sim_date,
        args.seed,
    )
    # Si --groups apunta a archivo inexistente, tratar como mock
    gpath = args.groups if args.groups.exists() else None

    df = execute_monte_carlo(groups, snap, model, hosts, iterations=args.iterations, seed=args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    write_summary(
        args.summary,
        iterations=args.iterations,
        seed=args.seed,
        model_path=args.model_path,
        groups_path=gpath,
        sim_date=sim_date,
        df=df,
        groups=groups,
    )
    logger.info("CSV resultados: %s (MD5 %s)", args.out, _file_md5(args.out))
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
