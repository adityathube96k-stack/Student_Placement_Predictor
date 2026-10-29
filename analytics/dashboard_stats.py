"""Headline numbers for each role's dashboard."""
import json

from analytics import placement_analytics as pa
from database.db import query_all, query_one, scalar
from ml.model_loader import get_metadata
from models.student import Student
from utils.readiness import calculate_readiness_score


def admin_overview():
    meta = get_metadata()
    return {
        "users": scalar("SELECT COUNT(*) FROM users"),
        "students": scalar("SELECT COUNT(*) FROM students"),
        "complete_profiles": sum(1 for s in query_all("SELECT * FROM students") if Student.completeness(s) == 100),
        "companies": scalar("SELECT COUNT(*) FROM companies WHERE is_active = 1"),
        "open_drives": scalar("SELECT COUNT(*) FROM drives WHERE status IN ('Upcoming','Active')"),
        "predictions": scalar("SELECT COUNT(*) FROM prediction_history"),
        "interviews": scalar("SELECT COUNT(*) FROM interview_history"),
        "resumes": scalar("SELECT COUNT(*) FROM resume_analysis"),
        "model": meta,
        "recent_users": query_all("SELECT id, full_name, email, role, created_at FROM users "
                                  "ORDER BY id DESC LIMIT 6"),
    }


def tpo_overview():
    outcomes = pa.placement_outcomes()
    return {
        "outcomes": outcomes,
        "predictions": pa.prediction_summary(),
        "open_drives": scalar("SELECT COUNT(*) FROM drives WHERE status IN ('Upcoming','Active')"),
        "pending_applications": scalar("SELECT COUNT(*) FROM drive_applications WHERE status = 'Applied'"),
        "upcoming": query_all(
            "SELECT d.id, d.job_role, d.drive_date, d.openings, d.status, c.name AS company_name "
            "FROM drives d JOIN companies c ON c.id = d.company_id "
            "WHERE d.status IN ('Upcoming','Active') ORDER BY d.drive_date ASC LIMIT 5"),
    }


def student_overview(user_id, student):
    pred = query_one("SELECT * FROM prediction_history WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    ready = None
    if Student.has_scores(student):
        ready = calculate_readiness_score(
            student["cgpa"], student["attendance"], student["aptitude_score"],
            student["coding_score"], student["communication_score"], student["technical_score"])
    interview = query_one("SELECT * FROM interview_history WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    resume = query_one("SELECT overall_score, rating FROM resume_analysis WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    apps = query_all("SELECT status FROM drive_applications WHERE user_id = %s", (user_id,))
    return {"prediction": pred, "readiness": ready, "interview": interview, "resume": resume,
            "completeness": Student.completeness(student), "applications": len(apps),
            "shortlisted": sum(1 for a in apps if a["status"] in ("Shortlisted", "Selected"))}
