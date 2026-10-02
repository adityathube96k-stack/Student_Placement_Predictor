from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from database.db import get_connection

from recommendation_engine.skill_gap import (
    calculate_skill_gap
)

from recommendation_engine.skill_recommendation import (
    generate_skill_recommendations
)


recommendation_bp = Blueprint(
    "recommendation",
    __name__,
    url_prefix="/student"
)


@recommendation_bp.route("/recommendations")
def recommendations():

    # =================================================
    # LOGIN CHECK
    # =================================================

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    # =================================================
    # ROLE CHECK
    # =================================================

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

        # =================================================
        # CONNECT TO MYSQL
        # =================================================

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    aptitude_score,
                    coding_score,
                    communication_score,
                    technical_score
                FROM students
                WHERE user_id = %s
                """,
                (session["user_id"],)
            )

            student = cursor.fetchone()

        # =================================================
        # CHECK PROFILE
        # =================================================

        if not student:

            flash(
                "Student profile not found.",
                "danger"
            )

            return redirect(
                url_for("dashboard.dashboard")
            )

        # =================================================
        # CHECK SCORES
        # =================================================

        required_scores = [
            student["aptitude_score"],
            student["coding_score"],
            student["communication_score"],
            student["technical_score"]
        ]

        if any(
            score is None
            for score in required_scores
        ):

            flash(
                "Please complete your skill scores in your profile first.",
                "warning"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        # =================================================
        # CALCULATE SKILL GAP
        # =================================================

        skill_gap_result = calculate_skill_gap(

            aptitude_score=
                student["aptitude_score"],

            coding_score=
                student["coding_score"],

            communication_score=
                student["communication_score"],

            technical_score=
                student["technical_score"]
        )

        # =================================================
        # GENERATE RECOMMENDATIONS
        # =================================================

        recommendations = (
            generate_skill_recommendations(
                skill_gap_result["skills"]
            )
        )

        # =================================================
        # DISPLAY PAGE
        # =================================================

        return render_template(

            "student/recommendations.html",

            recommendations=
                recommendations,

            skill_gap=
                skill_gap_result
        )

    except Exception as error:

        print(
            "Recommendation Route Error:",
            error
        )

        flash(
            "Unable to generate recommendations.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()