from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from analytics import company_analytics as ca
from analytics import placement_analytics as pa
from analytics.dashboard_stats import tpo_overview
from company_eligibility.eligibility_checker import check_all_companies
from models.company import Company, Drive
from models.report import Report
from models.student import Student
from notifications.service import notify, notify_many
from routes._common import float_field, user_id
from utils.constants import APPLICATION_STATUSES, BRANCHES, DRIVE_STATUSES
from utils.decorators import tpo_required

tpo_bp = Blueprint("tpo", __name__, url_prefix="/tpo")


@tpo_bp.route("/dashboard")
@tpo_required
def dashboard():
    return render_template("tpo/tpo_dashboard.html", overview=tpo_overview(), branches=pa.branch_breakdown(),
                           funnel=ca.drive_funnel(), matrix=ca.eligibility_matrix()[:6])


@tpo_bp.route("/placement-statistics")
@tpo_required
def placement_statistics():
    return render_template(
        "tpo/placement_statistics.html", outcomes=pa.placement_outcomes(), branches=pa.branch_breakdown(),
        cgpa=pa.cgpa_histogram(), readiness=pa.readiness_distribution(), demand=ca.skills_demand_vs_supply(),
        predictions=pa.prediction_summary(), status=pa.status_breakdown(), matrix=ca.eligibility_matrix())


@tpo_bp.route("/eligible-students")
@tpo_required
def eligible_students():
    companies = Company.all(active_only=True)
    try:
        selected_id = int(request.args.get("company_id") or (companies[0]["id"] if companies else 0))
    except ValueError:
        selected_id = companies[0]["id"] if companies else 0
    branch = request.args.get("branch", "")
    selected = next((c for c in companies if c["id"] == selected_id), None)
    eligible, near = [], []
    if selected:
        rule = Company.as_rule(selected)
        for s in Student.all(branch=branch):
            if not Student.has_scores(s):
                continue
            res = check_all_companies(s["cgpa"], s["attendance"], s["aptitude_score"], s["coding_score"],
                                      s["communication_score"], s["technical_score"], s.get("skills"),
                                      s.get("backlogs") or 0, [rule])[0]
            row = dict(s, match=res["match_percent"], missing=res["missing_requirements"],
                       missing_skills=res["missing_skills"])
            if res["eligible"]:
                eligible.append(row)
            elif res["match_percent"] >= 75:
                near.append(row)
        eligible.sort(key=lambda r: -r["cgpa"])
        near.sort(key=lambda r: -r["match"])
    return render_template("tpo/eligible_students.html", companies=companies, selected=selected,
                           eligible=eligible, near=near, branches=BRANCHES, branch=branch)


# --- Drives ---------------------------------------------------------------------

def _drive_form(form):
    try:
        company_id = int(form.get("company_id", ""))
    except ValueError:
        raise ValueError("Choose a company.") from None
    if not Company.get(company_id):
        raise ValueError("Choose a company.")
    role = form.get("job_role", "").strip()
    if len(role) < 2:
        raise ValueError("Job role is required.")
    try:
        drive_date = date.fromisoformat(form.get("drive_date", ""))
    except ValueError:
        raise ValueError("Enter a valid drive date.") from None
    status = form.get("status", "Upcoming")
    if status not in DRIVE_STATUSES:
        raise ValueError("Invalid status.")
    return {"company_id": company_id, "job_role": role, "drive_date": drive_date,
            "location": form.get("location", "").strip() or None,
            "openings": int(float_field(form, "openings", 1, 1000, "Openings")),
            "package_lpa": float_field(form, "package_lpa", 0, 500, "Package"),
            "status": status, "description": form.get("description", "").strip() or None}


@tpo_bp.route("/company-drives")
@tpo_required
def company_drives():
    status = request.args.get("status", "")
    return render_template("tpo/company_drives.html", drives=Drive.all(status or None), status=status,
                           statuses=DRIVE_STATUSES)


@tpo_bp.route("/drives/new", methods=["GET", "POST"])
@tpo_required
def drive_new():
    companies = Company.all(active_only=True)
    if request.method == "POST":
        try:
            data = _drive_form(request.form)
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("tpo/drive_form.html", drive=request.form, companies=companies, mode="new",
                                   statuses=DRIVE_STATUSES), 400
        Drive.create(data, user_id())
        company = Company.get(data["company_id"])
        if data["status"] in ("Upcoming", "Active"):
            rule = Company.as_rule(company)
            ids = []
            for s in Student.all():
                if Student.has_scores(s) and check_all_companies(
                        s["cgpa"], s["attendance"], s["aptitude_score"], s["coding_score"],
                        s["communication_score"], s["technical_score"], s.get("skills"),
                        s.get("backlogs") or 0, [rule])[0]["eligible"]:
                    ids.append(s["user_id"])
            notify_many(ids, "new_drive", "drive", "/student/drives", company=company["name"],
                        role=data["job_role"], date=data["drive_date"].strftime("%d %b"))
            flash(f"Drive created. {len(ids)} eligible student(s) were notified.", "success")
        else:
            flash("Drive created.", "success")
        return redirect(url_for("tpo.company_drives"))
    return render_template("tpo/drive_form.html", drive={"status": "Upcoming", "openings": 5, "drive_date": date.today().isoformat()},
                           companies=companies, mode="new", statuses=DRIVE_STATUSES)


@tpo_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"])
@tpo_required
def drive_edit(drive_id):
    drive = Drive.get(drive_id)
    if not drive:
        flash("Drive not found.", "danger")
        return redirect(url_for("tpo.company_drives"))
    companies = Company.all()
    if request.method == "POST":
        try:
            data = _drive_form(request.form)
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("tpo/drive_form.html", drive=request.form, companies=companies, mode="edit",
                                   drive_id=drive_id, statuses=DRIVE_STATUSES), 400
        Drive.update(drive_id, data)
        flash("Drive updated.", "success")
        return redirect(url_for("tpo.company_drives"))
    if isinstance(drive.get("drive_date"), (date, datetime)):
        drive["drive_date"] = drive["drive_date"].strftime("%Y-%m-%d")
    return render_template("tpo/drive_form.html", drive=drive, companies=companies, mode="edit",
                           drive_id=drive_id, statuses=DRIVE_STATUSES)


@tpo_bp.route("/drives/<int:drive_id>/delete", methods=["POST"])
@tpo_required
def drive_delete(drive_id):
    if Drive.get(drive_id):
        Drive.delete(drive_id)
        flash("Drive deleted.", "success")
    return redirect(url_for("tpo.company_drives"))


@tpo_bp.route("/drives/<int:drive_id>/applicants")
@tpo_required
def drive_applicants(drive_id):
    drive = Drive.get(drive_id)
    if not drive:
        flash("Drive not found.", "danger")
        return redirect(url_for("tpo.company_drives"))
    return render_template("tpo/drive_applicants.html", drive=drive, applicants=Drive.applicants(drive_id),
                           statuses=APPLICATION_STATUSES)


@tpo_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@tpo_required
def application_status(application_id):
    app_row = Drive.get_application(application_id)
    status = request.form.get("status", "")
    if not app_row or status not in APPLICATION_STATUSES:
        flash("Invalid request.", "danger")
        return redirect(url_for("tpo.company_drives"))
    previous = app_row["status"]
    Drive.set_application_status(application_id, status)
    uid = app_row["user_id"]
    if status == "Selected":
        Student.set_placement(uid, "Placed", app_row["company_name"], app_row["package_lpa"])
        notify(uid, "selected", "success", "/student/drives", company=app_row["company_name"],
               role=app_row["job_role"])
    else:
        if previous == "Selected":
            student = Student.get_by_user_id(uid)
            if student and student.get("placed_company") == app_row["company_name"]:
                Student.set_placement(uid, "Not Placed")
        if status != previous:
            notify(uid, "application_status", "drive", "/student/drives", company=app_row["company_name"],
                   role=app_row["job_role"], status=status)
    flash("Application updated.", "success")
    return redirect(url_for("tpo.drive_applicants", drive_id=app_row["drive_id"]))


@tpo_bp.route("/reports")
@tpo_required
def reports():
    return render_template("tpo/placement_reports.html", outcomes=pa.placement_outcomes(),
                           recent=Report.recent(None, 8))
