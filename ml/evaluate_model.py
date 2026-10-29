"""Evaluate the active model on the held-out split."""
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)

from ml.model_loader import load_model
from ml.preprocessing import prepare_data


def evaluate_model():
    pipeline, meta = load_model()
    _, X_test, _, y_test, _, _ = prepare_data()
    X_test = X_test.reindex(columns=meta["features"])
    pred = pipeline.predict(X_test)
    return {
        "accuracy": round(accuracy_score(y_test, pred) * 100, 2),
        "precision": round(precision_score(y_test, pred, zero_division=0) * 100, 2),
        "recall": round(recall_score(y_test, pred, zero_division=0) * 100, 2),
        "f1": round(f1_score(y_test, pred, zero_division=0) * 100, 2),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
        "note": "Evaluated on rows the deployed model has also seen; "
                "use metadata metrics for the unbiased holdout estimate.",
    }


if __name__ == "__main__":
    for key, value in evaluate_model().items():
        print(f"{key}: {value}")
