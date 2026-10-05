from flask import (
    Blueprint,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

from database.db import get_connection
from reports.pdf_generator import generate_student_report


report_bp = Blueprint(
    "report",
    __name__,
    url_prefix="/reports"
)


def student_required():
    if "user_id" not in session:
        return False

    if session.get("role") != "student":
        return False

    return True


@report_bp.route("/student/pdf")
def student_pdf():

    if not student_required():
        flash("Student access required.", "error")
        return redirect(url_for("auth.login"))

    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:

            # ==================================================
            # 1. STUDENT PROFILE
            # ==================================================

            cursor.execute("""
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
                INNER JOIN students s
                    ON u.id = s.user_id
                WHERE u.id = %s
            """, (
                session["user_id"],
            ))

            student = cursor.fetchone()

            if not student:
                flash(
                    "Student profile not found.",
                    "error"
                )

                return redirect(
                    url_for("dashboard.dashboard")
                )

            # ==================================================
            # 2. LATEST PLACEMENT PREDICTION
            # ==================================================

            cursor.execute("""
                SELECT
                    prediction,
                    placement_probability,
                    not_placed_probability
                FROM prediction_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (
                session["user_id"],
            ))

            prediction = cursor.fetchone()

            # ==================================================
            # 3. LATEST READINESS
            # ==================================================

            cursor.execute("""
                SELECT
                    readiness_score,
                    readiness_level
                FROM readiness_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (
                session["user_id"],
            ))

            readiness = cursor.fetchone()

            # ==================================================
            # 4. LATEST SKILL GAP
            # ==================================================

            cursor.execute("""
                SELECT
                    total_gap,
                    overall_status
                FROM skill_gap_history
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
            """, (
                session["user_id"],
            ))

            skill_gap = cursor.fetchone()

        # ======================================================
        # PREPARE PREDICTION DATA
        # ======================================================

        if prediction:

            prediction_status = (
                prediction.get("prediction")
                or "Not Available"
            )

            placement_probability = (
                prediction.get("placement_probability")
                or 0
            )

            not_placed_probability = (
                prediction.get("not_placed_probability")
                or 0
            )

            if str(prediction_status).lower() == "placed":
                prediction_probability = (
                    placement_probability
                )
            else:
                prediction_probability = (
                    not_placed_probability
                )

        else:

            prediction_status = "Not Available"
            prediction_probability = "Not Available"

        # ======================================================
        # REPORT DATA
        # ======================================================

        report_data = {

            # Placement
            "prediction": prediction_status,

            "probability": prediction_probability,

            # Readiness
            "readiness_score": (
                readiness["readiness_score"]
                if readiness
                else "Not Available"
            ),

            "readiness_level": (
                readiness["readiness_level"]
                if readiness
                else "Not Available"
            ),

            # Skill Gap
            "skill_gap": (
                skill_gap["total_gap"]
                if skill_gap
                else "Not Available"
            ),

            "skill_status": (
                skill_gap["overall_status"]
                if skill_gap
                else "Not Available"
            ),

            # Resume
            "resume_score": "Not Available",
            "resume_status": "Not Available",

            # Recommendations
            "recommendations": []
        }

        # ======================================================
        # GENERATE PDF
        # ======================================================

        pdf_buffer = generate_student_report(
            student,
            report_data
        )

        # ======================================================
        # SAFE FILE NAME
        # ======================================================

        student_name = (
            student.get("full_name")
            or "student"
        )

        safe_name = (
            student_name
            .strip()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        filename = (
            f"{safe_name}_Placement_Report.pdf"
        )

        # ======================================================
        # SEND PDF
        # ======================================================

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as error:

        print(
            "Student PDF Report Error:",
            error
        )

        flash(
            "Unable to generate placement report.",
            "error"
        )

        return redirect(
            url_for("dashboard.dashboard")
        )

    finally:

        if connection:
            connection.close()