"""Institute-wide placement analytics (used by Admin and TPO)."""
from collections import Counter, defaultdict

from database.db import query_all, query_one, scalar
from utils.helpers import percent
from utils.readiness import calculate_readiness_score

SCORE_COLUMNS = [("cgpa", "CGPA"), ("attendance", "Attendance"), ("aptitude_score", "Aptitude"),
                 ("coding_score", "Coding"), ("communication_score", "Communication"),
                 ("technical_score", "Technical")]


def _students():
    return query_all("SELECT s.*, u.full_name FROM students s JOIN users u ON u.id = s.user_id "
                     "WHERE u.is_active = 1")


def _complete(student):
    return all(student.get(k) is not None for k, _ in SCORE_COLUMNS)


def score_averages():
    rows = [s for s in _students() if _complete(s)]
    if not rows:
        return {label: 0 for _, label in SCORE_COLUMNS}
    return {label: round(sum(s[k] for s in rows) / len(rows), 1) for k, label in SCORE_COLUMNS}


def branch_breakdown():
    groups = defaultdict(list)
    for s in _students():
        groups[s.get("branch") or "Unspecified"].append(s)
    out = []
    for branch, rows in groups.items():
        cgpas = [s["cgpa"] for s in rows if s["cgpa"] is not None]
        placed = sum(1 for s in rows if s["placement_status"] == "Placed")
        out.append({"branch": branch, "students": len(rows), "placed": placed,
                    "avg_cgpa": round(sum(cgpas) / len(cgpas), 2) if cgpas else 0,
                    "placement_rate": percent(placed, len(rows))})
    return sorted(out, key=lambda r: -r["students"])


def readiness_distribution():
    counts = Counter({"Excellent": 0, "Good": 0, "Moderate": 0, "Needs Improvement": 0})
    for s in _students():
        if _complete(s):
            counts[calculate_readiness_score(
                s["cgpa"], s["attendance"], s["aptitude_score"], s["coding_score"],
                s["communication_score"], s["technical_score"])["readiness_level"]] += 1
    return dict(counts)


def cgpa_histogram():
    bins = [("< 6", 0, 6), ("6 - 7", 6, 7), ("7 - 8", 7, 8), ("8 - 9", 8, 9), ("9 +", 9, 10.01)]
    values = [s["cgpa"] for s in _students() if s["cgpa"] is not None]
    return [{"label": label, "count": sum(1 for v in values if lo <= v < hi)} for label, lo, hi in bins]


def placed_vs_not_scores():
    """Average scores of placed vs not-yet-placed students (for radar comparison)."""
    placed = [s for s in _students() if _complete(s) and s["placement_status"] == "Placed"]
    others = [s for s in _students() if _complete(s) and s["placement_status"] != "Placed"]

    def avg(rows, key):
        return round(sum(r[key] for r in rows) / len(rows), 1) if rows else 0
    skills = [("aptitude_score", "Aptitude"), ("coding_score", "Coding"),
              ("communication_score", "Communication"), ("technical_score", "Technical"),
              ("attendance", "Attendance")]
    return {"labels": [l for _, l in skills],
            "placed": [avg(placed, k) for k, _ in skills],
            "others": [avg(others, k) for k, _ in skills]}


def prediction_summary():
    """Latest prediction per student."""
    rows = query_all(
        "SELECT p.user_id, p.prediction, p.placement_probability FROM prediction_history p "
        "WHERE p.id = (SELECT MAX(id) FROM prediction_history WHERE user_id = p.user_id)")
    placed = sum(1 for r in rows if r["prediction"] == "Placed")
    avg_prob = round(sum(r["placement_probability"] or 0 for r in rows) / len(rows), 1) if rows else 0
    return {"students": len(rows), "placed": placed, "not_placed": len(rows) - placed,
            "avg_probability": avg_prob, "placed_rate": percent(placed, len(rows))}


def placement_outcomes():
    placed = query_all("SELECT placed_company, package_lpa FROM students WHERE placement_status = 'Placed'")
    pk = [p["package_lpa"] for p in placed if p["package_lpa"]]
    by_company = Counter(p["placed_company"] or "Other" for p in placed)
    total = scalar("SELECT COUNT(*) FROM students")
    return {"placed": len(placed), "total": total, "rate": percent(len(placed), total),
            "avg_package": round(sum(pk) / len(pk), 2) if pk else 0,
            "highest_package": max(pk) if pk else 0,
            "by_company": [{"company": k, "count": v} for k, v in by_company.most_common(8)]}


def monthly_activity(months=6):
    """Registrations and predictions per month for the last N months."""
    from datetime import datetime
    now = datetime.now()
    keys = []
    year, month = now.year, now.month
    for _ in range(months):
        keys.append((year, month))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    keys.reverse()
    users = Counter((u["created_at"].year, u["created_at"].month) for u in
                    query_all("SELECT created_at FROM users WHERE role = 'student'") if u["created_at"])
    preds = Counter((p["created_at"].year, p["created_at"].month) for p in
                    query_all("SELECT created_at FROM prediction_history") if p["created_at"])
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return {"labels": [names[m - 1] for _, m in keys],
            "registrations": [users.get(k, 0) for k in keys],
            "predictions": [preds.get(k, 0) for k in keys]}


def status_breakdown():
    rows = query_all("SELECT placement_status AS status, COUNT(*) AS n FROM students GROUP BY placement_status")
    return {r["status"]: int(r["n"]) for r in rows}
