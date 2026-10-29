import random

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from interview_engine.answer_evaluator import evaluate_answer
from interview_engine.feedback_generator import generate_feedback
from interview_engine.interview_score import calculate_interview_score, get_score_level
from interview_engine.question_generator import get_all_questions, get_question_by_id, get_questions_by_category
from models.interview import Interview
from routes._common import user_id
from utils.constants import INTERVIEW_CATEGORIES
from utils.decorators import student_required
from utils.helpers import parse_json

interview_bp = Blueprint("interview", __name__, url_prefix="/student")


@interview_bp.route("/mock-interview")
@student_required
def mock_interview():
    questions = get_all_questions()
    categories = [{"name": c, "count": len(get_questions_by_category(c))} for c in INTERVIEW_CATEGORIES]
    return render_template("student/interview.html", categories=categories, total=len(questions),
                           recent=Interview.history(user_id())[:3])


@interview_bp.route("/mock-interview/start")
@student_required
def start_interview():
    category = request.args.get("category", "Mixed")
    try:
        count = max(3, min(int(request.args.get("count", 5)), 10))
    except ValueError:
        count = 5
    pool = get_all_questions() if category == "Mixed" else get_questions_by_category(category)
    if not pool:
        flash("No questions available for that category.", "danger")
        return redirect(url_for("interview.mock_interview"))
    chosen = random.sample(pool, min(count, len(pool)))
    session["interview"] = {"category": category, "ids": [q["id"] for q in chosen]}
    return render_template("student/interview_session.html", questions=chosen, category=category)


@interview_bp.route("/mock-interview/submit", methods=["POST"])
@student_required
def submit_interview():
    state = session.get("interview")
    if not state:
        flash("Your interview session expired. Start a new one.", "warning")
        return redirect(url_for("interview.mock_interview"))
    results = []
    for qid in state["ids"]:
        question = get_question_by_id(qid)
        answer = request.form.get(f"answer_{qid}", "").strip()
        evaluation = evaluate_answer(answer, question["keywords"])
        results.append({"id": qid, "question": question["question"], "category": question["category"],
                        "difficulty": question["difficulty"], "answer": answer, "evaluation": evaluation})
    score = calculate_interview_score(results)
    feedback = generate_feedback(results, score)
    session.pop("interview", None)
    details = {"results": results, "feedback": feedback}
    interview_id = Interview.save(user_id(), state["category"], len(results), score,
                                  get_score_level(score), details)
    return redirect(url_for("interview.interview_result", interview_id=interview_id))


@interview_bp.route("/mock-interview/result/<int:interview_id>")
@student_required
def interview_result(interview_id):
    row = Interview.get(user_id(), interview_id)
    if not row:
        flash("Interview not found.", "danger")
        return redirect(url_for("interview.interview_history"))
    details = parse_json(row["details"], {})
    results = details.get("results", []) if isinstance(details, dict) else details
    feedback = details.get("feedback", []) if isinstance(details, dict) else []
    return render_template("student/interview_result.html", row=row, results=results, feedback=feedback)


@interview_bp.route("/mock-interview-history")
@student_required
def interview_history():
    rows = Interview.history(user_id())
    chart = [{"date": r["created_at"].strftime("%d %b"), "value": r["interview_score"]} for r in reversed(rows[:12])]
    return render_template("student/interview_history.html", history=rows, trend=chart)
