from flask import Blueprint, request, jsonify, session

from ml.predict import predict_placement
from utils.helpers import calculate_employability_score
from utils.validators import validate_student_scores, detect_skill_gaps
from utils.recommendations import generate_recommendations
from database.db import get_db_connection


prediction_bp = Blueprint("prediction", __name__)


# =========================================================
# Generate Prediction
# =========================================================

@prediction_bp.route("/predict", methods=["POST"])
def predict():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request data is required."
        }), 400

    required_fields = [
        "cgpa",
        "attendance",
        "technical_score",
        "coding_score",
        "aptitude_score",
        "communication_score",
        "certifications_count",
        "projects_count",
        "internships_count"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"Missing field: {field}"
            }), 400

    connection = None
    cursor = None

    try:

        # Convert input values
        cgpa = float(data["cgpa"])
        attendance = float(data["attendance"])
        technical_score = float(data["technical_score"])
        coding_score = float(data["coding_score"])
        aptitude_score = float(data["aptitude_score"])
        communication_score = float(data["communication_score"])

        certifications_count = int(data["certifications_count"])
        projects_count = int(data["projects_count"])
        internships_count = int(data["internships_count"])

        # Validate scores
        validation_errors = validate_student_scores(
            cgpa,
            attendance,
            technical_score,
            coding_score,
            aptitude_score,
            communication_score
        )

        if validation_errors:
            return jsonify({
                "success": False,
                "message": "Invalid student data.",
                "errors": validation_errors
            }), 400

        # 1. ML prediction
        placement_result = predict_placement(
            cgpa=cgpa,
            attendance=attendance,
            technical_score=technical_score,
            coding_score=coding_score,
            aptitude_score=aptitude_score,
            communication_score=communication_score,
            certifications_count=certifications_count,
            projects_count=projects_count,
            internships_count=internships_count
        )

        # 2. Employability score
        employability_score = calculate_employability_score(
            cgpa=cgpa,
            attendance=attendance,
            technical_score=technical_score,
            coding_score=coding_score,
            aptitude_score=aptitude_score,
            communication_score=communication_score,
            certifications_count=certifications_count,
            projects_count=projects_count,
            internships_count=internships_count
        )

        # 3. Skill gaps
        skill_gaps = detect_skill_gaps(
            technical_score=technical_score,
            coding_score=coding_score,
            aptitude_score=aptitude_score,
            communication_score=communication_score
        )

        # 4. Recommendations
        recommendations = generate_recommendations(skill_gaps)

        # 5. Database connection
        connection = get_db_connection()

        if not connection:
            return jsonify({
                "success": False,
                "message": "Database connection failed."
            }), 500

        cursor = connection.cursor(dictionary=True)

        # 6. Get student profile
        cursor.execute(
            """
            SELECT id
            FROM student_profiles
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "success": False,
                "message": "Student profile not found. Please create your profile first."
            }), 404

        student_id = student["id"]

        # 7. Save prediction
        cursor.execute(
            """
            INSERT INTO predictions
            (
                student_id,
                performance_prediction,
                placement_probability,
                employability_score,
                prediction_label,
                model_name,
                model_version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                student_id,
                placement_result["prediction"],
                placement_result["placement_probability"],
                employability_score,
                placement_result["label"],
                "Logistic Regression",
                "1.0"
            )
        )

        prediction_id = cursor.lastrowid

        # 8. Save skill gaps
        for gap in skill_gaps:

            cursor.execute(
                """
                INSERT INTO skill_gaps
                (
                    student_id,
                    skill_name,
                    current_score,
                    target_score,
                    priority
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    student_id,
                    gap["skill"],
                    gap["current_score"],
                    gap["target_score"],
                    gap["priority"]
                )
            )

        # 9. Save recommendations
        for recommendation in recommendations:

            cursor.execute(
                """
                INSERT INTO recommendations
                (
                    student_id,
                    category,
                    recommendation,
                    priority
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    student_id,
                    recommendation["category"],
                    recommendation["recommendation"],
                    recommendation["priority"]
                )
            )

        # 10. Save prediction history
        cursor.execute(
            """
            INSERT INTO prediction_history
            (
                student_id,
                placement_probability,
                employability_score,
                performance_prediction,
                model_name,
                model_version
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                student_id,
                placement_result["placement_probability"],
                employability_score,
                placement_result["prediction"],
                "Logistic Regression",
                "1.0"
            )
        )

        # Commit everything together
        connection.commit()

        return jsonify({
            "success": True,
            "message": "Student prediction generated and saved successfully.",

            "prediction_id": prediction_id,

            "prediction": {
                "placement_prediction": placement_result["prediction"],
                "placement_probability": placement_result["placement_probability"],
                "label": placement_result["label"]
            },

            "employability_score": employability_score,

            "skill_gaps": skill_gaps,

            "recommendations": recommendations

        }), 200

    except (ValueError, TypeError):

        if connection:
            connection.rollback()

        return jsonify({
            "success": False,
            "message": "Invalid input values."
        }), 400

    except Exception as e:

        if connection:
            connection.rollback()

        print("Prediction error:", e)

        return jsonify({
            "success": False,
            "message": "Prediction failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# Prediction History
# =========================================================

@prediction_bp.route("/history", methods=["GET"])
def prediction_history():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    connection = get_db_connection()

    if not connection:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = connection.cursor(dictionary=True)

    try:

        # Find student's profile
        cursor.execute(
            """
            SELECT id
            FROM student_profiles
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "success": False,
                "message": "Student profile not found."
            }), 404

        student_id = student["id"]

        # Get prediction history
        cursor.execute(
            """
            SELECT
                id,
                performance_prediction,
                placement_probability,
                employability_score,
                prediction_label,
                model_name,
                model_version,
                created_at
            FROM predictions
            WHERE student_id = %s
            ORDER BY created_at DESC
            """,
            (student_id,)
        )

        predictions = cursor.fetchall()

        return jsonify({
            "success": True,
            "count": len(predictions),
            "history": predictions
        }), 200

    except Exception as e:

        print("Prediction history error:", e)

        return jsonify({
            "success": False,
            "message": "Failed to fetch prediction history."
        }), 500

    finally:

        cursor.close()
        connection.close()