"""Train, compare and persist the placement model.

Usage:  python manage.py train        (or)  python -m ml.train_model
"""
import json
import os
from datetime import datetime

import joblib
import numpy as np
import sklearn
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from config import Config
from ml.feature_engineering import FEATURE_LABELS
from ml.preprocessing import RANDOM_STATE, prepare_data

PIPELINE_PATH = os.path.join(Config.MODEL_DIR, "placement_pipeline.joblib")
METADATA_PATH = os.path.join(Config.MODEL_DIR, "model_metadata.json")
LOG_PATH = os.path.join(os.path.dirname(Config.MODEL_DIR), "training_logs", "training.log")


def _candidates():
    return {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=1),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150, max_depth=3, learning_rate=0.08, random_state=RANDOM_STATE),
    }


def _pipeline(model):
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("model", model),
    ])


def train_model(paths=None, activate=True, trained_by=None):
    """Compare candidate algorithms with cross-validation, keep the best.

    Returns the metadata dict (also written to model_metadata.json when activate=True).
    """
    X_train, X_test, y_train, y_test, features, data = prepare_data(paths)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    comparison = []
    for name, estimator in _candidates().items():
        scores = cross_val_score(_pipeline(estimator), X_train, y_train, cv=cv, scoring="f1")
        comparison.append({"algorithm": name, "cv_f1": round(float(scores.mean()) * 100, 2),
                           "cv_std": round(float(scores.std()) * 100, 2)})
    # Parsimony: prefer the simpler model when scores are within 0.5 F1 points.
    top = max(row["cv_f1"] for row in comparison)
    best = next(row for row in comparison if row["cv_f1"] >= top - 0.5)
    estimator = _candidates()[best["algorithm"]]

    pipeline = _pipeline(estimator).fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    importance = permutation_importance(
        pipeline, X_test, y_test, n_repeats=10, random_state=RANDOM_STATE, scoring="f1")
    importances = sorted(
        ({"feature": f, "label": FEATURE_LABELS[f], "importance": round(float(v), 4)}
         for f, v in zip(features, importance.importances_mean)),
        key=lambda item: item["importance"], reverse=True)

    # Deploy a model fitted on all rows; holdout metrics above remain the honest estimate.
    final = _pipeline(_candidates()[best["algorithm"]]).fit(data[features], data["placed"])
    version = datetime.now().strftime("v%Y%m%d-%H%M%S")
    metadata = {
        "version": version,
        "algorithm": best["algorithm"],
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trained_by": trained_by,
        "sklearn_version": sklearn.__version__,
        "features": features,
        "feature_medians": {f: float(np.nanmedian(data[f])) for f in features},
        "rows": int(len(data)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "placed_rate": round(float(data["placed"].mean()) * 100, 2),
        "metrics": {
            "accuracy": round(float(accuracy_score(y_test, predictions)) * 100, 2),
            "precision": round(float(precision_score(y_test, predictions, zero_division=0)) * 100, 2),
            "recall": round(float(recall_score(y_test, predictions, zero_division=0)) * 100, 2),
            "f1": round(float(f1_score(y_test, predictions, zero_division=0)) * 100, 2),
            "roc_auc": round(float(roc_auc_score(y_test, probabilities)) * 100, 2),
        },
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "comparison": comparison,
        "importances": importances,
    }
    if activate:
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        joblib.dump(final, PIPELINE_PATH)
        with open(METADATA_PATH, "w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2)
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"{metadata['trained_at']} {version} {best['algorithm']} "
                      f"rows={len(data)} acc={metadata['metrics']['accuracy']} "
                      f"f1={metadata['metrics']['f1']}\n")
        from ml import model_loader
        model_loader._cache["pipeline"] = None  # force reload on next prediction
    return metadata


if __name__ == "__main__":
    info = train_model()
    print(f"Trained {info['algorithm']} ({info['version']}) on {info['rows']} rows")
    for key, value in info["metrics"].items():
        print(f"  {key:<10} {value}%")
