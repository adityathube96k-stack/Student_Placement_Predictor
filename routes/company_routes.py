from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from database.db import get_connection
from company_eligibility.eligibility_checker import check_all_companies

import json


company_bp = Blueprint(
    "company",
    __name__,
    url_prefix="/student"
)


# =========================================================
# COMPANY ELIGIBILITY
# =========================================================

@company_bp.route("/company-eligibility")
def company_eligibility():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    connection = None

    try:

        connection = get_connection()

        # -----------------------------------------
        # Get student profile
        # -----------------------------------------
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    cgpa,
                    attendance,
                    aptitude_score,
                    coding_score,
                    communication_score,
                    technical_score,
                    skills
                FROM students
                WHERE user_id = %s
                """,
                (session["user_id"],)
            )

            student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "danger"
            )

            return redirect(
                url_for("dashboard.dashboard")
            )

        # -----------------------------------------
        # Check required scores
        # -----------------------------------------
        scores = [
            student["cgpa"],
            student["attendance"],
            student["aptitude_score"],
            student["coding_score"],
            student["communication_score"],
            student["technical_score"]
        ]

        if any(score is None for score in scores):

            flash(
                "Please complete your academic and skill scores "
                "in your profile before checking company eligibility.",
                "warning"
            )

            return redirect(
                url_for("dashboard.profile")
            )

        # -----------------------------------------
        # Student skills
        # -----------------------------------------
        student_skills = student.get("skills")

        # -----------------------------------------
        # Check all companies
        # -----------------------------------------
        results = check_all_companies(

            cgpa=student["cgpa"],

            attendance=student["attendance"],

            aptitude_score=student["aptitude_score"],

            coding_score=student["coding_score"],

            communication_score=student["communication_score"],

            technical_score=student["technical_score"],

            student_skills=student_skills
        )

        # -----------------------------------------
        # Summary
        # -----------------------------------------
        eligible_count = sum(
            1
            for result in results
            if result["eligible"]
        )

        not_eligible_count = (
            len(results) - eligible_count
        )

        # -----------------------------------------
        # Save eligibility results
        # -----------------------------------------
        with connection.cursor() as cursor:

            for result in results:

                missing_requirements = json.dumps(
                    result.get(
                        "missing_requirements",
                        []
                    )
                )

                missing_skills = json.dumps(
                    result.get(
                        "missing_skills",
                        []
                    )
                )

                cursor.execute(
                    """
                    INSERT INTO company_eligibility_history
                    (
                        user_id,
                        company_name,
                        eligible,
                        missing_requirements,
                        missing_skills
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
                        result["company"],
                        result["eligible"],
                        missing_requirements,
                        missing_skills
                    )
                )

        connection.commit()

        return render_template(
            "student/company_eligibility.html",
            results=results,
            student=student,
            eligible_count=eligible_count,
            not_eligible_count=not_eligible_count
        )

    except Exception as error:

        if connection:
            connection.rollback()

        print(
            "Company Eligibility Error:",
            error
        )

        flash(
            "Unable to check company eligibility.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()


# =========================================================
# COMPANY ELIGIBILITY HISTORY
# =========================================================

@company_bp.route("/company-eligibility-history")
def company_eligibility_history():

    # -----------------------------------------
    # Authentication check
    # -----------------------------------------
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.login"))

    connection = None

    try:

        connection = get_connection()

        # -----------------------------------------
        # Get eligibility history
        # -----------------------------------------
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    company_name,
                    eligible,
                    missing_requirements,
                    missing_skills,
                    checked_at
                FROM company_eligibility_history
                WHERE user_id = %s
                ORDER BY checked_at DESC, id DESC
                """,
                (session["user_id"],)
            )

            history = cursor.fetchall()

        # -----------------------------------------
        # Convert JSON fields
        # -----------------------------------------
        for record in history:

            try:

                record["missing_requirements"] = json.loads(
                    record["missing_requirements"]
                ) if record["missing_requirements"] else []

            except (json.JSONDecodeError, TypeError):

                record["missing_requirements"] = []

            try:

                record["missing_skills"] = json.loads(
                    record["missing_skills"]
                ) if record["missing_skills"] else []

            except (json.JSONDecodeError, TypeError):

                record["missing_skills"] = []

        # -----------------------------------------
        # Render history page
        # -----------------------------------------
        return render_template(
            "student/company_eligibility_history.html",
            history=history
        )

    except Exception as error:

        print(
            "Company Eligibility History Error:",
            error
        )

        flash(
            "Unable to load company eligibility history.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()