# ==========================================================
# STUDENT PLACEMENT PREDICTOR
# ML MODEL EVALUATION
# ==========================================================

import os
import joblib

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from preprocessing import prepare_data


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "models",
    "placement_model.pkl"
)


# ==========================================================
# EVALUATE MODEL
# ==========================================================

def evaluate_model():

    print(
        "=========================================="
    )

    print(
        "PLACEMENT MODEL EVALUATION"
    )

    print(
        "=========================================="
    )


    # ------------------------------------------------------
    # Check model
    # ------------------------------------------------------

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            "Trained model not found. "
            "Run train_model.py first."
        )


    # ------------------------------------------------------
    # Prepare test data
    # ------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = prepare_data()


    # ------------------------------------------------------
    # Load model
    # ------------------------------------------------------

    model = joblib.load(
        MODEL_PATH
    )


    # ------------------------------------------------------
    # Make predictions
    # ------------------------------------------------------

    y_pred = model.predict(
        X_test
    )


    # ------------------------------------------------------
    # Calculate metrics
    # ------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )


    # ------------------------------------------------------
    # Display metrics
    # ------------------------------------------------------

    print(
        f"Accuracy  : {accuracy * 100:.2f}%"
    )

    print(
        f"Precision : {precision * 100:.2f}%"
    )

    print(
        f"Recall    : {recall * 100:.2f}%"
    )

    print(
        f"F1 Score  : {f1 * 100:.2f}%"
    )


    # ------------------------------------------------------
    # Classification report
    # ------------------------------------------------------

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )


    # ------------------------------------------------------
    # Confusion matrix
    # ------------------------------------------------------

    print(
        "Confusion Matrix:"
    )

    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )


    print(
        "=========================================="
    )

    print(
        "MODEL EVALUATION COMPLETED"
    )

    print(
        "=========================================="
    )


    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    try:

        evaluate_model()

    except Exception as error:

        print(
            "Evaluation Error:",
            error
        )