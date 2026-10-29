from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ml.predict import predict_placement
from models.prediction import Prediction
from recommendation_engine.skill_gap import calculate_skill_gap
from routes._common import float_field, get_student, need_scores, user_id
from utils.decorators import student_required

prediction_bp = Blueprint("prediction", __name__, url_prefix="/student")

FIELDS = [("cgpa", 0, 10, "CGPA"), ("attendance", 0, 100, "Attendance"),
          ("aptitude_score", 0, 100, "Aptitude score"), ("coding_score", 0, 100, "Coding score"),
          ("communication_score", 0, 100, "Communication score"), ("technical_score", 0, 100, "Technical score"),
          ("projects", 0, 50, "Projects"), ("internships", 0, 20, "Internships"),
          ("certifications", 0, 50, "Certifications")]
ADVICE = {
    "cgpa": "Keep your CGPA steady; most recruiters filter on it first.",
    "attendance": "Raise attendance above 75% to clear eligibility screens.",
    "aptitude_score": "Practise timed aptitude sets, since they are the first round at most companies.",
    "coding_score": "Solve data-structure problems daily to lift your coding score.",
    "communication_score": "Practise mock interviews and group discussions.",
    "technical_score": "Revise DBMS, OS and networks, and build one solid project.",
    "projects": "Add a deployable project to your resume.",
    "internships": "An internship or live project strongly improves selection odds.",
    "certifications": "Earn one or two recognised certifications.",
}


def _defaults(student):
    return {k: (student.get(k) if student and student.get(k) is not None else "") for k, *_ in FIELDS}


@prediction_bp.route("/prediction", methods=["GET", "POST"])
@student_required
def prediction():
    student = get_student()
    if request.method == "POST":
        try:
            inputs = {key: float_field(request.form, key, lo, hi, label) for key, lo, hi, label in FIELDS}
        except ValueError as error:
            flash(str(error), "danger")
            return render_template("student/prediction.html", values=request.form, student=student), 400
        result = predict_placement(**inputs)
        Prediction.save(user_id(), inputs, result)
        gap = calculate_skill_gap(inputs["aptitude_score"], inputs["coding_score"],
                                  inputs["communication_score"], inputs["technical_score"])
        tips = [ADVICE[f["feature"]] for f in result["risks"]][:3] or \
               ["You are on track. Keep practising and apply to every eligible drive."]
        return render_template("student/result.html", result=result, inputs=inputs, gap=gap,
                               tips=tips, student=student)
    return render_template("student/prediction.html", values=_defaults(student), student=student)


@prediction_bp.route("/prediction-history")
@student_required
def prediction_history():
    rows = Prediction.history(user_id())
    chart = [{"date": r["created_at"].strftime("%d %b"), "value": r["placement_probability"]}
             for r in reversed(rows[:12])]
    return render_template("student/prediction_history.html", history=rows, trend=chart)


@prediction_bp.route("/prediction/preview", methods=["POST"])
@student_required
def preview():
    """Live what-if estimate for the prediction form (nothing is saved)."""
    payload = request.get_json(silent=True) or {}
    try:
        inputs = {key: float_field(payload, key, lo, hi, label) for key, lo, hi, label in FIELDS}
    except ValueError as error:
        return jsonify(ok=False, error=str(error)), 400
    result = predict_placement(**inputs)
    return jsonify(ok=True, probability=result["placement_probability"], band=result["band"],
                   result=result["result"], factors=result["factors"][:3])
