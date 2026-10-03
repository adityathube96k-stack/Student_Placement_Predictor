from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from interview_engine.question_generator import (
    get_all_questions,
    get_questions_by_category,
    get_question_by_id
)

from interview_engine.answer_evaluator import evaluate_answer
from interview_engine.feedback_generator import generate_feedback
from interview_engine.interview_score import calculate_interview_score


interview_bp = Blueprint(
    "interview",
    __name__,
    url_prefix="/student"
)


# =====================================================
# MOCK INTERVIEW HOME
# =====================================================

@interview_bp.route("/mock-interview")
def mock_interview():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    questions = get_all_questions()

    return render_template(
        "student/interview.html",
        questions=questions
    )


# =====================================================
# START INTERVIEW
# =====================================================

@interview_bp.route("/mock-interview/start")
def start_interview():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    category = request.args.get(
        "category",
        "Technical"
    )

    questions = get_questions_by_category(
        category
    )

    if not questions:

        flash(
            "No questions available for this category.",
            "warning"
        )

        return redirect(
            url_for("interview.mock_interview")
        )

    session["interview_questions"] = [
        question["id"]
        for question in questions
    ]

    session["interview_answers"] = {}

    return render_template(
        "student/interview_session.html",
        questions=questions,
        category=category
    )


# =====================================================
# SUBMIT INTERVIEW
# =====================================================

@interview_bp.route(
    "/mock-interview/submit",
    methods=["POST"]
)
def submit_interview():

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "student":
        flash(
            "Access denied.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    question_ids = session.get(
        "interview_questions",
        []
    )

    if not question_ids:

        flash(
            "No active interview session found.",
            "warning"
        )

        return redirect(
            url_for("interview.mock_interview")
        )

    answers = {}

    for question_id in question_ids:

        answer = request.form.get(
            f"answer_{question_id}",
            ""
        ).strip()

        answers[str(question_id)] = answer

    session["interview_answers"] = answers

    evaluation_results = []

    for question_id in question_ids:

        question = get_question_by_id(
            int(question_id)
        )

        if not question:
            continue

        answer = answers.get(
            str(question_id),
            ""
        )

        evaluation = evaluate_answer(
            answer=answer,
            keywords=question.get(
                "keywords",
                []
            )
        )

        evaluation_results.append({

            "question":
                question["question"],

            "category":
                question["category"],

            "difficulty":
                question["difficulty"],

            "answer":
                answer,

            "evaluation":
                evaluation
        })

    interview_score = calculate_interview_score(
        evaluation_results
    )

    feedback = generate_feedback(
        evaluation_results,
        interview_score
    )

    session.pop(
        "interview_questions",
        None
    )

    session.pop(
        "interview_answers",
        None
    )

    return render_template(
        "student/interview_result.html",
        results=evaluation_results,
        score=interview_score,
        feedback=feedback
    )