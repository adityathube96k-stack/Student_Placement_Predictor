"""Helpers shared by route modules."""
from flask import flash, redirect, session, url_for

from models.student import Student


def user_id():
    return session.get("user_id")


def get_student():
    return Student.get_by_user_id(session["user_id"])


def scores_ready(student):
    return Student.has_scores(student)


def need_scores(student):
    """Return a redirect when the profile is missing or has no scores, else None."""
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))
    if not Student.has_scores(student):
        flash("Complete your academic and skill scores in your profile first.", "warning")
        return redirect(url_for("dashboard.profile"))
    return None


def float_field(form, name, low, high, label):
    """Parse a bounded numeric form field; raises ValueError with a friendly message."""
    raw = (form.get(name) or "").strip()
    if raw == "":
        raise ValueError(f"{label} is required.")
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"{label} must be a number.") from None
    if not low <= value <= high:
        raise ValueError(f"{label} must be between {low:g} and {high:g}.")
    return value


def parse_profile(form, current_user_id=None):
    """Validate the shared student-profile form. Returns (user_fields, student_fields)."""
    from database.db import query_one
    from models.user import User
    from utils.helpers import split_skills
    from utils.validators import validate_email, validate_name, validate_phone

    name = form.get("full_name", "").strip()
    email = form.get("email", "").strip().lower()
    if not validate_name(name):
        raise ValueError("Please enter the full name.")
    if not validate_email(email):
        raise ValueError("Please enter a valid email address.")
    existing = User.find_by_email(email)
    if existing and existing["id"] != current_user_id:
        raise ValueError("That email is already used by another account.")
    phone = form.get("phone", "").strip()
    if not validate_phone(phone):
        raise ValueError("Please enter a valid phone number.")
    data = {
        "enrollment_no": form.get("enrollment_no", "").strip() or None,
        "phone": phone or None,
        "branch": form.get("branch", "").strip() or None,
        "year": form.get("year", "").strip() or None,
        "cgpa": float_field(form, "cgpa", 0, 10, "CGPA"),
        "attendance": float_field(form, "attendance", 0, 100, "Attendance"),
        "aptitude_score": float_field(form, "aptitude_score", 0, 100, "Aptitude score"),
        "coding_score": float_field(form, "coding_score", 0, 100, "Coding score"),
        "communication_score": float_field(form, "communication_score", 0, 100, "Communication score"),
        "technical_score": float_field(form, "technical_score", 0, 100, "Technical score"),
        "backlogs": int(float_field(form, "backlogs", 0, 30, "Active backlogs")),
        "projects": int(float_field(form, "projects", 0, 50, "Projects")),
        "internships": int(float_field(form, "internships", 0, 20, "Internships")),
        "certifications": int(float_field(form, "certifications", 0, 50, "Certifications")),
        "skills": ", ".join(split_skills(form.get("skills", ""))) or None,
    }
    if data["enrollment_no"]:
        clash = query_one("SELECT user_id FROM students WHERE enrollment_no = %s", (data["enrollment_no"],))
        if clash and clash["user_id"] != current_user_id:
            raise ValueError("That enrollment number is already registered.")
    return {"full_name": name, "email": email}, data
