"""Thread-safe model loading with automatic recovery.

If the saved model is missing or was pickled by an incompatible scikit-learn
version, it is retrained from the bundled dataset instead of crashing the app.
"""
import json
import os
import threading

import joblib

from config import Config

PIPELINE_PATH = os.path.join(Config.MODEL_DIR, "placement_pipeline.joblib")
METADATA_PATH = os.path.join(Config.MODEL_DIR, "model_metadata.json")

_lock = threading.RLock()
_cache = {"pipeline": None, "metadata": None}


def _read_metadata():
    with open(METADATA_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def load_model(force=False):
    """Return (pipeline, metadata), training a model first if necessary."""
    with _lock:
        if _cache["pipeline"] is not None and not force:
            return _cache["pipeline"], _cache["metadata"]
        try:
            pipeline = joblib.load(PIPELINE_PATH)
            metadata = _read_metadata()
        except Exception:  # missing file, version mismatch, corrupt pickle
            from ml.train_model import train_model

            metadata = train_model(activate=True)
            pipeline = joblib.load(PIPELINE_PATH)
        _cache["pipeline"], _cache["metadata"] = pipeline, metadata
        return pipeline, metadata


def reload_model():
    return load_model(force=True)


def get_metadata():
    return load_model()[1]
