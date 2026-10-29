from flask import Blueprint, flash, render_template, request

from database.db import execute, query_all
from routes._common import float_field, get_student, user_id
from utils.decorators import student_required
from utils.readiness import calculate_readiness_score

readiness_bp = Blueprint("readiness", __name__, url_prefix="/student")
FIELDS = [("cgpa", 0, 10, "CGPA"), ("attendance", 0, 100, "Attendance"),
          ("aptitude_score", 0, 100, "Aptitude score"), ("coding_score", 0, 100, "Coding score"),
          ("communication_score", 0, 100, "Communication score"), ("technical_score", 0, 100, "Technical score")]


def _from_student(student):
    if not student or any(student.get(k) is None for k, *_ in FIELDS):
        return None
    return {k: student[k] for k, *_ in FIELDS}


@readiness_bp.route("/readiness-score", methods=["GET", "POST"])
@student_required
def readiness_score():
    student = get_student()
    values, saved = _from_student(student), False
    if request.method == "POST":
        try:
            values = {k: float_field(request.form, k, lo, hi, label) for k, lo, hi, label in FIELDS}
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("student/readiness_score.html", values=request.form, result=None), 400
        result = calculate_readiness_score(**values)
        execute(
            "INSERT INTO readiness_history (user_id,cgpa,attendance,aptitude_score,coding_score,"
            "communication_score,technical_score,readiness_score,readiness_level) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_id(), *values.values(), result["readiness_score"], result["readiness_level"]))
        saved = True
    else:
        result = calculate_readiness_score(**values) if values else None
    return render_template("student/readiness_score.html", values=values or {}, result=result, saved=saved)


@readiness_bp.route("/readiness-history")
@student_required
def readiness_history():
    rows = query_all("SELECT * FROM readiness_history WHERE user_id = %s ORDER BY created_at DESC, id DESC", (user_id(),))
    chart = [{"date": r["created_at"].strftime("%d %b"), "value": r["readiness_score"]} for r in reversed(rows[:12])]
    return render_template("student/readiness_history.html", history=rows, trend=chart)
