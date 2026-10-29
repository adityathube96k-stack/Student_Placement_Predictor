import json
import os
import uuid

from flask import (Blueprint, current_app, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename

from models.resume import Resume
from models.student import Student
from resume_analyzer.parser import analyze_resume
from routes._common import get_student, user_id
from utils.decorators import student_required
from utils.helpers import parse_json, split_skills
from utils.logger import log

resume_bp = Blueprint("resume", __name__, url_prefix="/student")


def _is_pdf(path):
    with open(path, "rb") as handle:
        return handle.read(5) == b"%PDF-"


@resume_bp.route("/resume", methods=["GET", "POST"])
@student_required
def resume_upload():
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or not file.filename:
            flash("Choose a PDF resume to upload.", "danger")
            return redirect(url_for("resume.resume_upload"))
        original = secure_filename(file.filename) or "resume.pdf"
        if not original.lower().endswith(".pdf"):
            flash("Only PDF files are supported.", "danger")
            return redirect(url_for("resume.resume_upload"))
        stored = f"u{user_id()}_{uuid.uuid4().hex}.pdf"
        path = os.path.join(current_app.config["RESUME_UPLOAD_DIR"], stored)
        file.save(path)
        try:
            if not _is_pdf(path):
                raise ValueError("That file is not a valid PDF.")
            result = analyze_resume(path)
        except Exception as error:  # noqa: BLE001
            os.remove(path)
            log.warning("Resume analysis failed: %s", error)
            flash(str(error) if isinstance(error, ValueError) else "We could not analyse that PDF.", "danger")
            return redirect(url_for("resume.resume_upload"))
        analysis_id = Resume.save(user_id(), original, stored, os.path.getsize(path), result)
        flash("Resume analysed.", "success")
        return redirect(url_for("resume.resume_result", analysis_id=analysis_id))
    return render_template("student/resume_upload.html", latest=Resume.latest(user_id()),
                           history=Resume.history(user_id())[:5])


@resume_bp.route("/resume/<int:analysis_id>")
@student_required
def resume_result(analysis_id):
    row = Resume.get(user_id(), analysis_id)
    if not row:
        flash("Analysis not found.", "danger")
        return redirect(url_for("resume.resume_upload"))
    student = get_student()
    skills = parse_json(row["skills_json"], {})
    detected = sorted({s for group in skills.values() for s in group}) if isinstance(skills, dict) else []
    known = {s.lower() for s in split_skills(student.get("skills"))}
    return render_template(
        "student/resume_result.html", row=row, skills=skills, detected=detected,
        sections=parse_json(row.get("sections_json"), {}),
        recommendations=parse_json(row["recommendations_json"], []),
        new_skills=[s for s in detected if s.lower() not in known])


@resume_bp.route("/resume/<int:analysis_id>/sync-skills", methods=["POST"])
@student_required
def sync_skills(analysis_id):
    row = Resume.get(user_id(), analysis_id)
    if not row:
        return redirect(url_for("resume.resume_upload"))
    skills = parse_json(row["skills_json"], {})
    detected = [s for group in skills.values() for s in group]
    student = get_student()
    merged = split_skills(", ".join(split_skills(student.get("skills")) + detected))
    Student.update_profile(user_id(), {"skills": ", ".join(merged)})
    flash(f"Added resume skills to your profile ({len(merged)} total).", "success")
    return redirect(url_for("resume.resume_result", analysis_id=analysis_id))


@resume_bp.route("/resume/<int:analysis_id>/file")
@student_required
def resume_file(analysis_id):
    row = Resume.get(user_id(), analysis_id)
    if not row:
        return redirect(url_for("resume.resume_upload"))
    return send_from_directory(current_app.config["RESUME_UPLOAD_DIR"], row["stored_filename"],
                               download_name=row["original_filename"], mimetype="application/pdf")


@resume_bp.route("/resume-history")
@student_required
def resume_history():
    return render_template("student/resume_history.html", history=Resume.history(user_id()))
