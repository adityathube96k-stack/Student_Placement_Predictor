from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from database.db import get_connection


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/student"
)


# ==========================================================
# STUDENT DASHBOARD
# ==========================================================

@dashboard_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "error")
        return redirect(url_for("auth.login"))

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    u.full_name,
                    u.email,

                    s.enrollment_no,
                    s.phone,
                    s.branch,
                    s.year,

                    s.cgpa,
                    s.attendance,
                    s.aptitude_score,
                    s.coding_score,
                    s.communication_score,
                    s.technical_score,

                    s.skills

                FROM users u

                JOIN students s
                    ON u.id = s.user_id

                WHERE u.id = %s
                """,
                (session["user_id"],)
            )

            student = cursor.fetchone()

        return render_template(
            "student/dashboard.html",
            student=student
        )

    except Exception as error:

        print("Dashboard Error:", error)

        flash(
            "Unable to load dashboard.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    finally:

        if connection:
            connection.close()


# ==========================================================
# STUDENT PROFILE
# ==========================================================

@dashboard_bp.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "error")
        return redirect(url_for("auth.login"))

    connection = None


    # ======================================================
    # UPDATE PROFILE
    # ======================================================

    if request.method == "POST":

        enrollment_no = request.form.get(
            "enrollment_no",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        cgpa = request.form.get(
            "cgpa",
            ""
        ).strip()

        attendance = request.form.get(
            "attendance",
            ""
        ).strip()

        aptitude_score = request.form.get(
            "aptitude_score",
            ""
        ).strip()

        coding_score = request.form.get(
            "coding_score",
            ""
        ).strip()

        communication_score = request.form.get(
            "communication_score",
            ""
        ).strip()

        technical_score = request.form.get(
            "technical_score",
            ""
        ).strip()

        # NEW: STUDENT SKILLS

        skills = request.form.get(
            "skills",
            ""
        ).strip()


        # ==================================================
        # BASIC VALIDATION
        # ==================================================

        if not enrollment_no:

            flash(
                "Enrollment number is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )


        if not branch:

            flash(
                "Branch is required.",
                "error"
            )

            return redirect(
                url_for("dashboard.profile")
            )


        # ==================================================
        # SAVE PROFILE
        # ==================================================

        try:

            connection = get_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE students

                    SET

                        enrollment_no = %s,
                        phone = %s,
                        branch = %s,
                        year = %s,

                        cgpa = %s,
                        attendance = %s,

                        aptitude_score = %s,
                        coding_score = %s,
                        communication_score = %s,
                        technical_score = %s,

                        skills = %s

                    WHERE user_id = %s
                    """,

                    (

                        enrollment_no,
                        phone,
                        branch,

                        year or None,

                        cgpa or None,
                        attendance or None,

                        aptitude_score or None,
                        coding_score or None,
                        communication_score or None,
                        technical_score or None,

                        skills or None,

                        session["user_id"]

                    )
                )

            connection.commit()

            flash(
                "Profile updated successfully!",
                "success"
            )

            return redirect(
                url_for("dashboard.profile")
            )


        except Exception as error:

            if connection:
                connection.rollback()

            print(
                "Profile Update Error:",
                error
            )

            flash(
                "Unable to update profile.",
                "error"
            )


        finally:

            if connection:
                connection.close()


    # ======================================================
    # LOAD PROFILE
    # ======================================================

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT

                    u.full_name,
                    u.email,

                    s.enrollment_no,
                    s.phone,
                    s.branch,
                    s.year,

                    s.cgpa,
                    s.attendance,

                    s.aptitude_score,
                    s.coding_score,
                    s.communication_score,
                    s.technical_score,

                    s.skills

                FROM users u

                JOIN students s
                    ON u.id = s.user_id

                WHERE u.id = %s
                """,

                (session["user_id"],)
            )

            student = cursor.fetchone()


        return render_template(
            "student/profile.html",
            student=student
        )


    except Exception as error:

        print(
            "Profile Error:",
            error
        )

        flash(
            "Unable to load profile.",
            "error"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )


    finally:

        if connection:
            connection.close()