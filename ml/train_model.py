# ==========================================================
# STUDENT PLACEMENT PREDICTOR
# ML MODEL TRAINING
# ==========================================================

import os
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
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

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "placement_model.pkl"
)


# ==========================================================
# TRAIN MODEL
# ==========================================================

def train_model():

    print(
        "=========================================="
    )

    print(
        "STARTING PLACEMENT MODEL TRAINING"
    )

    print(
        "=========================================="
    )


    # ------------------------------------------------------
    # Prepare data
    # ------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = prepare_data()


    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )


    # ------------------------------------------------------
    # Create Logistic Regression model
    # ------------------------------------------------------

    model = LogisticRegression(
        max_iter=1000,
        random_state=42
    )


    # ------------------------------------------------------
    # Train model
    # ------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )


    print(
        "Model training completed."
    )


    # ------------------------------------------------------
    # Make predictions
    # ------------------------------------------------------

    y_pred = model.predict(
        X_test
    )


    # ------------------------------------------------------
    # Calculate accuracy
    # ------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )


    print(
        f"Model Accuracy: {accuracy * 100:.2f}%"
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


    # ------------------------------------------------------
    # Create model directory
    # ------------------------------------------------------

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )


    # ------------------------------------------------------
    # Save trained model
    # ------------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH
    )


    print(
        "=========================================="
    )

    print(
        "MODEL SAVED SUCCESSFULLY"
    )

    print(
        f"Model path: {MODEL_PATH}"
    )

    print(
        "=========================================="
    )


    return model, accuracy


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    try:

        train_model()

    except Exception as error:

        print(
            "Model Training Error:",
            error
        )