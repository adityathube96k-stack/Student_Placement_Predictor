from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from database.db import get_connection

from company_eligibility.eligibility_checker import (
    check_all_companies
)


# ==========================================================
# COMPANY ELIGIBILITY BLUEPRINT
# ==========================================================

company_bp = Blueprint(
    "company",
    __name__,
    url_prefix="/student"
)


# ==========================================================
# COMPANY ELIGIBILITY
# ==========================================================

@company_bp.route("/company-eligibility")
def company_eligibility():

    # ------------------------------------------------------
    # LOGIN CHECK
    # ------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )


    # ------------------------------------------------------
    # ROLE CHECK
    # ------------------------------------------------------

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

        # --------------------------------------------------
        # DATABASE CONNECTION
        # --------------------------------------------------

        connection = get_connection()


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


        # --------------------------------------------------
        # STUDENT PROFILE CHECK
        # --------------------------------------------------

        if not student:

            flash(
                "Student profile not found.",
                "danger"
            )

            return redirect(
                url_for("dashboard.dashboard")
            )


        # --------------------------------------------------
        # CHECK SCORE VALUES
        # --------------------------------------------------

        scores = [

            student["cgpa"],

            student["attendance"],

            student["aptitude_score"],

            student["coding_score"],

            student["communication_score"],

            student["technical_score"]

        ]


        if any(
            score is None
            for score in scores
        ):

            flash(

                "Please complete your academic and "
                "skill scores in your profile before "
                "checking company eligibility.",

                "warning"

            )

            return redirect(
                url_for("dashboard.profile")
            )


        # --------------------------------------------------
        # STUDENT SKILLS
        # --------------------------------------------------

        student_skills = student.get(
            "skills"
        )


        # --------------------------------------------------
        # CHECK ALL COMPANIES
        # --------------------------------------------------

        results = check_all_companies(

            cgpa=student["cgpa"],

            attendance=student["attendance"],

            aptitude_score=student["aptitude_score"],

            coding_score=student["coding_score"],

            communication_score=student["communication_score"],

            technical_score=student["technical_score"],

            student_skills=student_skills

        )


        # --------------------------------------------------
        # SUMMARY COUNTS
        # --------------------------------------------------

        eligible_count = sum(

            1

            for result in results

            if result["eligible"]

        )


        not_eligible_count = (

            len(results)
            - eligible_count

        )


        # --------------------------------------------------
        # RENDER PAGE
        # --------------------------------------------------

        return render_template(

            "student/company_eligibility.html",

            results=results,

            student=student,

            eligible_count=eligible_count,

            not_eligible_count=not_eligible_count

        )


    except Exception as error:

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