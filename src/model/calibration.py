"""Utilidades de calibración isotónica y métricas probabilísticas (Fase 3)."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import label_binarize
from sklearn.utils.validation import check_is_fitted

# Etiquetas fijas multiclase (0=gana A, 1=empate, 2=gana B)
CLASS_LABELS: list[int] = [0, 1, 2]


def brier_score_multiclass(y_true: np.ndarray, probs: np.ndarray) -> float:
    """
    Brier multiclase: promedio por muestra de sum_k (p_k - y_onehot_k)^2.
    Misma definición que en la consigna (sin dividir por n_classes).
    """
    y_true = np.asarray(y_true, dtype=int).ravel()
    probs = np.asarray(probs, dtype=float)
    if probs.ndim != 2 or probs.shape[1] != len(CLASS_LABELS):
        raise ValueError(f"probs debe ser (n, {len(CLASS_LABELS)}); forma={probs.shape}")
    y_oh = np.zeros_like(probs, dtype=float)
    for k in CLASS_LABELS:
        y_oh[:, k] = (y_true == k).astype(float)
    return float(np.mean(np.sum((probs - y_oh) ** 2, axis=1)))


class IsotonicCalibratedClassifier(ClassifierMixin, BaseEstimator):
    """
    Calibración isotónica multiclase estilo One-vs-Rest + renorm (equiv. a
    `CalibratedClassifierCV(..., method='isotonic')` sobre un conjunto fijo).

    scikit-learn >= 1.8 ya no admite `cv='prefit'` en `CalibratedClassifierCV`;
    este estimador ajusta isótonas sobre `predict_proba` del modelo base ya
    entrenado usando solo (X_val, y_val), sin re-entrenar el base.
    """

    def __init__(self, base_estimator: Any = None):
        self.base_estimator = base_estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> IsotonicCalibratedClassifier:
        if self.base_estimator is None:
            raise ValueError("base_estimator es obligatorio.")
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=int).ravel()
        if X.ndim != 2:
            raise ValueError("X debe ser 2D.")
        self.classes_ = np.array(CLASS_LABELS, dtype=int)
        n_classes = len(self.classes_)
        raw = self.base_estimator.predict_proba(X)
        if raw.shape[1] != n_classes:
            raise ValueError(
                f"predict_proba tiene {raw.shape[1]} columnas; se esperaban {n_classes}."
            )
        Y_bin = label_binarize(y, classes=self.classes_.tolist())
        if Y_bin.shape[1] != n_classes:
            raise ValueError("label_binarize no produjo la forma esperada.")
        self.calibrators_: list[IsotonicRegression] = []
        for k in range(n_classes):
            iso = IsotonicRegression(out_of_bounds="clip")
            iso.fit(raw[:, k], Y_bin[:, k])
            self.calibrators_.append(iso)
        if hasattr(self.base_estimator, "n_features_in_"):
            self.n_features_in_ = int(self.base_estimator.n_features_in_)
        else:
            self.n_features_in_ = X.shape[1]
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        check_is_fitted(self, "calibrators_")
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError("X debe ser 2D.")
        raw = self.base_estimator.predict_proba(X)
        cols = [iso.predict(raw[:, k]) for k, iso in enumerate(self.calibrators_)]
        q = np.column_stack(cols).astype(np.float64, copy=False)
        q = np.clip(q, 1e-12, 1.0)
        q /= q.sum(axis=1, keepdims=True)
        return q

    def predict(self, X: np.ndarray) -> np.ndarray:
        probas = self.predict_proba(X)
        return self.classes_[np.argmax(probas, axis=1)]


def calibrate_isotonic(base_model: Any, X_val: np.ndarray, y_val: np.ndarray) -> IsotonicCalibratedClassifier:
    """Calibra probabilidades del modelo base con isotónica OvR sobre (X_val, y_val)."""
    cal = IsotonicCalibratedClassifier(base_estimator=base_model)
    cal.fit(X_val, y_val)
    return cal


def evaluate_probabilities(
    name: str,
    y_true: np.ndarray,
    probs: np.ndarray,
    labels: list[int] | None = None,
) -> dict[str, dict[str, float | int]]:
    """Devuelve {name: {log_loss, brier_multiclass, n}}."""
    labels = labels or CLASS_LABELS
    y_true = np.asarray(y_true, dtype=int).ravel()
    probs = np.asarray(probs, dtype=float)
    ll = float(log_loss(y_true, probs, labels=labels))
    brier = brier_score_multiclass(y_true, probs)
    return {name: {"log_loss": ll, "brier_multiclass": brier, "n": int(len(y_true))}}
