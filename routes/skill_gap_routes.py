from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from database.db import get_connection
from recommendation_engine.skill_gap import calculate_skill_gap


skill_gap_bp = Blueprint(
    "skill_gap",
    __name__,
    url_prefix="/student"
)


@skill_gap_bp.route(
    "/skill-gap",
    methods=["GET", "POST"]
)
def skill_gap():

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
                    aptitude_score,
                    coding_score,
                    communication_score,
                    technical_score
                FROM students
                WHERE user_id = %s
                """,
                (
                    session["user_id"],
                )
            )

            student = cursor.fetchone()

    except Exception as error:

        print(
            "Skill Gap Database Error:",
            error
        )

        flash(
            "Unable to load student profile.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()

    if request.method == "GET":

        inputs = {
            "aptitude_score":
                student["aptitude_score"]
                if student and student["aptitude_score"] is not None
                else "",

            "coding_score":
                student["coding_score"]
                if student and student["coding_score"] is not None
                else "",

            "communication_score":
                student["communication_score"]
                if student and student["communication_score"] is not None
                else "",

            "technical_score":
                student["technical_score"]
                if student and student["technical_score"] is not None
                else ""
        }

        return render_template(
            "student/skill_gap.html",
            inputs=inputs
        )

    try:

        aptitude_score = float(
            request.form.get(
                "aptitude_score",
                0
            )
        )

        coding_score = float(
            request.form.get(
                "coding_score",
                0
            )
        )

        communication_score = float(
            request.form.get(
                "communication_score",
                0
            )
        )

        technical_score = float(
            request.form.get(
                "technical_score",
                0
            )
        )

        result = calculate_skill_gap(
            aptitude_score=aptitude_score,
            coding_score=coding_score,
            communication_score=communication_score,
            technical_score=technical_score
        )

        connection = None

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO skill_gap_history (
                        user_id,
                        aptitude_score,
                        coding_score,
                        communication_score,
                        technical_score,
                        total_gap,
                        overall_status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        session["user_id"],
                        aptitude_score,
                        coding_score,
                        communication_score,
                        technical_score,
                        result["total_gap"],
                        result["overall_status"]
                    )
                )

        except Exception as error:

            print(
                "Skill Gap History Error:",
                error
            )

            flash(
                "Skill gap calculated, but history could not be saved.",
                "warning"
            )

        finally:

            if connection:
                connection.close()

        return render_template(
            "student/skill_gap.html",
            result=result,
            inputs={
                "aptitude_score": aptitude_score,
                "coding_score": coding_score,
                "communication_score": communication_score,
                "technical_score": technical_score
            }
        )

    except ValueError as error:

        flash(
            str(error),
            "danger"
        )

        return redirect(
            url_for(
                "skill_gap.skill_gap"
            )
        )

    except Exception as error:

        print(
            "Skill Gap Route Error:",
            error
        )

        flash(
            "Unable to analyze skill gaps.",
            "danger"
        )

        return redirect(
            url_for(
                "skill_gap.skill_gap"
            )
        )


# ==========================================================
# SKILL GAP HISTORY
# ==========================================================

@skill_gap_bp.route(
    "/skill-gap-history"
)
def skill_gap_history():

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
                    aptitude_score,
                    coding_score,
                    communication_score,
                    technical_score,
                    total_gap,
                    overall_status,
                    created_at
                FROM skill_gap_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (
                    session["user_id"],
                )
            )

            history = cursor.fetchall()

        return render_template(
            "student/skill_gap_history.html",
            history=history
        )

    except Exception as error:

        print(
            "Skill Gap History Route Error:",
            error
        )

        flash(
            "Unable to load skill gap history.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()