from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash
)

from database.db import get_connection


tpo_bp = Blueprint(
    "tpo",
    __name__,
    url_prefix="/tpo"
)


# =====================================================
# TPO ACCESS CONTROL
# =====================================================

def tpo_required():
    if "user_id" not in session:
        return False

    if session.get("role") != "tpo":
        return False

    return True


# =====================================================
# TPO DASHBOARD
# =====================================================

@tpo_bp.route("/dashboard")
def dashboard():

    if not tpo_required():
        flash("TPO access required.", "error")
        return redirect(url_for("auth.login"))

    connection = None

    stats = {
        "total_students": 0,
        "total_predictions": 0,
        "placed_students": 0,
        "not_placed_students": 0
    }

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            # -----------------------------------------
            # TOTAL STUDENTS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM students
            """)

            result = cursor.fetchone()

            stats["total_students"] = result["total"] or 0


            # -----------------------------------------
            # TOTAL PREDICTIONS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
            """)

            result = cursor.fetchone()

            stats["total_predictions"] = result["total"] or 0


            # -----------------------------------------
            # PLACED PREDICTIONS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
                WHERE prediction = 'Placed'
            """)

            result = cursor.fetchone()

            stats["placed_students"] = result["total"] or 0


            # -----------------------------------------
            # NOT PLACED PREDICTIONS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
                WHERE prediction = 'Not Placed'
            """)

            result = cursor.fetchone()

            stats["not_placed_students"] = result["total"] or 0


        return render_template(
            "tpo/tpo_dashboard.html",
            stats=stats
        )


    except Exception as error:

        print("TPO Dashboard Error:", error)

        flash(
            "Unable to load TPO dashboard.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    finally:

        if connection:
            connection.close()


# =====================================================
# PLACEMENT STATISTICS
# =====================================================

@tpo_bp.route("/placement-statistics")
def placement_statistics():

    if not tpo_required():
        flash(
            "TPO access required.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = None

    statistics = {
        "total_students": 0,
        "total_predictions": 0,
        "placed_predictions": 0,
        "not_placed_predictions": 0,
        "placement_rate": 0,
        "average_cgpa": 0,
        "average_attendance": 0,
        "average_aptitude": 0,
        "average_coding": 0,
        "average_communication": 0,
        "average_technical": 0
    }

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            # -----------------------------------------
            # STUDENT COUNT
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM students
            """)

            result = cursor.fetchone()

            statistics["total_students"] = result["total"] or 0


            # -----------------------------------------
            # STUDENT AVERAGES
            # -----------------------------------------

            cursor.execute("""
                SELECT
                    AVG(cgpa) AS average_cgpa,
                    AVG(attendance) AS average_attendance,
                    AVG(aptitude_score) AS average_aptitude,
                    AVG(coding_score) AS average_coding,
                    AVG(communication_score)
                        AS average_communication,
                    AVG(technical_score)
                        AS average_technical
                FROM students
            """)

            result = cursor.fetchone()

            statistics["average_cgpa"] = round(
                float(result["average_cgpa"] or 0),
                2
            )

            statistics["average_attendance"] = round(
                float(result["average_attendance"] or 0),
                2
            )

            statistics["average_aptitude"] = round(
                float(result["average_aptitude"] or 0),
                2
            )

            statistics["average_coding"] = round(
                float(result["average_coding"] or 0),
                2
            )

            statistics["average_communication"] = round(
                float(result["average_communication"] or 0),
                2
            )

            statistics["average_technical"] = round(
                float(result["average_technical"] or 0),
                2
            )


            # -----------------------------------------
            # PREDICTION STATISTICS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
            """)

            result = cursor.fetchone()

            statistics["total_predictions"] = (
                result["total"] or 0
            )


            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
                WHERE prediction = 'Placed'
            """)

            result = cursor.fetchone()

            statistics["placed_predictions"] = (
                result["total"] or 0
            )


            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
                WHERE prediction = 'Not Placed'
            """)

            result = cursor.fetchone()

            statistics["not_placed_predictions"] = (
                result["total"] or 0
            )


            # -----------------------------------------
            # PLACEMENT RATE
            # -----------------------------------------

            if statistics["total_predictions"] > 0:

                statistics["placement_rate"] = round(
                    (
                        statistics["placed_predictions"]
                        /
                        statistics["total_predictions"]
                    ) * 100,
                    2
                )


        return render_template(
            "tpo/placement_statistics.html",
            statistics=statistics
        )


    except Exception as error:

        print(
            "TPO Placement Statistics Error:",
            error
        )

        flash(
            "Unable to load placement statistics.",
            "error"
        )

        return redirect(
            url_for("tpo.dashboard")
        )


    finally:

        if connection:
            connection.close()


# =====================================================
# ELIGIBLE STUDENTS
# =====================================================

@tpo_bp.route("/eligible-students")
def eligible_students():

    if not tpo_required():
        flash(
            "TPO access required.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = None

    students = []

    placed_count = 0
    average_cgpa = 0

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            # -----------------------------------------
            # STUDENT ELIGIBILITY DATA
            # -----------------------------------------

            cursor.execute("""
                SELECT
                    s.id,
                    u.full_name,
                    u.email,
                    s.enrollment_no,
                    s.branch,
                    s.cgpa,
                    s.attendance,
                    s.aptitude_score,
                    s.coding_score,
                    s.communication_score,
                    s.technical_score,

                    (
                        SELECT ph.prediction
                        FROM prediction_history ph
                        WHERE ph.user_id = s.user_id
                        ORDER BY ph.created_at DESC
                        LIMIT 1
                    ) AS prediction

                FROM students s

                INNER JOIN users u
                    ON s.user_id = u.id

                ORDER BY s.cgpa DESC
            """)

            students = cursor.fetchall()


            # -----------------------------------------
            # PLACED COUNT
            # -----------------------------------------

            for student in students:

                if student["prediction"] == "Placed":
                    placed_count += 1


            # -----------------------------------------
            # AVERAGE CGPA
            # -----------------------------------------

            cursor.execute("""
                SELECT AVG(cgpa) AS average_cgpa
                FROM students
                WHERE cgpa IS NOT NULL
            """)

            result = cursor.fetchone()

            average_cgpa = round(
                float(result["average_cgpa"] or 0),
                2
            )


        return render_template(
            "tpo/eligible_students.html",
            students=students,
            placed_count=placed_count,
            average_cgpa=average_cgpa
        )


    except Exception as error:

        print(
            "TPO Eligible Students Error:",
            error
        )

        flash(
            "Unable to load eligible students.",
            "error"
        )

        return redirect(
            url_for("tpo.dashboard")
        )


    finally:

        if connection:
            connection.close()


# =====================================================
# COMPANY DRIVES
# =====================================================

@tpo_bp.route("/company-drives")
def company_drives():

    if not tpo_required():
        flash(
            "TPO access required.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    # -------------------------------------------------
    # DEMO PLACEMENT DRIVES
    #
    # These are sample drives for the project UI.
    # They are NOT real company hiring requirements.
    # -------------------------------------------------

    drives = [

        {
            "company_name": "TCS",
            "job_role": "Graduate Engineer Trainee",
            "drive_date": "15 October 2026",
            "location": "Pune",
            "min_cgpa": "6.50",
            "openings": 25,
            "status": "Active",
            "skills": [
                "Python",
                "SQL",
                "Problem Solving",
                "Communication"
            ]
        },

        {
            "company_name": "Infosys",
            "job_role": "Systems Engineer",
            "drive_date": "20 October 2026",
            "location": "Pune",
            "min_cgpa": "6.00",
            "openings": 20,
            "status": "Active",
            "skills": [
                "Java",
                "Python",
                "SQL",
                "Communication"
            ]
        },

        {
            "company_name": "Wipro",
            "job_role": "Project Engineer",
            "drive_date": "25 October 2026",
            "location": "Mumbai",
            "min_cgpa": "6.00",
            "openings": 15,
            "status": "Active",
            "skills": [
                "Python",
                "Java",
                "SQL",
                "Problem Solving"
            ]
        },

        {
            "company_name": "Accenture",
            "job_role": "Associate Software Engineer",
            "drive_date": "30 October 2026",
            "location": "Pune",
            "min_cgpa": "6.50",
            "openings": 30,
            "status": "Active",
            "skills": [
                "Python",
                "SQL",
                "Web Development",
                "Communication"
            ]
        },

        {
            "company_name": "Capgemini",
            "job_role": "Software Engineer",
            "drive_date": "05 November 2026",
            "location": "Pune",
            "min_cgpa": "6.00",
            "openings": 18,
            "status": "Active",
            "skills": [
                "Python",
                "SQL",
                "Problem Solving",
                "Technical Skills"
            ]
        }

    ]


    # -------------------------------------------------
    # TOTAL OPENINGS
    # -------------------------------------------------

    total_openings = sum(
        drive["openings"]
        for drive in drives
    )


    return render_template(
        "tpo/company_drives.html",
        drives=drives,
        total_openings=total_openings
    )


# =====================================================
# PLACEMENT REPORTS
# =====================================================

@tpo_bp.route("/reports")
def reports():

    if not tpo_required():
        flash(
            "TPO access required.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    connection = None

    report = {
        "total_students": 0,
        "total_predictions": 0,
        "placed_predictions": 0,
        "not_placed_predictions": 0,
        "placement_rate": 0
    }

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            # -----------------------------------------
            # TOTAL STUDENTS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM students
            """)

            result = cursor.fetchone()

            report["total_students"] = (
                result["total"] or 0
            )


            # -----------------------------------------
            # TOTAL PREDICTIONS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
            """)

            result = cursor.fetchone()

            report["total_predictions"] = (
                result["total"] or 0
            )


            # -----------------------------------------
            # PLACED PREDICTIONS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
                WHERE prediction = 'Placed'
            """)

            result = cursor.fetchone()

            report["placed_predictions"] = (
                result["total"] or 0
            )


            # -----------------------------------------
            # NOT PLACED PREDICTIONS
            # -----------------------------------------

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
                WHERE prediction = 'Not Placed'
            """)

            result = cursor.fetchone()

            report["not_placed_predictions"] = (
                result["total"] or 0
            )


            # -----------------------------------------
            # PLACEMENT RATE
            # -----------------------------------------

            if report["total_predictions"] > 0:

                report["placement_rate"] = round(
                    (
                        report["placed_predictions"]
                        /
                        report["total_predictions"]
                    ) * 100,
                    2
                )


        return render_template(
            "tpo/placement_reports.html",
            report=report
        )


    except Exception as error:

        print(
            "TPO Placement Reports Error:",
            error
        )

        flash(
            "Unable to load placement reports.",
            "error"
        )

        return redirect(
            url_for("tpo.dashboard")
        )


    finally:

        if connection:
            connection.close()