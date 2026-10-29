from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from company_eligibility.eligibility_checker import check_all_companies, check_student
from database.db import execute_many, query_all, scalar
from models.company import Company, Drive
from models.student import Student
from models.user import User
from notifications.service import notify
from routes._common import get_student, need_scores, user_id
from utils.decorators import student_required

company_bp = Blueprint("company", __name__, url_prefix="/student")


def _snapshot(results):
    """Store a history snapshot at most once every 10 minutes."""
    last = scalar("SELECT MAX(checked_at) FROM company_eligibility_history WHERE user_id = %s", (user_id(),), None)
    if isinstance(last, datetime) and (datetime.now() - last).total_seconds() < 600:
        return
    now = datetime.now()
    execute_many(
        "INSERT INTO company_eligibility_history (user_id, company_name, eligible, missing_requirements, "
        "missing_skills, checked_at) VALUES (%s,%s,%s,%s,%s,%s)",
        [(user_id(), r["company"], 1 if r["eligible"] else 0,
          ", ".join(m["requirement"] for m in r["missing_requirements"]),
          ", ".join(r["missing_skills"]), now) for r in results])


@company_bp.route("/company-eligibility")
@student_required
def company_eligibility():
    student = get_student()
    blocked = need_scores(student)
    if blocked:
        return blocked
    results = check_student(student)
    _snapshot(results)
    eligible = [r for r in results if r["eligible"]]
    return render_template("student/company_eligibility.html", student=student, results=results,
                           eligible=eligible, not_eligible=[r for r in results if not r["eligible"]])


@company_bp.route("/company-eligibility-history")
@student_required
def company_eligibility_history():
    rows = query_all("SELECT * FROM company_eligibility_history WHERE user_id = %s "
                     "ORDER BY checked_at DESC, id", (user_id(),))
    groups = {}
    for row in rows:
        groups.setdefault(row["checked_at"], []).append(row)
    checks = [{"when": when, "rows": items, "eligible": sum(1 for r in items if r["eligible"]),
               "total": len(items)} for when, items in groups.items()]
    return render_template("student/company_eligibility_history.html", checks=checks)


@company_bp.route("/drives")
@student_required
def drives():
    student = get_student()
    scores_ok = Student.has_scores(student)
    rules = {c["id"]: Company.as_rule(c) for c in Company.all()}
    mine = {a["id"]: a for a in Drive.for_student(user_id())}  # keyed by drive id (d.* overrides)
    applied = {a["id"]: a["application_status"] for a in Drive.for_student(user_id())}
    cards = []
    for drive in Drive.open_drives():
        verdict = None
        if scores_ok:
            verdict = check_all_companies(
                student["cgpa"], student["attendance"], student["aptitude_score"], student["coding_score"],
                student["communication_score"], student["technical_score"], student.get("skills"),
                student.get("backlogs") or 0, [rules[drive["company_id"]]])[0]
        cards.append({"drive": drive, "verdict": verdict, "status": applied.get(drive["id"])})
    history = [a for a in Drive.for_student(user_id())]
    return render_template("student/drives.html", cards=cards, history=history, scores_ok=scores_ok, student=student)


@company_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_drive(drive_id):
    student = get_student()
    blocked = need_scores(student)
    if blocked:
        return blocked
    drive = Drive.get(drive_id)
    if not drive or drive["status"] not in ("Upcoming", "Active"):
        flash("This drive is not open for applications.", "danger")
        return redirect(url_for("company.drives"))
    rule = Company.as_rule(Company.get(drive["company_id"]))
    verdict = check_all_companies(
        student["cgpa"], student["attendance"], student["aptitude_score"], student["coding_score"],
        student["communication_score"], student["technical_score"], student.get("skills"),
        student.get("backlogs") or 0, [rule])[0]
    if not verdict["eligible"]:
        flash(f"You do not meet the {drive['company_name']} criteria yet.", "warning")
    elif Drive.application(drive_id, user_id()):
        flash("You have already applied to this drive.", "info")
    else:
        Drive.apply(drive_id, user_id())
        flash(f"Applied to {drive['company_name']}. Track the status here.", "success")
    return redirect(url_for("company.drives"))
