import os
import uuid

from flask import (Blueprint, current_app, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.utils import secure_filename

from analytics import company_analytics as ca
from analytics import placement_analytics as pa
from analytics.dashboard_stats import admin_overview
from database.db import execute, execute_count, query_all, query_one
from ml.model_loader import get_metadata
from ml.preprocessing import BASE_DATASET, validate_upload
from ml.train_model import train_model
from models.company import Company
from models.report import Report
from models.student import Student
from models.user import User
from notifications.service import notify_many
from routes._common import float_field, parse_profile, user_id
from utils.constants import BRANCHES, SKILL_SUGGESTIONS, YEARS
from utils.decorators import admin_required
from utils.helpers import split_skills
from utils.logger import log

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    return render_template(
        "admin/admin_dashboard.html", overview=admin_overview(), averages=pa.score_averages(),
        branches=pa.branch_breakdown(), readiness=pa.readiness_distribution(),
        activity=pa.monthly_activity(), outcomes=pa.placement_outcomes())


# --- Students -----------------------------------------------------------------

@admin_bp.route("/students")
@admin_required
def manage_students():
    search = request.args.get("q", "").strip()
    branch = request.args.get("branch", "")
    status = request.args.get("status", "")
    students = Student.all(search, branch, status)
    for s in students:
        s["completeness"] = Student.completeness(s)
    return render_template("admin/manage_students.html", students=students, branches=BRANCHES,
                           filters={"q": search, "branch": branch, "status": status})


@admin_bp.route("/students/new", methods=["GET", "POST"])
@admin_required
def student_new():
    if request.method == "POST":
        try:
            user_fields, data = parse_profile(request.form)
            password = request.form.get("password", "")
            from utils.validators import password_problem
            if password_problem(password):
                raise ValueError(password_problem(password))
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("admin/student_form.html", student=request.form, mode="new", branches=BRANCHES,
                                   years=YEARS, suggestions=SKILL_SUGGESTIONS), 400
        uid = User.create(user_fields["full_name"], user_fields["email"], password)
        Student.create_profile(uid)
        Student.update_profile(uid, data)
        flash(f"Student {user_fields['full_name']} created.", "success")
        return redirect(url_for("admin.manage_students"))
    return render_template("admin/student_form.html", student={}, mode="new", branches=BRANCHES,
                           years=YEARS, suggestions=SKILL_SUGGESTIONS)


@admin_bp.route("/students/<int:uid>/edit", methods=["GET", "POST"])
@admin_required
def student_edit(uid):
    student = Student.get_by_user_id(uid)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.manage_students"))
    if request.method == "POST":
        try:
            user_fields, data = parse_profile(request.form, uid)
            status = request.form.get("placement_status", "Not Placed")
            if status not in ("Not Placed", "In Process", "Placed"):
                raise ValueError("Invalid placement status.")
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("admin/student_form.html", student=dict(student, **request.form.to_dict()),
                                   mode="edit", branches=BRANCHES, years=YEARS, suggestions=SKILL_SUGGESTIONS), 400
        User.update_name_email(uid, user_fields["full_name"], user_fields["email"])
        Student.update_profile(uid, data)
        company = request.form.get("placed_company", "").strip() or None
        package = request.form.get("package_lpa", "").strip()
        Student.set_placement(uid, status, company if status == "Placed" else None,
                              float(package) if package and status == "Placed" else None)
        flash("Student updated.", "success")
        return redirect(url_for("admin.manage_students"))
    return render_template("admin/student_form.html", student=student, mode="edit", branches=BRANCHES,
                           years=YEARS, suggestions=SKILL_SUGGESTIONS)


@admin_bp.route("/students/<int:uid>/toggle", methods=["POST"])
@admin_required
def student_toggle(uid):
    user = User.find_by_id(uid)
    if user and user["role"] == "student":
        User.set_active(uid, not user["is_active"])
        flash(f"{user['full_name']} {'deactivated' if user['is_active'] else 'reactivated'}.", "success")
    return redirect(url_for("admin.manage_students"))


@admin_bp.route("/students/<int:uid>/delete", methods=["POST"])
@admin_required
def student_delete(uid):
    user = User.find_by_id(uid)
    if user and user["role"] == "student":
        execute("DELETE FROM users WHERE id = %s", (uid,))
        flash(f"{user['full_name']} and all their records were deleted.", "success")
    return redirect(url_for("admin.manage_students"))


# --- Companies ----------------------------------------------------------------

def _company_form(form):
    name = form.get("name", "").strip()
    if len(name) < 2:
        raise ValueError("Company name is required.")
    return {
        "name": name, "industry": form.get("industry", "").strip() or None,
        "location": form.get("location", "").strip() or None,
        "website": form.get("website", "").strip() or None,
        "description": form.get("description", "").strip() or None,
        "min_cgpa": float_field(form, "min_cgpa", 0, 10, "Minimum CGPA"),
        "min_attendance": float_field(form, "min_attendance", 0, 100, "Minimum attendance"),
        "min_aptitude": float_field(form, "min_aptitude", 0, 100, "Minimum aptitude"),
        "min_coding": float_field(form, "min_coding", 0, 100, "Minimum coding"),
        "min_communication": float_field(form, "min_communication", 0, 100, "Minimum communication"),
        "min_technical": float_field(form, "min_technical", 0, 100, "Minimum technical"),
        "max_backlogs": int(float_field(form, "max_backlogs", 0, 30, "Maximum backlogs")),
        "required_skills": ", ".join(split_skills(form.get("required_skills", ""))) or None,
        "package_lpa": float_field(form, "package_lpa", 0, 500, "Package"),
        "is_active": 1 if form.get("is_active", "1") == "1" else 0,
    }


@admin_bp.route("/companies")
@admin_required
def manage_companies():
    rows = Company.all()
    matrix = {m["company_id"]: m["eligible"] for m in ca.eligibility_matrix()}
    for c in rows:
        c["eligible_students"] = matrix.get(c["id"], 0)
        c["skills_list"] = split_skills(c.get("required_skills"))
    return render_template("admin/manage_companies.html", companies=rows)


@admin_bp.route("/companies/new", methods=["GET", "POST"])
@admin_required
def company_new():
    if request.method == "POST":
        try:
            data = _company_form(request.form)
            if Company.name_exists(data["name"]):
                raise ValueError("A company with that name already exists.")
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("admin/company_form.html", company=request.form, mode="new",
                                   suggestions=SKILL_SUGGESTIONS), 400
        Company.create(data)
        flash(f"{data['name']} added.", "success")
        return redirect(url_for("admin.manage_companies"))
    return render_template("admin/company_form.html", mode="new", suggestions=SKILL_SUGGESTIONS, company={
        "min_cgpa": 6.5, "min_attendance": 70, "min_aptitude": 55, "min_coding": 55, "min_communication": 55,
        "min_technical": 55, "max_backlogs": 0, "package_lpa": 4, "is_active": 1})


@admin_bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
@admin_required
def company_edit(company_id):
    company = Company.get(company_id)
    if not company:
        flash("Company not found.", "danger")
        return redirect(url_for("admin.manage_companies"))
    if request.method == "POST":
        try:
            data = _company_form(request.form)
            if Company.name_exists(data["name"], company_id):
                raise ValueError("A company with that name already exists.")
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("admin/company_form.html", company=dict(company, **request.form.to_dict()),
                                   mode="edit", suggestions=SKILL_SUGGESTIONS), 400
        Company.update(company_id, data)
        flash("Company updated.", "success")
        return redirect(url_for("admin.manage_companies"))
    return render_template("admin/company_form.html", company=company, mode="edit", suggestions=SKILL_SUGGESTIONS)


@admin_bp.route("/companies/<int:company_id>/toggle", methods=["POST"])
@admin_required
def company_toggle(company_id):
    company = Company.get(company_id)
    if company:
        Company.update(company_id, {"is_active": 0 if company["is_active"] else 1})
        flash(f"{company['name']} {'paused' if company['is_active'] else 'activated'}.", "success")
    return redirect(url_for("admin.manage_companies"))


@admin_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
@admin_required
def company_delete(company_id):
    company = Company.get(company_id)
    if company:
        Company.delete(company_id)
        flash(f"{company['name']} and its drives were removed.", "success")
    return redirect(url_for("admin.manage_companies"))


# --- Datasets and model training -------------------------------------------------

def _active_dataset_paths(include_base=True):
    paths = [BASE_DATASET] if include_base else []
    for row in query_all("SELECT filename FROM datasets WHERE use_for_training = 1 AND filename != 'placement_dataset.csv'"):
        path = os.path.join(current_app.config["DATASET_UPLOAD_DIR"], row["filename"])
        if os.path.exists(path):
            paths.append(path)
    return paths


@admin_bp.route("/upload-dataset", methods=["GET", "POST"])
@admin_required
def upload_dataset():
    if request.method == "POST":
        file = request.files.get("dataset")
        if not file or not file.filename:
            flash("Choose a CSV file to upload.", "danger")
            return redirect(url_for("admin.upload_dataset"))
        original = secure_filename(file.filename)
        if not original.lower().endswith(".csv"):
            flash("Only CSV files are supported.", "danger")
            return redirect(url_for("admin.upload_dataset"))
        stored = f"{uuid.uuid4().hex[:12]}_{original}"
        path = os.path.join(current_app.config["DATASET_UPLOAD_DIR"], stored)
        file.save(path)
        try:
            summary = validate_upload(path)
        except Exception as error:  # noqa: BLE001
            os.remove(path)
            flash(f"Dataset rejected: {error}", "danger")
            return redirect(url_for("admin.upload_dataset"))
        execute("INSERT INTO datasets (filename, original_name, rows_count, placed_count, extra_features, "
                "uploaded_by, use_for_training) VALUES (%s,%s,%s,%s,%s,%s,1)",
                (stored, original, summary["rows"], summary["placed"],
                 ",".join(f for f in summary["features"] if f in ("projects", "internships", "certifications")),
                 user_id()))
        note = f" {summary['dropped']} invalid row(s) were ignored." if summary["dropped"] else ""
        flash(f"Dataset accepted: {summary['rows']} valid rows.{note} Retrain the model to use it.", "success")
        return redirect(url_for("admin.upload_dataset"))
    return render_template("admin/upload_dataset.html", datasets=query_all("SELECT d.*, u.full_name AS uploader "
                           "FROM datasets d LEFT JOIN users u ON u.id = d.uploaded_by ORDER BY d.id DESC"))


@admin_bp.route("/datasets/<int:dataset_id>/toggle", methods=["POST"])
@admin_required
def dataset_toggle(dataset_id):
    execute_count("UPDATE datasets SET use_for_training = CASE WHEN use_for_training = 1 THEN 0 ELSE 1 END "
                  "WHERE id = %s", (dataset_id,))
    return redirect(url_for("admin.upload_dataset"))


@admin_bp.route("/datasets/<int:dataset_id>/delete", methods=["POST"])
@admin_required
def dataset_delete(dataset_id):
    row = query_one("SELECT * FROM datasets WHERE id = %s", (dataset_id,))
    if row and row["filename"] != "placement_dataset.csv":
        path = os.path.join(current_app.config["DATASET_UPLOAD_DIR"], row["filename"])
        if os.path.exists(path):
            os.remove(path)
        execute("DELETE FROM datasets WHERE id = %s", (dataset_id,))
        flash("Dataset deleted.", "success")
    return redirect(url_for("admin.upload_dataset"))


@admin_bp.route("/model-training", methods=["GET", "POST"])
@admin_required
def model_training():
    if request.method == "POST":
        include_base = request.form.get("include_base") == "1"
        paths = _active_dataset_paths(include_base)
        if not paths:
            flash("Select at least one dataset to train on.", "danger")
            return redirect(url_for("admin.model_training"))
        try:
            meta = train_model(paths, activate=True, trained_by=user_id())
        except Exception as error:  # noqa: BLE001
            log.exception("Training failed")
            flash(f"Training failed: {error}", "danger")
            return redirect(url_for("admin.model_training"))
        execute("UPDATE model_versions SET is_active = 0")
        m = meta["metrics"]
        execute("INSERT INTO model_versions (version, algorithm, accuracy, precision_score, recall_score, "
                "f1_score, roc_auc, train_rows, test_rows, features, is_active, trained_by) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s)",
                (meta["version"], meta["algorithm"], m["accuracy"], m["precision"], m["recall"], m["f1"],
                 m["roc_auc"], meta["train_rows"], meta["test_rows"], ",".join(meta["features"]), user_id()))
        notify_many(User.ids_by_role("admin"), "model_trained", "success", "/admin/model-training",
                    algorithm=meta["algorithm"], version=meta["version"], accuracy=m["accuracy"], rows=meta["rows"])
        flash(f"Model retrained: {meta['algorithm']} reached {m['accuracy']}% accuracy on held-out data.", "success")
        return redirect(url_for("admin.model_training"))
    versions = query_all("SELECT v.*, u.full_name AS trainer FROM model_versions v "
                         "LEFT JOIN users u ON u.id = v.trained_by ORDER BY v.id DESC LIMIT 10")
    return render_template("admin/model_training.html", meta=get_metadata(), versions=versions,
                           datasets=query_all("SELECT * FROM datasets ORDER BY id"))


# --- Analytics & reports ---------------------------------------------------------

@admin_bp.route("/analytics")
@admin_required
def analytics():
    return render_template(
        "admin/analytics.html", averages=pa.score_averages(), branches=pa.branch_breakdown(),
        readiness=pa.readiness_distribution(), cgpa=pa.cgpa_histogram(), compare=pa.placed_vs_not_scores(),
        predictions=pa.prediction_summary(), outcomes=pa.placement_outcomes(), activity=pa.monthly_activity(),
        demand=ca.skills_demand_vs_supply(), matrix=ca.eligibility_matrix(), funnel=ca.drive_funnel())


@admin_bp.route("/reports")
@admin_required
def reports():
    return render_template("admin/reports.html", recent=Report.recent(None, 10))
