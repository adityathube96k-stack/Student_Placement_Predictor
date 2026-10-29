"""Placement prediction with per-feature explanations."""
import pandas as pd

from ml.feature_engineering import FEATURE_LABELS, validate_inputs
from ml.model_loader import load_model


def predict_placement(cgpa, attendance, aptitude_score, coding_score,
                      communication_score, technical_score,
                      projects=None, internships=None, certifications=None):
    values = validate_inputs({
        "cgpa": cgpa, "attendance": attendance, "aptitude_score": aptitude_score,
        "coding_score": coding_score, "communication_score": communication_score,
        "technical_score": technical_score, "projects": projects,
        "internships": internships, "certifications": certifications,
    })
    pipeline, meta = load_model()
    features = meta["features"]
    # One batched call: row 0 is the student; the rest swap a single feature for the
    # median (typical) value. The probability change is that feature's contribution.
    used = [f for f in features if f in values]
    rows = [[values.get(f) for f in features]]
    for feature in used:
        row = [values.get(f) for f in features]
        row[features.index(feature)] = meta["feature_medians"][feature]
        rows.append(row)
    probs = pipeline.predict_proba(pd.DataFrame(rows, columns=features, dtype=float))[:, 1]
    probability = float(probs[0])
    factors = [{"feature": f, "label": FEATURE_LABELS[f],
                "impact": round((probability - float(probs[i + 1])) * 100, 1)}
               for i, f in enumerate(used)]
    factors.sort(key=lambda item: abs(item["impact"]), reverse=True)

    placed = probability >= 0.5
    placement = round(probability * 100, 2)
    if placement >= 75:
        band = "High"
    elif placement >= 50:
        band = "Moderate"
    else:
        band = "Low"
    return {
        "prediction": int(placed),
        "result": "Placed" if placed else "Not Placed",
        "placement_probability": placement,
        "not_placed_probability": round(100 - placement, 2),
        "confidence": round(max(placement, 100 - placement), 2),
        "band": band,
        "model_version": meta["version"],
        "factors": factors,
        "strengths": [f for f in factors if f["impact"] > 0.5][:3],
        "risks": [f for f in factors if f["impact"] < -0.5][:3][::-1] or [],
    }
