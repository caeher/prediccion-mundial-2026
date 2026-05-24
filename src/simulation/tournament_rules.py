"""
Reglas FIFA Mundial 2026 (12 grupos, 8 mejores terceros, dieciseisavos).
Anexo C: data/external/annex_c_wc2026.json (495 combinaciones oficiales).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.simulation.feature_provider import FeatureSnapshot
from src.utils import EXTERNAL_DIR

logger = logging.getLogger(__name__)

GROUP_LETTERS: list[str] = list("ABCDEFGHIJKL")
POINTS_WIN = 3
POINTS_DRAW = 1

# Índice de slots 1A,1B,1D,1E,1G,1I,1K,1L vs terceros (Anexo C columnas)
SLOT_WINNER_GROUPS: tuple[str, ...] = ("A", "B", "D", "E", "G", "I", "K", "L")

ANNEX_C_PATH: Path = EXTERNAL_DIR / "annex_c_wc2026.json"
DEFAULT_GROUPS_PATH: Path = EXTERNAL_DIR / "world_cup_2026.json"

TBD_RE = re.compile(r"^TBD_", re.I)


@dataclass
class GroupPhaseOut:
    """Resultado fase de grupos + 8 terceros clasificados."""

    ordered: dict[str, list[str]]  # grupo -> [1º,2º,3º,4º]
    advancing_third_keys: str  # 8 letras ordenadas p.ej. 'CDEFGHIJ'
    annex_slots: tuple[str, ...]  # tercero de qué grupo va a cada slot vs 1A,1B,...


def load_annex_map(path: Path | None = None) -> dict[str, tuple[str, ...]]:
    p = path or ANNEX_C_PATH
    if not p.exists():
        raise FileNotFoundError(f"Falta Anexo C en {p}. Ejecuta scripts/parse_annex_c_wiki.py si hace falta.")
    raw = json.loads(p.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, ...]] = {}
    for row in raw:
        key = row["advancing_third_groups"]
        slots = tuple(str(x) for x in row["slots_ABDE_GIKL"])
        out[key] = slots
    return out


def _third_team(ordered: dict[str, list[str]], group_letter: str) -> str:
    return ordered[group_letter][2]


def _winner(ordered: dict[str, list[str]], g: str) -> str:
    return ordered[g][0]


def _runner_up(ordered: dict[str, list[str]], g: str) -> str:
    return ordered[g][1]


def sort_group_teams(
    teams: list[str],
    points: dict[str, int],
    snap: FeatureSnapshot,
    rng: np.random.Generator,
) -> list[str]:
    """
    Orden final en grupo: puntos desc, ELO desc, rank FIFA asc (1 mejor), ruido reproducible.
    """
    noise = {t: float(rng.random()) for t in teams}
    return sorted(
        teams,
        key=lambda t: (-points[t], -snap.elo(t), snap.fifa_rank(t), noise[t], t),
    )


def simulate_group_stage(
    groups: dict[str, list[str]],
    P: np.ndarray,
    team_to_idx: dict[str, int],
    snap: FeatureSnapshot,
    rng: np.random.Generator,
) -> GroupPhaseOut:
    """Simula 72 partidos de grupos (6 por grupo)."""
    ordered: dict[str, list[str]] = {}
    third_rows: list[dict[str, Any]] = []

    for g in GROUP_LETTERS:
        tms = list(groups[g])
        if len(tms) != 4:
            raise ValueError(f"Grupo {g} debe tener 4 equipos, hay {len(tms)}.")
        pts = {t: 0 for t in tms}
        for i in range(4):
            for j in range(i + 1, 4):
                a, b = tms[i], tms[j]
                ia, ib = team_to_idx[a], team_to_idx[b]
                pr = P[ia, ib]
                outc = int(rng.choice(3, p=pr))
                if outc == 0:
                    pts[a] += POINTS_WIN
                elif outc == 2:
                    pts[b] += POINTS_WIN
                else:
                    pts[a] += POINTS_DRAW
                    pts[b] += POINTS_DRAW
        rank = sort_group_teams(tms, pts, snap, rng)
        ordered[g] = rank
        third = rank[2]
        third_rows.append({"group": g, "team": third, "pts": pts[third], "elo": snap.elo(third)})

    third_rows.sort(key=lambda r: (-r["pts"], -r["elo"], r["group"]))
    best8 = third_rows[:8]
    advancing_key = "".join(sorted(r["group"] for r in best8))
    annex_map = load_annex_map()
    if advancing_key not in annex_map:
        raise KeyError(
            f"Combinación de terceros no encontrada en Anexo C: {advancing_key}. "
            "Verifica annex_c_wc2026.json."
        )
    annex_slots = annex_map[advancing_key]
    return GroupPhaseOut(ordered=ordered, advancing_third_keys=advancing_key, annex_slots=annex_slots)


def third_for_winner_slot(ordered: dict[str, list[str]], annex_slots: tuple[str, ...], winner_letter: str) -> str:
    """Equipo tercero que enfrenta al 1º del grupo `winner_letter` según Anexo C."""
    idx = SLOT_WINNER_GROUPS.index(winner_letter)
    src_g = annex_slots[idx]
    return _third_team(ordered, src_g)


def build_r32_pairs(ordered: dict[str, list[str]], annex_slots: tuple[str, ...]) -> list[tuple[str, str]]:
    """16 enfrentamientos en orden partido 73..88."""
    w = ordered
    m: list[tuple[str, str]] = []
    m.append((_runner_up(w, "A"), _runner_up(w, "B")))
    m.append((_winner(w, "E"), third_for_winner_slot(w, annex_slots, "E")))
    m.append((_winner(w, "F"), _runner_up(w, "C")))
    m.append((_winner(w, "C"), _runner_up(w, "F")))
    m.append((_winner(w, "I"), third_for_winner_slot(w, annex_slots, "I")))
    m.append((_runner_up(w, "E"), _runner_up(w, "I")))
    m.append((_winner(w, "A"), third_for_winner_slot(w, annex_slots, "A")))
    m.append((_winner(w, "L"), third_for_winner_slot(w, annex_slots, "L")))
    m.append((_winner(w, "D"), third_for_winner_slot(w, annex_slots, "D")))
    m.append((_winner(w, "G"), third_for_winner_slot(w, annex_slots, "G")))
    m.append((_runner_up(w, "K"), _runner_up(w, "L")))
    m.append((_winner(w, "H"), _runner_up(w, "J")))
    m.append((_winner(w, "B"), third_for_winner_slot(w, annex_slots, "B")))
    m.append((_winner(w, "J"), _runner_up(w, "H")))
    m.append((_winner(w, "K"), third_for_winner_slot(w, annex_slots, "K")))
    m.append((_runner_up(w, "D"), _runner_up(w, "G")))
    return m


# Índices 0..15 = partidos 73..88
R16_FROM_R32: list[tuple[int, int]] = [(1, 4), (0, 2), (3, 5), (6, 7), (10, 11), (8, 9), (13, 15), (12, 14)]
QF_FROM_R16: list[tuple[int, int]] = [(0, 1), (4, 5), (2, 3), (6, 7)]
SF_FROM_QF: list[tuple[int, int]] = [(0, 1), (2, 3)]


def play_bracket_tree(
    r32_pairs: list[tuple[str, str]],
    sim_ko: Any,
) -> tuple[str, str, str, frozenset[str]]:
    """
    sim_ko(a,b) -> (winner, loser).
    Devuelve (campeón, subcampeón, tercer lugar, semifinalistas).
    """
    if len(r32_pairs) != 16:
        raise ValueError("Se esperan 16 partidos de R32.")

    w32: list[str] = []
    for a, b in r32_pairs:
        win, _ = sim_ko(a, b)
        w32.append(win)

    def play_pairs(idxs: list[tuple[int, int]], prev: list[str]) -> list[str]:
        out: list[str] = []
        for i, j in idxs:
            win, _ = sim_ko(prev[i], prev[j])
            out.append(win)
        return out

    w16 = play_pairs(R16_FROM_R32, w32)
    w8 = play_pairs(QF_FROM_R16, w16)
    sf_winners: list[str] = []
    sf_losers: list[str] = []
    for i, j in SF_FROM_QF:
        win, lose = sim_ko(w8[i], w8[j])
        sf_winners.append(win)
        sf_losers.append(lose)
    semis = frozenset(sf_winners + sf_losers)
    champ, runner_up = sim_ko(sf_winners[0], sf_winners[1])
    third, _ = sim_ko(sf_losers[0], sf_losers[1])
    return champ, runner_up, third, semis


def _flatten_groups(groups: dict[str, list[str]]) -> list[str]:
    return [t for g in GROUP_LETTERS for t in groups[g]]


def _snake_mock_groups(team_codes: list[str]) -> dict[str, list[str]]:
    """Snake draft: 48 equipos en 12 grupos (4 por grupo)."""
    if len(team_codes) < 48:
        raise ValueError(f"Se necesitan 48 equipos para mock; hay {len(team_codes)}.")
    top = team_codes[:48]
    cols: list[list[str]] = [[] for _ in range(12)]
    for p, team in enumerate(top):
        r = p // 12
        c = p % 12
        if r % 2 == 1:
            c = 11 - c
        cols[c].append(team)
    return {GROUP_LETTERS[i]: cols[i] for i in range(12)}


def resolve_tbd_and_validate(
    groups: dict[str, list[str]],
    snap: FeatureSnapshot,
    rng: np.random.Generator,
) -> dict[str, list[str]]:
    """Sustituye placeholders TBD_* por equipos con ELO alto no usados."""
    used: set[str] = {t for g in GROUP_LETTERS for t in groups[g] if not TBD_RE.match(t)}
    pool = sorted((set(snap.team_features.keys()) - used), key=lambda t: -snap.elo(t))
    pi = 0
    out: dict[str, list[str]] = {}
    for g in GROUP_LETTERS:
        row: list[str] = []
        for t in groups[g]:
            if TBD_RE.match(t):
                while pi < len(pool) and pool[pi] in used:
                    pi += 1
                if pi >= len(pool):
                    raise ValueError("No hay suficientes equipos en el snapshot para reemplazar TBD_*.")
                repl = pool[pi]
                pi += 1
                used.add(repl)
                row.append(repl)
            else:
                if t not in snap.team_features:
                    raise ValueError(f"Equipo {t} sin features en snapshot.")
                row.append(t)
                used.add(t)
        out[g] = row
    return out


def load_groups_config(path: Path | None, snap: FeatureSnapshot, rng: np.random.Generator) -> dict[str, list[str]]:
    """
    Carga JSON de grupos o, si no existe, construye mock por top-ELO (snake).
    """
    p = path or DEFAULT_GROUPS_PATH
    if not p.exists():
        logger.warning("No existe %s; usando mock snake por ELO.", p)
        pool = sorted(snap.team_features.keys(), key=lambda t: -snap.elo(t))
        if len(pool) < 48:
            raise ValueError(
                f"Snapshot tiene solo {len(pool)} equipos; se necesitan 48 para la simulación. "
                "Usa international_results completo o reduce el alcance."
            )
        return _snake_mock_groups(pool)

    data = json.loads(Path(p).read_text(encoding="utf-8"))
    groups = {g: [str(x).strip().upper() for x in data["groups"][g]] for g in GROUP_LETTERS}
    return resolve_tbd_and_validate(groups, snap, rng)


def read_wc_json(path: Path) -> tuple[str, frozenset[str], dict[str, list[str]]]:
    """Lee sim_date, hosts y grupos en bruto (pueden incluir TBD_*)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sim_date = str(data.get("sim_date", "2026-06-11"))
    hosts = frozenset(str(x).strip().upper() for x in data.get("hosts", []))
    groups = {g: [str(x).strip().upper() for x in data["groups"][g]] for g in GROUP_LETTERS}
    return sim_date, hosts, groups


def teams_in_order(groups: dict[str, list[str]]) -> list[str]:
    """Orden fijo A..L y posición en grupo para tensor P."""
    return _flatten_groups(groups)
