# ==========================================================
# STUDENT PLACEMENT PREDICTOR
# ML DATA PREPROCESSING
# ==========================================================

import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "placement_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "models"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "scaler.pkl"
)


# ==========================================================
# FEATURES
# ==========================================================

FEATURE_COLUMNS = [
    "cgpa",
    "attendance",
    "aptitude_score",
    "coding_score",
    "communication_score",
    "technical_score"
]

TARGET_COLUMN = "placed"


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset():

    if not os.path.exists(DATASET_PATH):

        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    data = pd.read_csv(
        DATASET_PATH
    )

    return data


# ==========================================================
# VALIDATE DATASET
# ==========================================================

def validate_dataset(data):

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing columns: "
            + ", ".join(missing_columns)
        )

    if data.empty:

        raise ValueError(
            "Placement dataset is empty."
        )

    return True


# ==========================================================
# PREPARE DATA
# ==========================================================

def prepare_data():

    # Load dataset
    data = load_dataset()

    # Validate dataset
    validate_dataset(data)

    # Select features
    X = data[
        FEATURE_COLUMNS
    ].copy()

    # Select target
    y = data[
        TARGET_COLUMN
    ].copy()

    # Convert values to numeric
    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    y = pd.to_numeric(
        y,
        errors="coerce"
    )

    # Remove invalid rows
    valid_rows = (
        X.notna().all(axis=1)
        & y.notna()
    )

    X = X.loc[
        valid_rows
    ]

    y = y.loc[
        valid_rows
    ]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # Create scaler
    scaler = StandardScaler()

    # Fit only on training data
    X_train_scaled = scaler.fit_transform(
        X_train
    )

    # Transform test data
    X_test_scaled = scaler.transform(
        X_test
    )

    # Create model directory
    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    # Save scaler
    joblib.dump(
        scaler,
        SCALER_PATH
    )

    return (
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test
    )


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    try:

        (
            X_train,
            X_test,
            y_train,
            y_test
        ) = prepare_data()

        print(
            "=========================================="
        )

        print(
            "ML PREPROCESSING SUCCESSFUL"
        )

        print(
            "=========================================="
        )

        print(
            f"Training samples: {len(X_train)}"
        )

        print(
            f"Testing samples: {len(X_test)}"
        )

        print(
            f"Training features: {X_train.shape[1]}"
        )

        print(
            f"Scaler saved at: {SCALER_PATH}"
        )

        print(
            "=========================================="
        )

    except Exception as error:

        print(
            "Preprocessing Error:",
            error
        )