"""Dataset loading and train/test preparation."""
import os

import pandas as pd
from sklearn.model_selection import train_test_split

from config import Config
from ml.feature_engineering import TARGET_COLUMN, clean_dataframe, select_features

BASE_DATASET = os.path.join(Config.DATASET_DIR, "placement_dataset.csv")
FEATURE_COLUMNS = None  # determined per dataset; see select_features()
TEST_SIZE = 0.20
RANDOM_STATE = 42


def load_datasets(paths=None):
    """Load and merge one or more CSV files. Missing optional columns become NaN
    (median-imputed inside the model pipeline)."""
    paths = paths or [BASE_DATASET]
    frames = []
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found: {path}")
        frames.append(pd.read_csv(path))
    merged = pd.concat(frames, ignore_index=True, sort=False)
    data = clean_dataframe(merged)
    if data.empty:
        raise ValueError("Dataset has no valid rows.")
    if data[TARGET_COLUMN].nunique() < 2:
        raise ValueError("Dataset must contain both placed (1) and not placed (0) rows.")
    if len(data) < 30:
        raise ValueError("Dataset needs at least 30 valid rows to train a model.")
    return data


def prepare_data(paths=None):
    data = load_datasets(paths)
    features = select_features(data)
    X, y = data[features], data[TARGET_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)
    return X_train, X_test, y_train, y_test, features, data


def validate_upload(path):
    """Validate an uploaded CSV. Returns summary dict or raises ValueError."""
    frame = pd.read_csv(path)
    original_rows = len(frame)
    data = clean_dataframe(frame)
    if len(data) == 0:
        raise ValueError("No valid rows found. Check numeric values and that 'placed' is 0 or 1.")
    return {
        "rows": int(len(data)),
        "dropped": int(original_rows - len(data)),
        "placed": int(data[TARGET_COLUMN].sum()),
        "features": select_features(data),
    }
