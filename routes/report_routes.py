from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, send_file, session, url_for

from database.db import query_all
from models.report import Report
from models.student import Student
from reports.excel_generator import build_csv, build_workbook
from reports.pdf_generator import generate_student_report
from reports.report_templates import build_student_report_data
from routes._common import get_student, user_id
from utils.decorators import role_required, student_required

report_bp = Blueprint("report", __name__, url_prefix="/reports")
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
STAFF = role_required("admin", "tpo")


def _stamp():
    return datetime.now().strftime("%Y%m%d")


def _send(buffer, name, mimetype, kind, fmt):
    Report.log(user_id(), kind, fmt)
    return send_file(buffer, as_attachment=True, download_name=name, mimetype=mimetype)


@report_bp.route("/student")
@student_required
def student_reports():
    return render_template("student/reports.html", student=get_student(), recent=Report.recent(user_id()))


@report_bp.route("/student/pdf")
@student_required
def student_pdf():
    student = get_student()
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))
    buffer = generate_student_report(student, build_student_report_data(user_id(), student))
    safe = "".join(ch if ch.isalnum() else "_" for ch in (student.get("full_name") or "student")).strip("_")
    return _send(buffer, f"{safe}_Placement_Report.pdf", "application/pdf", "student_pdf", "pdf")


@report_bp.route("/student/history.xlsx")
@student_required
def student_history_xlsx():
    uid = user_id()
    preds = query_all("SELECT created_at, prediction, placement_probability, cgpa, attendance, aptitude_score, "
                      "coding_score, communication_score, technical_score FROM prediction_history "
                      "WHERE user_id = %s ORDER BY id DESC", (uid,))
    ready = query_all("SELECT created_at, readiness_score, readiness_level FROM readiness_history "
                      "WHERE user_id = %s ORDER BY id DESC", (uid,))
    ivs = query_all("SELECT created_at, category, total_questions, interview_score, performance_level "
                    "FROM interview_history WHERE user_id = %s ORDER BY id DESC", (uid,))
    sheets = [
        ("Predictions", ["Date", "Result", "Placement %", "CGPA", "Attendance", "Aptitude", "Coding", "Communication", "Technical"],
         [list(map(_cell, r.values())) for r in preds]),
        ("Readiness", ["Date", "Score", "Level"], [list(map(_cell, r.values())) for r in ready]),
        ("Mock interviews", ["Date", "Category", "Questions", "Score", "Level"], [list(map(_cell, r.values())) for r in ivs]),
    ]
    return _send(build_workbook(sheets, "Your activity history"), f"My_Placement_History_{_stamp()}.xlsx",
                 XLSX, "student_history", "xlsx")


def _cell(v):
    return v.strftime("%Y-%m-%d %H:%M") if hasattr(v, "strftime") else v


# --- Staff exports (admin + TPO) ----------------------------------------------

def _students_rows():
    rows = Student.all()
    return [[r["full_name"], r["email"], r["enrollment_no"], r["branch"], r["year"], r["cgpa"], r["attendance"],
             r["backlogs"], r["aptitude_score"], r["coding_score"], r["communication_score"],
             r["technical_score"], r["projects"], r["internships"], r["certifications"],
             r["placement_status"], r["placed_company"], r["package_lpa"], r["skills"]] for r in rows]


STUDENT_HEADERS = ["Name", "Email", "Enrollment", "Branch", "Year", "CGPA", "Attendance %", "Backlogs",
                   "Aptitude", "Coding", "Communication", "Technical", "Projects", "Internships",
                   "Certifications", "Placement status", "Company", "Package (LPA)", "Skills"]


@report_bp.route("/staff/students.xlsx")
@STAFF
def students_xlsx():
    return _send(build_workbook([("Students", STUDENT_HEADERS, _students_rows())], "Student records"),
                 f"Students_{_stamp()}.xlsx", XLSX, "students", "xlsx")


@report_bp.route("/staff/students.csv")
@STAFF
def students_csv():
    return _send(build_csv(STUDENT_HEADERS, _students_rows()), f"Students_{_stamp()}.csv", "text/csv",
                 "students", "csv")


@report_bp.route("/staff/predictions.xlsx")
@STAFF
def predictions_xlsx():
    rows = query_all("SELECT u.full_name, p.created_at, p.prediction, p.placement_probability, p.cgpa, p.attendance, "
                     "p.aptitude_score, p.coding_score, p.communication_score, p.technical_score, p.model_version "
                     "FROM prediction_history p JOIN users u ON u.id = p.user_id ORDER BY p.id DESC")
    headers = ["Student", "Date", "Result", "Placement %", "CGPA", "Attendance", "Aptitude", "Coding",
               "Communication", "Technical", "Model"]
    return _send(build_workbook([("Predictions", headers, [list(map(_cell, r.values())) for r in rows])]),
                 f"Predictions_{_stamp()}.xlsx", XLSX, "predictions", "xlsx")


@report_bp.route("/staff/placements.xlsx")
@STAFF
def placements_xlsx():
    from analytics.company_analytics import drive_funnel, eligibility_matrix
    from analytics.placement_analytics import branch_breakdown
    placed = [[r["full_name"], r["branch"], r["cgpa"], r["placed_company"], r["package_lpa"]]
              for r in Student.all(status="Placed")]
    sheets = [
        ("Placed students", ["Name", "Branch", "CGPA", "Company", "Package (LPA)"], placed),
        ("Branch summary", ["Branch", "Students", "Placed", "Avg CGPA", "Placement %"],
         [[b["branch"], b["students"], b["placed"], b["avg_cgpa"], b["placement_rate"]] for b in branch_breakdown()]),
        ("Eligibility by company", ["Company", "Package (LPA)", "Eligible students", "Assessed"],
         [[e["company"], e["package_lpa"], e["eligible"], e["assessed"]] for e in eligibility_matrix()]),
        ("Application funnel", ["Stage", "Count"], [[f["stage"], f["count"]] for f in drive_funnel()]),
    ]
    return _send(build_workbook(sheets, "Placement summary"), f"Placement_Report_{_stamp()}.xlsx",
                 XLSX, "placements", "xlsx")


@report_bp.route("/staff/companies.xlsx")
@STAFF
def companies_xlsx():
    rows = query_all("SELECT name, industry, location, package_lpa, min_cgpa, min_attendance, min_aptitude, "
                     "min_coding, min_communication, min_technical, max_backlogs, required_skills, is_active "
                     "FROM companies ORDER BY name")
    headers = ["Company", "Industry", "Location", "Package (LPA)", "Min CGPA", "Min attendance", "Min aptitude",
               "Min coding", "Min communication", "Min technical", "Max backlogs", "Required skills", "Active"]
    return _send(build_workbook([("Companies", headers, [list(r.values()) for r in rows])]),
                 f"Companies_{_stamp()}.xlsx", XLSX, "companies", "xlsx")
