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
from utils.readiness import calculate_readiness_score


readiness_bp = Blueprint(
    "readiness",
    __name__,
    url_prefix="/student"
)


@readiness_bp.route(
    "/readiness-score",
    methods=["GET", "POST"]
)
def readiness_score():

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

    if request.method == "GET":

        return render_template(
            "student/readiness_score.html"
        )

    try:

        cgpa = float(
            request.form.get(
                "cgpa",
                0
            )
        )

        attendance = float(
            request.form.get(
                "attendance",
                0
            )
        )

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

        result = calculate_readiness_score(
            cgpa=cgpa,
            attendance=attendance,
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
                    INSERT INTO readiness_history (
                        user_id,
                        cgpa,
                        attendance,
                        aptitude_score,
                        coding_score,
                        communication_score,
                        technical_score,
                        readiness_score,
                        readiness_level
                    )
                    VALUES (
                        %s,
                        %s,
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
                        cgpa,
                        attendance,
                        aptitude_score,
                        coding_score,
                        communication_score,
                        technical_score,
                        result["readiness_score"],
                        result["readiness_level"]
                    )
                )

        except Exception as error:

            print(
                "Readiness History Error:",
                error
            )

            flash(
                "Readiness score calculated, but history could not be saved.",
                "warning"
            )

        finally:

            if connection:
                connection.close()

        return render_template(
            "student/readiness_score.html",
            result=result,
            inputs={
                "cgpa": cgpa,
                "attendance": attendance,
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
                "readiness.readiness_score"
            )
        )

    except Exception as error:

        print(
            "Readiness Route Error:",
            error
        )

        flash(
            "Unable to calculate readiness score.",
            "danger"
        )

        return redirect(
            url_for(
                "readiness.readiness_score"
            )
        )


# ==========================================================
# READINESS HISTORY
# ==========================================================

@readiness_bp.route(
    "/readiness-history"
)
def readiness_history():

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
                    cgpa,
                    attendance,
                    aptitude_score,
                    coding_score,
                    communication_score,
                    technical_score,
                    readiness_score,
                    readiness_level,
                    created_at
                FROM readiness_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (
                    session["user_id"],
                )
            )

            history = cursor.fetchall()

        return render_template(
            "student/readiness_history.html",
            history=history
        )

    except Exception as error:

        print(
            "Readiness History Route Error:",
            error
        )

        flash(
            "Unable to load readiness history.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()