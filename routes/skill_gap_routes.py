from flask import Blueprint, flash, render_template, request

from database.db import execute, query_all
from recommendation_engine.course_recommender import recommend_courses
from recommendation_engine.skill_gap import calculate_skill_gap
from recommendation_engine.skill_recommendation import generate_skill_recommendations
from routes._common import float_field, get_student, user_id
from utils.decorators import student_required

skill_gap_bp = Blueprint("skill_gap", __name__, url_prefix="/student")
FIELDS = [("cgpa", 0, 10, "CGPA"), ("attendance", 0, 100, "Attendance"),
          ("aptitude_score", 0, 100, "Aptitude score"), ("coding_score", 0, 100, "Coding score"),
          ("communication_score", 0, 100, "Communication score"), ("technical_score", 0, 100, "Technical score")]


@skill_gap_bp.route("/skill-gap", methods=["GET", "POST"])
@student_required
def skill_gap():
    student = get_student()
    values = {k: student.get(k) for k, *_ in FIELDS} if student else {}
    if request.method == "POST":
        try:
            values = {k: float_field(request.form, k, lo, hi, label) for k, lo, hi, label in FIELDS}
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("student/skill_gap.html", values=request.form, gap=None), 400
        save = True
    else:
        save = False
    if any(values.get(k) is None for k, *_ in FIELDS):
        return render_template("student/skill_gap.html", values=values, gap=None)
    gap = calculate_skill_gap(values["aptitude_score"], values["coding_score"],
                              values["communication_score"], values["technical_score"])
    if save:
        execute("INSERT INTO skill_gap_history (user_id,cgpa,attendance,aptitude_score,coding_score,"
                "communication_score,technical_score,total_gap,overall_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (user_id(), *values.values(), gap["total_gap"], gap["overall_status"]))
    recs = generate_skill_recommendations(gap["skills"])
    return render_template("student/skill_gap.html", values=values, gap=gap, recommendations=recs,
                           courses=recommend_courses(gap["skills"], student.get("skills") if student else None, limit=4),
                           saved=save)


@skill_gap_bp.route("/skill-gap-history")
@student_required
def skill_gap_history():
    rows = query_all("SELECT * FROM skill_gap_history WHERE user_id = %s ORDER BY created_at DESC, id DESC", (user_id(),))
    chart = [{"date": r["created_at"].strftime("%d %b"), "value": r["total_gap"]} for r in reversed(rows[:12])]
    return render_template("student/skill_gap_history.html", history=rows, trend=chart)
