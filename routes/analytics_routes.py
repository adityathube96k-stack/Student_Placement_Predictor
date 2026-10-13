
from flask import Blueprint, render_template, redirect, url_for, session, flash
from database.db import get_connection

analytics_bp = Blueprint(
    "analytics",
    __name__,
    url_prefix="/student"
)


@analytics_bp.route("/analytics")
def student_analytics():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_predictions,
                    AVG(placement_probability) AS avg_probability,
                    SUM(
                        CASE
                            WHEN LOWER(prediction) IN (
                                'placed',
                                'likely to be placed',
                                'likely placed'
                            )
                            THEN 1 ELSE 0
                        END
                    ) AS positive_predictions,
                    AVG(cgpa) AS avg_cgpa,
                    AVG(attendance) AS avg_attendance,
                    AVG(aptitude_score) AS avg_aptitude,
                    AVG(coding_score) AS avg_coding,
                    AVG(communication_score) AS avg_communication,
                    AVG(technical_score) AS avg_technical
                FROM prediction_history
                WHERE user_id = %s
                """,
                (session["user_id"],)
            )
            summary = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    created_at,
                    prediction,
                    placement_probability,
                    not_placed_probability
                FROM prediction_history
                WHERE user_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT 10
                """,
                (session["user_id"],)
            )
            history = cursor.fetchall()

        return render_template(
            "student/analytics.html",
            summary=summary,
            history=history
        )

    except Exception as error:
        print("Analytics Error:", error)
        flash("Unable to load analytics right now.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    finally:
        if connection:
            connection.close()
