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

from interview_engine.feedback_generator import (
    generate_feedback
)

from interview_engine.interview_score import (
    calculate_interview_score,
    get_score_level
)

from database.db import get_connection


# =====================================================
# BLUEPRINT
# =====================================================

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

    session["interview_category"] = category

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

    category = session.get(
        "interview_category",
        "Technical"
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

    # =================================================
    # CALCULATE INTERVIEW SCORE
    # =================================================

    interview_score = calculate_interview_score(
        evaluation_results
    )

    performance_level = get_score_level(
        interview_score
    )

    # =================================================
    # GENERATE FEEDBACK
    # =================================================

    feedback = generate_feedback(
        evaluation_results,
        interview_score
    )

    # =================================================
    # SAVE INTERVIEW HISTORY
    # =================================================

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO interview_history
                (
                    user_id,
                    category,
                    total_questions,
                    interview_score,
                    performance_level
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    session["user_id"],
                    category,
                    len(evaluation_results),
                    interview_score,
                    performance_level
                )
            )

        connection.commit()

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "Interview History Error:",
            error
        )

        flash(
            "Interview completed, but history could not be saved.",
            "warning"
        )

    finally:

        if connection:
            connection.close()

    # =================================================
    # CLEAR ACTIVE INTERVIEW SESSION
    # =================================================

    session.pop(
        "interview_questions",
        None
    )

    session.pop(
        "interview_answers",
        None
    )

    session.pop(
        "interview_category",
        None
    )

    # =================================================
    # SHOW RESULT
    # =================================================

    return render_template(
        "student/interview_result.html",
        results=evaluation_results,
        score=interview_score,
        performance_level=performance_level,
        feedback=feedback
    )


# =====================================================
# INTERVIEW HISTORY
# =====================================================

@interview_bp.route(
    "/mock-interview-history"
)
def interview_history():

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

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    category,
                    total_questions,
                    interview_score,
                    performance_level,
                    created_at
                FROM interview_history
                WHERE user_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (session["user_id"],)
            )

            history = cursor.fetchall()

        return render_template(
            "student/interview_history.html",
            history=history
        )

    except Exception as error:

        print(
            "Interview History Error:",
            error
        )

        flash(
            "Unable to load interview history.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()