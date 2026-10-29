"""Per-student progress analytics."""
from database.db import query_all
from utils.constants import SKILL_TARGETS


def progress_timeline(user_id):
    def series(sql, key):
        rows = list(reversed(query_all(sql, (user_id,))))
        return [{"date": r["created_at"].strftime("%d %b") if r["created_at"] else "",
                 "value": float(r[key] or 0)} for r in rows]
    return {
        "predictions": series("SELECT created_at, placement_probability FROM prediction_history "
                              "WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT 12",
                              "placement_probability"),
        "readiness": series("SELECT created_at, readiness_score FROM readiness_history "
                            "WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT 12",
                            "readiness_score"),
        "interviews": series("SELECT created_at, interview_score FROM interview_history "
                             "WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT 12",
                             "interview_score"),
    }


def skill_radar(student):
    if not student:
        return {"labels": [], "current": [], "target": []}
    keys = {"Aptitude": "aptitude_score", "Coding": "coding_score",
            "Communication": "communication_score", "Technical": "technical_score"}
    return {"labels": list(keys),
            "current": [float(student.get(k) or 0) for k in keys.values()],
            "target": [SKILL_TARGETS[name] for name in keys]}


def improvement(series):
    """Change between first and latest value of a timeline series."""
    values = [p["value"] for p in series]
    if len(values) < 2:
        return None
    return round(values[-1] - values[0], 1)
