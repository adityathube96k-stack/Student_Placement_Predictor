
from flask import Blueprint, request, jsonify, session
from database.db import get_db_connection

student_bp = Blueprint("student", __name__)


# ============================================================
# AUTHENTICATION HELPER
# ============================================================

def require_login():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Authentication required."
        }), 401
    return None


def get_student_profile_id(cursor):
    """Return the logged-in user's student profile ID."""
    cursor.execute(
        "SELECT id FROM student_profiles WHERE user_id = %s",
        (session["user_id"],)
    )
    profile = cursor.fetchone()
    return profile["id"] if profile else None


def database_error_response(message, error):
    print(f"{message}: {error}")
    return jsonify({
        "success": False,
        "message": message
    }), 500


# ============================================================
# PROFILE
# ============================================================

@student_bp.route("/profile", methods=["POST"])
def create_or_update_profile():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    department = data.get("department")

    if not student_id or not department:
        return jsonify({
            "success": False,
            "message": "Student ID and department are required."
        }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id FROM student_profiles WHERE user_id = %s",
            (session["user_id"],)
        )
        existing = cursor.fetchone()

        values = (
            student_id,
            department,
            data.get("year_of_study"),
            data.get("semester"),
            data.get("phone"),
            data.get("date_of_birth") or None,
            data.get("gender"),
        )

        if existing:
            cursor.execute("""
                UPDATE student_profiles
                SET student_id = %s,
                    department = %s,
                    year_of_study = %s,
                    semester = %s,
                    phone = %s,
                    date_of_birth = %s,
                    gender = %s
                WHERE user_id = %s
            """, values + (session["user_id"],))
            message = "Student profile updated successfully."
        else:
            cursor.execute("""
                INSERT INTO student_profiles
                (user_id, student_id, department, year_of_study,
                 semester, phone, date_of_birth, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session["user_id"],) + values)
            message = "Student profile created successfully."

        connection.commit()
        return jsonify({
            "success": True,
            "message": message
        }), 200

    except Exception as e:
        connection.rollback()
        return database_error_response("Profile save failed", e)

    finally:
        cursor.close()
        connection.close()


@student_bp.route("/profile", methods=["GET"])
def get_profile():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT u.id, u.full_name, u.email,
                   sp.student_id, sp.department,
                   sp.year_of_study, sp.semester, sp.phone,
                   sp.date_of_birth, sp.gender
            FROM users u
            LEFT JOIN student_profiles sp ON u.id = sp.user_id
            WHERE u.id = %s
        """, (session["user_id"],))

        profile = cursor.fetchone()

        if not profile:
            return jsonify({
                "success": False,
                "message": "Profile not found."
            }), 404

        return jsonify({
            "success": True,
            "profile": profile
        }), 200

    finally:
        cursor.close()
        connection.close()


# ============================================================
# ACADEMIC RECORDS
# ============================================================

@student_bp.route("/academic", methods=["POST"])
def add_academic_record():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        cgpa = float(data.get("cgpa"))
        attendance = float(data.get("attendance"))
        semester_marks = float(data.get("semester_marks"))
        backlogs = int(data.get("backlogs", 0))
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Academic values must be valid numbers."
        }), 400

    if not 0 <= cgpa <= 10:
        return jsonify({
            "success": False,
            "message": "CGPA must be between 0 and 10."
        }), 400

    if not 0 <= attendance <= 100 or not 0 <= semester_marks <= 100:
        return jsonify({
            "success": False,
            "message": "Attendance and semester marks must be between 0 and 100."
        }), 400

    if backlogs < 0:
        return jsonify({
            "success": False,
            "message": "Backlogs cannot be negative."
        }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute("""
            INSERT INTO academic_records
            (student_id, cgpa, attendance, semester_marks,
             backlogs, academic_year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            student_id, cgpa, attendance, semester_marks,
            backlogs, data.get("academic_year")
        ))

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Academic record saved successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return database_error_response("Academic record save failed", e)

    finally:
        cursor.close()
        connection.close()


@student_bp.route("/academic", methods=["GET"])
def get_academic_records():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ar.id, ar.cgpa, ar.attendance,
                   ar.semester_marks, ar.backlogs,
                   ar.academic_year, ar.created_at
            FROM academic_records ar
            INNER JOIN student_profiles sp ON ar.student_id = sp.id
            WHERE sp.user_id = %s
            ORDER BY ar.created_at DESC
        """, (session["user_id"],))

        return jsonify({
            "success": True,
            "academic_records": cursor.fetchall()
        }), 200

    finally:
        cursor.close()
        connection.close()


# ============================================================
# STUDENT SKILLS
# ============================================================

@student_bp.route("/skills", methods=["POST"])
def save_skills():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        scores = {
            "technical_score": float(data.get("technical_score", 0)),
            "coding_score": float(data.get("coding_score", 0)),
            "aptitude_score": float(data.get("aptitude_score", 0)),
            "communication_score": float(
                data.get("communication_score", 0)
            )
        }
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Skill scores must be valid numbers."
        }), 400

    for name, score in scores.items():
        if not 0 <= score <= 100:
            return jsonify({
                "success": False,
                "message": f"{name} must be between 0 and 100."
            }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute(
            "SELECT id FROM student_skills WHERE student_id = %s",
            (student_id,)
        )
        existing = cursor.fetchone()

        extra_values = (
            data.get("programming_languages"),
            data.get("technical_skills"),
            data.get("soft_skills")
        )

        if existing:
            cursor.execute("""
                UPDATE student_skills
                SET technical_score = %s,
                    coding_score = %s,
                    aptitude_score = %s,
                    communication_score = %s,
                    programming_languages = %s,
                    technical_skills = %s,
                    soft_skills = %s
                WHERE student_id = %s
            """, (
                scores["technical_score"],
                scores["coding_score"],
                scores["aptitude_score"],
                scores["communication_score"],
                *extra_values,
                student_id
            ))
        else:
            cursor.execute("""
                INSERT INTO student_skills
                (student_id, technical_score, coding_score,
                 aptitude_score, communication_score,
                 programming_languages, technical_skills, soft_skills)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                scores["technical_score"],
                scores["coding_score"],
                scores["aptitude_score"],
                scores["communication_score"],
                *extra_values
            ))

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Student skills saved successfully."
        }), 200

    except Exception as e:
        connection.rollback()
        return database_error_response("Skills save failed", e)

    finally:
        cursor.close()
        connection.close()


@student_bp.route("/skills", methods=["GET"])
def get_skills():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ss.id, ss.technical_score, ss.coding_score,
                   ss.aptitude_score, ss.communication_score,
                   ss.programming_languages, ss.technical_skills,
                   ss.soft_skills, ss.created_at, ss.updated_at
            FROM student_skills ss
            INNER JOIN student_profiles sp ON ss.student_id = sp.id
            WHERE sp.user_id = %s
        """, (session["user_id"],))

        return jsonify({
            "success": True,
            "skills": cursor.fetchone()
        }), 200

    finally:
        cursor.close()
        connection.close()


# ============================================================
# CERTIFICATIONS
# ============================================================

@student_bp.route("/certifications", methods=["POST"])
def add_certification():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    if not data.get("certification_name"):
        return jsonify({
            "success": False,
            "message": "Certification name is required."
        }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute("""
            INSERT INTO certifications
            (student_id, certification_name, issuing_organization,
             issue_date, credential_url)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            data.get("certification_name"),
            data.get("issuing_organization"),
            data.get("issue_date") or None,
            data.get("credential_url")
        ))

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Certification added successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return database_error_response("Certification save failed", e)

    finally:
        cursor.close()
        connection.close()


@student_bp.route("/certifications", methods=["GET"])
def get_certifications():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.id, c.certification_name, c.issuing_organization,
                   c.issue_date, c.credential_url, c.created_at
            FROM certifications c
            INNER JOIN student_profiles sp ON c.student_id = sp.id
            WHERE sp.user_id = %s
            ORDER BY c.created_at DESC
        """, (session["user_id"],))

        return jsonify({
            "success": True,
            "certifications": cursor.fetchall()
        }), 200

    finally:
        cursor.close()
        connection.close()


# ============================================================
# PROJECTS
# ============================================================

@student_bp.route("/projects", methods=["POST"])
def add_project():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    if not data.get("project_title"):
        return jsonify({
            "success": False,
            "message": "Project title is required."
        }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute("""
            INSERT INTO projects
            (student_id, project_title, description, technologies,
             project_type, github_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            student_id,
            data.get("project_title"),
            data.get("description"),
            data.get("technologies"),
            data.get("project_type"),
            data.get("github_url")
        ))

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Project added successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return database_error_response("Project save failed", e)

    finally:
        cursor.close()
        connection.close()


@student_bp.route("/projects", methods=["GET"])
def get_projects():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT p.id, p.project_title, p.description, p.technologies,
                   p.project_type, p.github_url, p.created_at
            FROM projects p
            INNER JOIN student_profiles sp ON p.student_id = sp.id
            WHERE sp.user_id = %s
            ORDER BY p.created_at DESC
        """, (session["user_id"],))

        return jsonify({
            "success": True,
            "projects": cursor.fetchall()
        }), 200

    finally:
        cursor.close()
        connection.close()


# ============================================================
# INTERNSHIPS
# ============================================================

@student_bp.route("/internships", methods=["POST"])
def add_internship():
    auth_error = require_login()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    company_name = data.get("company_name")

    if not company_name:
        return jsonify({
            "success": False,
            "message": "Company name is required."
        }), 400

    duration_months = data.get("duration_months")
    if duration_months is not None:
        try:
            duration_months = int(duration_months)
            if duration_months < 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Duration must be a non-negative number."
            }), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute("""
            INSERT INTO internships
            (student_id, company_name, role, duration_months,
             start_date, end_date, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            student_id,
            company_name,
            data.get("role"),
            duration_months,
            data.get("start_date") or None,
            data.get("end_date") or None,
            data.get("description")
        ))

        connection.commit()
        return jsonify({
            "success": True,
            "message": "Internship added successfully."
        }), 201

    except Exception as e:
        connection.rollback()
        return database_error_response("Internship save failed", e)

    finally:
        cursor.close()
        connection.close()


@student_bp.route("/internships", methods=["GET"])
def get_internships():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT i.id, i.company_name, i.role, i.duration_months,
                   i.start_date, i.end_date, i.description, i.created_at
            FROM internships i
            INNER JOIN student_profiles sp ON i.student_id = sp.id
            WHERE sp.user_id = %s
            ORDER BY i.created_at DESC
        """, (session["user_id"],))

        return jsonify({
            "success": True,
            "internships": cursor.fetchall()
        }), 200

    finally:
        cursor.close()
        connection.close()


# ============================================================
# SKILL GAPS
# Return latest record per skill, with deterministic tie-breaking.
# ============================================================

@student_bp.route("/skill-gaps", methods=["GET"])
def get_skill_gaps():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute("""
            SELECT sg.id, sg.skill_name, sg.current_score,
                   sg.target_score, sg.priority, sg.created_at
            FROM skill_gaps sg
            INNER JOIN (
                SELECT skill_name, MAX(id) AS latest_id
                FROM skill_gaps
                WHERE student_id = %s
                GROUP BY skill_name
            ) latest ON sg.id = latest.latest_id
            WHERE sg.student_id = %s
            ORDER BY
                CASE sg.priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END,
                sg.current_score ASC
        """, (student_id, student_id))

        gaps = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(gaps),
            "skill_gaps": gaps
        }), 200

    except Exception as e:
        return database_error_response("Failed to fetch skill gaps", e)

    finally:
        cursor.close()
        connection.close()


# ============================================================
# RECOMMENDATIONS
# Return latest record per category.
# ============================================================

@student_bp.route("/recommendations", methods=["GET"])
def get_recommendations():
    auth_error = require_login()
    if auth_error:
        return auth_error

    connection = get_db_connection()
    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:
        student_id = get_student_profile_id(cursor)

        if not student_id:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        cursor.execute("""
            SELECT r.id, r.category, r.recommendation,
                   r.priority, r.is_completed, r.created_at
            FROM recommendations r
            INNER JOIN (
                SELECT category, MAX(id) AS latest_id
                FROM recommendations
                WHERE student_id = %s
                GROUP BY category
            ) latest ON r.id = latest.latest_id
            WHERE r.student_id = %s
            ORDER BY
                CASE r.priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END,
                r.id DESC
        """, (student_id, student_id))

        recommendations = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations
        }), 200

    except Exception as e:
        return database_error_response(
            "Failed to fetch recommendations", e
        )

    finally:
        cursor.close()
        connection.close()