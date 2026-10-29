"""Feature definitions and input validation shared by training and prediction."""
import pandas as pd

CORE_FEATURES = [
    "cgpa", "attendance", "aptitude_score", "coding_score",
    "communication_score", "technical_score",
]
OPTIONAL_FEATURES = ["projects", "internships", "certifications"]
ALL_FEATURES = CORE_FEATURES + OPTIONAL_FEATURES
TARGET_COLUMN = "placed"

FEATURE_LABELS = {
    "cgpa": "CGPA", "attendance": "Attendance", "aptitude_score": "Aptitude",
    "coding_score": "Coding", "communication_score": "Communication",
    "technical_score": "Technical", "projects": "Projects",
    "internships": "Internships", "certifications": "Certifications",
}
RANGES = {
    "cgpa": (0, 10), "attendance": (0, 100), "aptitude_score": (0, 100),
    "coding_score": (0, 100), "communication_score": (0, 100),
    "technical_score": (0, 100), "projects": (0, 50),
    "internships": (0, 20), "certifications": (0, 50),
}


def select_features(frame):
    """Core features plus any optional ones present in the dataset."""
    return CORE_FEATURES + [c for c in OPTIONAL_FEATURES if c in frame.columns]


def clean_dataframe(frame):
    """Coerce to numeric, drop unusable rows, clip to valid ranges, de-duplicate."""
    missing = [c for c in CORE_FEATURES + [TARGET_COLUMN] if c not in frame.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    data = frame[[c for c in ALL_FEATURES + [TARGET_COLUMN] if c in frame.columns]].copy()
    data = data.apply(pd.to_numeric, errors="coerce")
    data = data.dropna(subset=CORE_FEATURES + [TARGET_COLUMN])
    data = data[data[TARGET_COLUMN].isin([0, 1])]
    for column, (low, high) in RANGES.items():
        if column in data.columns:
            data[column] = data[column].clip(low, high)
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)
    return data.drop_duplicates().reset_index(drop=True)


def validate_inputs(inputs):
    """Return floats for the given inputs or raise ValueError with a clear message."""
    values = {}
    for name in ALL_FEATURES:
        raw = inputs.get(name)
        if raw in (None, ""):
            if name in CORE_FEATURES:
                raise ValueError(f"{FEATURE_LABELS[name]} is required.")
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{FEATURE_LABELS[name]} must be a number.") from None
        low, high = RANGES[name]
        if not low <= value <= high:
            raise ValueError(f"{FEATURE_LABELS[name]} must be between {low} and {high}.")
        values[name] = value
    return values


def build_frame(values, features):
    """One-row DataFrame in the exact column order the model was trained on."""
    return pd.DataFrame([[values.get(f) for f in features]], columns=features, dtype=float)
