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

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    if "user_id" not in session:

        flash(
            "Please login to access Skill Gap Analysis.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    user_id = session["user_id"]


    # =====================================================
    # DEFAULT INPUTS
    # =====================================================

    inputs = {
        "cgpa": "",
        "attendance": "",
        "aptitude_score": "",
        "coding_score": "",
        "communication_score": "",
        "technical_score": ""
    }


    result = None


    # =====================================================
    # GET STUDENT PROFILE
    # =====================================================

    connection = None

    try:

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
                    technical_score
                FROM students
                WHERE user_id = %s
                """,
                (user_id,)
            )

            student = cursor.fetchone()


        if student:

            inputs = {
                "cgpa": (
                    student["cgpa"]
                    if student["cgpa"] is not None
                    else ""
                ),

                "attendance": (
                    student["attendance"]
                    if student["attendance"] is not None
                    else ""
                ),

                "aptitude_score": (
                    student["aptitude_score"]
                    if student["aptitude_score"] is not None
                    else ""
                ),

                "coding_score": (
                    student["coding_score"]
                    if student["coding_score"] is not None
                    else ""
                ),

                "communication_score": (
                    student["communication_score"]
                    if student["communication_score"] is not None
                    else ""
                ),

                "technical_score": (
                    student["technical_score"]
                    if student["technical_score"] is not None
                    else ""
                )
            }


    except Exception as error:

        print(
            "Skill Gap Profile Error:",
            error
        )

    finally:

        if connection:

            connection.close()


    # =====================================================
    # POST - ANALYZE SKILL GAP
    # =====================================================

    if request.method == "POST":

        try:

            # -------------------------------------------------
            # READ INPUTS
            # -------------------------------------------------

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


            # -------------------------------------------------
            # STORE INPUTS FOR TEMPLATE
            # -------------------------------------------------

            inputs = {
                "cgpa": cgpa,
                "attendance": attendance,
                "aptitude_score": aptitude_score,
                "coding_score": coding_score,
                "communication_score": communication_score,
                "technical_score": technical_score
            }


            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            if not 0 <= cgpa <= 10:

                flash(
                    "CGPA must be between 0 and 10.",
                    "danger"
                )

                return render_template(
                    "student/skill_gap.html",
                    inputs=inputs,
                    result=None
                )


            if not 0 <= attendance <= 100:

                flash(
                    "Attendance must be between 0 and 100.",
                    "danger"
                )

                return render_template(
                    "student/skill_gap.html",
                    inputs=inputs,
                    result=None
                )


            score_values = [
                aptitude_score,
                coding_score,
                communication_score,
                technical_score
            ]


            if any(
                score < 0 or score > 100
                for score in score_values
            ):

                flash(
                    "Skill scores must be between 0 and 100.",
                    "danger"
                )

                return render_template(
                    "student/skill_gap.html",
                    inputs=inputs,
                    result=None
                )


            # -------------------------------------------------
            # CALCULATE SKILL GAP
            # -------------------------------------------------

            result = calculate_skill_gap(
                aptitude_score,
                coding_score,
                communication_score,
                technical_score
            )


            # -------------------------------------------------
            # ACADEMIC TARGETS
            # -------------------------------------------------

            cgpa_target = 8.0
            attendance_target = 75.0


            cgpa_gap = max(
                0,
                round(
                    cgpa_target - cgpa,
                    2
                )
            )


            attendance_gap = max(
                0,
                round(
                    attendance_target - attendance,
                    2
                )
            )


            # -------------------------------------------------
            # ACADEMIC RESULT
            # -------------------------------------------------

            result["academic"] = {

                "cgpa": round(
                    cgpa,
                    2
                ),

                "cgpa_target": cgpa_target,

                "cgpa_gap": cgpa_gap,

                "attendance": round(
                    attendance,
                    2
                ),

                "attendance_target": attendance_target,

                "attendance_gap": attendance_gap
            }


            # -------------------------------------------------
            # PRIORITY SKILLS
            # -------------------------------------------------

            priority_skills = list(
                result.get(
                    "priority_skills",
                    []
                )
            )


            if cgpa_gap > 0:

                priority_skills.insert(
                    0,
                    "CGPA"
                )


            if attendance_gap > 0:

                priority_skills.insert(
                    1 if cgpa_gap > 0 else 0,
                    "Attendance"
                )


            # Remove duplicates while
            # preserving order

            result["priority_skills"] = list(
                dict.fromkeys(
                    priority_skills
                )
            )


            # -------------------------------------------------
            # SAVE HISTORY
            # -------------------------------------------------

            connection = None

            try:

                connection = get_connection()

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        INSERT INTO skill_gap_history
                        (
                            user_id,
                            cgpa,
                            attendance,
                            aptitude_score,
                            coding_score,
                            communication_score,
                            technical_score,
                            total_gap,
                            overall_status
                        )
                        VALUES
                        (
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
                            user_id,
                            cgpa,
                            attendance,
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


            # -------------------------------------------------
            # RENDER RESULT
            # -------------------------------------------------

            return render_template(
                "student/skill_gap.html",
                inputs=inputs,
                result=result
            )


        except ValueError:

            flash(
                "Please enter valid numeric values.",
                "danger"
            )

            return render_template(
                "student/skill_gap.html",
                inputs=inputs,
                result=None
            )


        except Exception as error:

            print(
                "Skill Gap Error:",
                error
            )

            flash(
                "Unable to analyze skill gap. Please try again.",
                "danger"
            )

            return render_template(
                "student/skill_gap.html",
                inputs=inputs,
                result=None
            )


    # =====================================================
    # GET REQUEST
    # =====================================================

    return render_template(
        "student/skill_gap.html",
        inputs=inputs,
        result=result
    )


# =========================================================
# SKILL GAP HISTORY
# =========================================================

@skill_gap_bp.route(
    "/skill-gap-history"
)
def skill_gap_history():

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    if "user_id" not in session:

        flash(
            "Please login to view Skill Gap History.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )


    user_id = session["user_id"]

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
                    total_gap,
                    overall_status,
                    created_at
                FROM skill_gap_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,)
            )

            history = cursor.fetchall()


        return render_template(
            "student/skill_gap_history.html",
            history=history
        )


    except Exception as error:

        print(
            "Skill Gap History Error:",
            error
        )

        flash(
            "Unable to load Skill Gap History.",
            "danger"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )


    finally:

        if connection:

            connection.close()