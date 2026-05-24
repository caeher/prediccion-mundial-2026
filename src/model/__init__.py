"""Modelado y calibración probabilística (Fase 3)."""

from src.model.calibration import (
    IsotonicCalibratedClassifier,
    brier_score_multiclass,
    calibrate_isotonic,
    evaluate_probabilities,
)

__all__ = [
    "IsotonicCalibratedClassifier",
    "brier_score_multiclass",
    "calibrate_isotonic",
    "evaluate_probabilities",
    "train_and_calibrate_pipeline",
]


def __getattr__(name: str):
    if name == "train_and_calibrate_pipeline":
        from src.model.train import train_and_calibrate_pipeline as _train

        return _train
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
