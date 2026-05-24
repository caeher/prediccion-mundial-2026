"""Fase 4: simulación Monte Carlo del Mundial 2026."""

from src.simulation.feature_provider import (
    MODEL_FEATURE_COLUMNS,
    build_matchup_feature_row,
    build_probability_tensor,
    build_team_snapshot,
    subset_feature_snapshot,
)
from src.simulation.monte_carlo import execute_monte_carlo
from src.simulation.tournament_rules import (
    GROUP_LETTERS,
    build_r32_pairs,
    load_annex_map,
    load_groups_config,
    play_bracket_tree,
    simulate_group_stage,
)

__all__ = [
    "MODEL_FEATURE_COLUMNS",
    "build_matchup_feature_row",
    "build_probability_tensor",
    "build_team_snapshot",
    "subset_feature_snapshot",
    "execute_monte_carlo",
    "GROUP_LETTERS",
    "build_r32_pairs",
    "load_annex_map",
    "load_groups_config",
    "play_bracket_tree",
    "simulate_group_stage",
]
