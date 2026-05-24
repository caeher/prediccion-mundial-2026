"""
Entrenamiento XGBoost multiclase + calibración isotónica y evaluación
temporal (Log-Loss, Brier multiclase). Ejecutar tras `python -m src.feature_engineering`.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import argparse
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from src.model.calibration import IsotonicCalibratedClassifier, calibrate_isotonic, evaluate_probabilities
from src.utils import PROCESSED_DIR, PROJECT_ROOT, REPORTS_DIR, set_seed, setup_logging

logger = logging.getLogger(__name__)

FEATURE_EXCLUDE: frozenset[str] = frozenset(
    {
        "match_id",
        "date",
        "team_A",
        "team_B",
        "tournament_type",
        "source",
        "result",
        "sample_weight",
    }
)


def _file_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_features(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe {path}. Ejecuta: python -m src.feature_engineering")
    df = pd.read_csv(path)
    for col in ("result", "sample_weight", "match_id", "date"):
        if col not in df.columns:
            raise ValueError(f"Falta columna requerida '{col}' en {path}")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Hay fechas inválidas en la columna 'date'.")
    df["year"] = df["date"].dt.year.astype(int)
    return df


def temporal_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_df = df[df["year"] <= 2018].copy()
    val_df = df[(df["year"] > 2018) & (df["year"] <= 2022)].copy()
    test_df = df[df["year"] > 2022].copy()
    return train_df, val_df, test_df


def drop_mirror(df: pd.DataFrame) -> pd.DataFrame:
    mid = df["match_id"].astype(str)
    return df[~mid.str.endswith("_m")].copy()


def infer_feature_columns(df: pd.DataFrame) -> list[str]:
    feats = [c for c in df.columns if c not in FEATURE_EXCLUDE and c != "year"]
    # Solo numéricas para XGBoost
    num_feats: list[str] = []
    for c in feats:
        if pd.api.types.is_numeric_dtype(df[c]):
            num_feats.append(c)
        else:
            logger.warning("Excluyendo columna no numérica de features: %s", c)
    return sorted(num_feats)


def build_xy(
    df: pd.DataFrame,
    features: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    X = df[features].to_numpy(dtype=np.float64)
    y = df["result"].to_numpy(dtype=np.int64)
    if "sample_weight" in df.columns:
        w = df["sample_weight"].to_numpy(dtype=np.float64)
        return X, y, w
    return X, y, None


def fit_base_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    w_train: np.ndarray | None,
) -> XGBClassifier:
    model = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        eval_metric="mlogloss",
        tree_method="hist",
        n_jobs=-1,
    )
    if w_train is not None:
        model.fit(X_train, y_train, sample_weight=w_train)
    else:
        model.fit(X_train, y_train)
    return model


def _top_feature_importances(model: XGBClassifier, features: list[str], top: int = 10) -> list[tuple[str, float]]:
    imp = getattr(model, "feature_importances_", None)
    if imp is None:
        return []
    pairs = list(zip(features, imp.astype(float)))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:top]


def _result_counts(df: pd.DataFrame) -> dict[int, int]:
    if df.empty or "result" not in df.columns:
        return {}
    vc = df["result"].astype(int).value_counts().sort_index()
    return {int(k): int(v) for k, v in vc.items()}


def train_and_calibrate_pipeline(
    df_path: Path | str | None = None,
    model_out: Path | str | None = None,
    report_out: Path | str | None = None,
) -> IsotonicCalibratedClassifier:
    """
    Entrena XGBoost en train (year<=2018, con filas espejo y sample_weight),
    calibra con validación 2019–2022 (sin espejo), evalúa test year>2022 (sin espejo).
    """
    setup_logging()
    set_seed(42)

    df_path = Path(df_path) if df_path else PROCESSED_DIR / "features_dataset.csv"
    model_out = Path(model_out) if model_out else PROJECT_ROOT / "models" / "final_xgboost.pkl"
    report_out = Path(report_out) if report_out else REPORTS_DIR / "training_summary.txt"

    df = load_features(df_path)
    train_df, val_df, test_df = temporal_split(df)
    val_eval = drop_mirror(val_df)
    test_eval = drop_mirror(test_df)

    features = infer_feature_columns(df)
    if not features:
        raise ValueError("No quedaron columnas numéricas de features tras excluir metadatos.")

    if len(val_eval) == 0:
        raise ValueError(
            "No hay filas en validación (2019–2022, sin espejo _m). "
            "Genera `features_dataset.csv` con cobertura temporal suficiente "
            "(ej. pipeline completo sobre international_results)."
        )

    X_train, y_train, w_train = build_xy(train_df, features)
    X_val, y_val, _ = build_xy(val_eval, features)
    X_test, y_test, _ = build_xy(test_eval, features)

    logger.info(
        "Splits - train=%d (con espejo), val=%d/%d (raw/sin espejo), test=%d/%d",
        len(train_df),
        len(val_df),
        len(val_eval),
        len(test_df),
        len(test_eval),
    )

    base_model = fit_base_model(X_train, y_train, w_train)
    calibrated = calibrate_isotonic(base_model, X_val, y_val)

    metrics: dict[str, dict[str, float | int]] = {}
    # Train: conjunto completo (incluye espejo) — sanity
    probs_train = calibrated.predict_proba(X_train)
    metrics.update(evaluate_probabilities("train", y_train, probs_train))
    probs_val = calibrated.predict_proba(X_val)
    metrics.update(evaluate_probabilities("validation", y_val, probs_val))

    if len(test_eval) > 0:
        probs_test = calibrated.predict_proba(X_test)
        metrics.update(evaluate_probabilities("test", y_test, probs_test))
        logger.info(
            "[TEST] Log Loss calibrado: %.4f | Brier multiclase: %.4f | n=%d",
            metrics["test"]["log_loss"],
            metrics["test"]["brier_multiclass"],
            metrics["test"]["n"],
        )
    else:
        logger.warning("Test vacío (sin partidos year>2022 sin espejo); métricas test omitidas.")
        metrics["test"] = {"log_loss": float("nan"), "brier_multiclass": float("nan"), "n": 0}

    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated, model_out)
    logger.info("Modelo guardado en %s", model_out)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "=== Resumen entrenamiento Fase 3 (XGBoost + isotónica) ===",
        f"CSV entrada: {df_path}",
        f"Modelo: {model_out}",
        "",
        "Hiperparámetros XGBClassifier (base):",
        "  objective=multi:softprob, num_class=3, n_estimators=150, max_depth=4,",
        "  learning_rate=0.05, random_state=42, eval_metric=mlogloss, tree_method=hist, n_jobs=-1",
        "",
        "Calibración: IsotonicCalibratedClassifier (OvR isotónico + renorm sobre validación 2019–2022; "
        "equiv. a isotónica sklearn sin re-ajustar el XGB base; sklearn 1.8 sin cv='prefit').",
        "",
        "Features numéricas (orden alfabético):",
        "  " + ", ".join(features),
        "",
        "Conteo filas por split:",
        f"  train (year<=2018, con espejo): {len(train_df)}",
        f"  validation raw (2019–2022): {len(val_df)} | sin espejo: {len(val_eval)}",
        f"  test raw (year>2022): {len(test_df)} | sin espejo: {len(test_eval)}",
        "",
        "Distribución result (train, con espejo): " + str(_result_counts(train_df)),
        "Distribución result (validation, sin espejo): " + str(_result_counts(val_eval)),
        "Distribución result (test, sin espejo): " + str(_result_counts(test_eval)),
        "",
        "Métricas (log_loss con labels=[0,1,2]):",
    ]
    for split in ("train", "validation", "test"):
        m = metrics[split]
        lines.append(
            f"  {split}: n={m['n']} log_loss={m['log_loss']:.6f} "
            f"brier_multiclass={m['brier_multiclass']:.6f}"
            if m["n"] > 0
            else f"  {split}: n=0 (omitido)"
        )

    lines.append("")
    lines.append("Importancia (base XGB, top 10):")
    for name, score in _top_feature_importances(base_model, features):
        lines.append(f"  {name}: {score:.6f}")

    lines.append("")
    lines.append(f"MD5 modelo ({model_out.name}): {_file_md5(model_out)}")
    report_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Reporte escrito en %s", report_out)

    return calibrated


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena y calibra XGBoost multiclase (Fase 3).")
    parser.add_argument(
        "--features-path",
        type=Path,
        default=None,
        help="CSV de features (por defecto data/processed/features_dataset.csv).",
    )
    parser.add_argument("--model-out", type=Path, default=None, help="Ruta del .pkl de salida.")
    parser.add_argument("--report-out", type=Path, default=None, help="Ruta del reporte .txt.")
    args = parser.parse_args()
    train_and_calibrate_pipeline(args.features_path, args.model_out, args.report_out)


if __name__ == "__main__":
    main()
