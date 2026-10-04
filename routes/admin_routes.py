from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.utils import secure_filename

from database.db import get_connection

import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

import joblib


# =====================================================
# ADMIN BLUEPRINT
# =====================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# =====================================================
# ADMIN ACCESS CHECK
# =====================================================

def admin_required():
    """
    Check whether the currently logged-in user is an admin.
    """

    if "user_id" not in session:
        return False

    if session.get("role") != "admin":
        return False

    return True


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@admin_bp.route("/dashboard")
def dashboard():

    if not admin_required():
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))

    connection = None

    stats = {
        "total_users": 0,
        "total_students": 0,
        "total_companies": 5,
        "total_predictions": 0,
        "total_interviews": 0
    }

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            # =================================================
            # TOTAL USERS
            # =================================================

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM users
            """)

            result = cursor.fetchone()

            stats["total_users"] = result["total"] or 0


            # =================================================
            # TOTAL STUDENTS
            # =================================================

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM students
            """)

            result = cursor.fetchone()

            stats["total_students"] = result["total"] or 0


            # =================================================
            # TOTAL PREDICTIONS
            # =================================================

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM prediction_history
            """)

            result = cursor.fetchone()

            stats["total_predictions"] = result["total"] or 0


            # =================================================
            # TOTAL INTERVIEWS
            # =================================================

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM interview_history
            """)

            result = cursor.fetchone()

            stats["total_interviews"] = result["total"] or 0


        return render_template(
            "admin/admin_dashboard.html",
            stats=stats
        )


    except Exception as error:

        print("Admin Dashboard Error:", error)

        flash(
            "Unable to load admin dashboard.",
            "error"
        )

        return render_template(
            "admin/admin_dashboard.html",
            stats=stats
        )


    finally:

        if connection:
            connection.close()


# =====================================================
# MANAGE STUDENTS
# =====================================================

@admin_bp.route("/students")
def manage_students():

    if not admin_required():
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))

    connection = None

    students = []

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    u.id,
                    u.full_name,
                    u.email,
                    u.role,
                    u.is_active,
                    s.enrollment_no,
                    s.branch,
                    s.year,
                    s.cgpa,
                    s.attendance,
                    s.aptitude_score,
                    s.coding_score,
                    s.communication_score,
                    s.technical_score
                FROM users u
                LEFT JOIN students s
                    ON u.id = s.user_id
                WHERE u.role = 'student'
                ORDER BY u.id DESC
            """)

            students = cursor.fetchall()


        return render_template(
            "admin/manage_students.html",
            students=students
        )


    except Exception as error:

        print("Manage Students Error:", error)

        flash(
            "Unable to load students.",
            "error"
        )

        return render_template(
            "admin/manage_students.html",
            students=[]
        )


    finally:

        if connection:
            connection.close()


# =====================================================
# MANAGE COMPANIES
# =====================================================

@admin_bp.route("/companies")
def manage_companies():

    if not admin_required():
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))

    return render_template(
        "admin/manage_companies.html"
    )


# =====================================================
# UPLOAD DATASET
# =====================================================

@admin_bp.route(
    "/upload-dataset",
    methods=["GET", "POST"]
)
def upload_dataset():

    if not admin_required():
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))


    if request.method == "POST":

        file = request.files.get("dataset")


        if not file or file.filename == "":
            flash(
                "Please select a CSV file.",
                "error"
            )

            return redirect(
                url_for("admin.upload_dataset")
            )


        if not file.filename.lower().endswith(".csv"):

            flash(
                "Only CSV files are allowed.",
                "error"
            )

            return redirect(
                url_for("admin.upload_dataset")
            )


        try:

            upload_folder = os.path.join(
                "dataset",
                "uploads"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            filename = secure_filename(
                file.filename
            )


            file_path = os.path.join(
                upload_folder,
                filename
            )


            file.save(file_path)


            dataframe = pd.read_csv(
                file_path
            )


            required_columns = [
                "cgpa",
                "attendance",
                "aptitude_score",
                "coding_score",
                "communication_score",
                "technical_score",
                "placed"
            ]


            missing_columns = [
                column
                for column in required_columns
                if column not in dataframe.columns
            ]


            if missing_columns:

                os.remove(file_path)

                flash(
                    "Missing required columns: "
                    + ", ".join(missing_columns),
                    "error"
                )

                return redirect(
                    url_for("admin.upload_dataset")
                )


            flash(
                f"Dataset uploaded successfully. "
                f"{len(dataframe)} records found.",
                "success"
            )

            return redirect(
                url_for("admin.upload_dataset")
            )


        except Exception as error:

            print(
                "Dataset Upload Error:",
                error
            )

            flash(
                "Dataset upload failed.",
                "error"
            )

            return redirect(
                url_for("admin.upload_dataset")
            )


    return render_template(
        "admin/upload_dataset.html"
    )


# =====================================================
# MODEL TRAINING
# =====================================================

@admin_bp.route(
    "/model-training",
    methods=["GET", "POST"]
)
def model_training():

    if not admin_required():
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))


    training_result = None


    if request.method == "POST":

        try:

            dataset_path = os.path.join(
                "dataset",
                "placement_dataset.csv"
            )


            if not os.path.exists(dataset_path):

                flash(
                    "Placement dataset not found.",
                    "error"
                )

                return redirect(
                    url_for("admin.model_training")
                )


            dataframe = pd.read_csv(
                dataset_path
            )


            required_columns = [
                "cgpa",
                "attendance",
                "aptitude_score",
                "coding_score",
                "communication_score",
                "technical_score",
                "placed"
            ]


            missing_columns = [
                column
                for column in required_columns
                if column not in dataframe.columns
            ]


            if missing_columns:

                flash(
                    "Missing dataset columns: "
                    + ", ".join(missing_columns),
                    "error"
                )

                return redirect(
                    url_for("admin.model_training")
                )


            features = [
                "cgpa",
                "attendance",
                "aptitude_score",
                "coding_score",
                "communication_score",
                "technical_score"
            ]


            X = dataframe[features]

            y = dataframe["placed"]


            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.20,
                random_state=42,
                stratify=y
            )


            scaler = StandardScaler()


            X_train_scaled = scaler.fit_transform(
                X_train
            )


            X_test_scaled = scaler.transform(
                X_test
            )


            model = LogisticRegression(
                max_iter=1000
            )


            model.fit(
                X_train_scaled,
                y_train
            )


            predictions = model.predict(
                X_test_scaled
            )


            accuracy = accuracy_score(
                y_test,
                predictions
            )


            os.makedirs(
                "ml",
                exist_ok=True
            )


            joblib.dump(
                model,
                os.path.join(
                    "ml",
                    "placement_model.pkl"
                )
            )


            joblib.dump(
                scaler,
                os.path.join(
                    "ml",
                    "scaler.pkl"
                )
            )


            training_result = {

                "accuracy": round(
                    accuracy * 100,
                    2
                ),

                "total_records": len(dataframe),

                "training_records": len(X_train),

                "testing_records": len(X_test)
            }


            flash(
                "Model trained successfully.",
                "success"
            )


        except Exception as error:

            print(
                "Model Training Error:",
                error
            )

            flash(
                "Model training failed.",
                "error"
            )


    return render_template(
        "admin/model_training.html",
        training_result=training_result
    )


# =====================================================
# ADMIN ANALYTICS
# =====================================================

@admin_bp.route("/analytics")
def analytics():

    if not admin_required():
        flash("Admin access required.", "error")
        return redirect(url_for("auth.login"))

    connection = None


    analytics_data = {

        "total_students": 0,

        "average_cgpa": 0,

        "average_attendance": 0,

        "average_aptitude": 0,

        "average_coding": 0,

        "average_communication": 0,

        "average_technical": 0,

        "prediction_count": 0,

        "placed_count": 0,

        "not_placed_count": 0,

        "placement_rate": 0,

        "excellent_count": 0,

        "good_count": 0,

        "moderate_count": 0
    }


    try:

        connection = get_connection()

        with connection.cursor() as cursor:


            # =================================================
            # STUDENT PERFORMANCE
            # =================================================

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_students,

                    AVG(cgpa)
                        AS average_cgpa,

                    AVG(attendance)
                        AS average_attendance,

                    AVG(aptitude_score)
                        AS average_aptitude,

                    AVG(coding_score)
                        AS average_coding,

                    AVG(communication_score)
                        AS average_communication,

                    AVG(technical_score)
                        AS average_technical

                FROM students

                WHERE
                    cgpa IS NOT NULL
                    AND attendance IS NOT NULL
            """)


            result = cursor.fetchone()


            if result:

                analytics_data[
                    "total_students"
                ] = result[
                    "total_students"
                ] or 0


                analytics_data[
                    "average_cgpa"
                ] = float(
                    result[
                        "average_cgpa"
                    ] or 0
                )


                analytics_data[
                    "average_attendance"
                ] = float(
                    result[
                        "average_attendance"
                    ] or 0
                )


                analytics_data[
                    "average_aptitude"
                ] = float(
                    result[
                        "average_aptitude"
                    ] or 0
                )


                analytics_data[
                    "average_coding"
                ] = float(
                    result[
                        "average_coding"
                    ] or 0
                )


                analytics_data[
                    "average_communication"
                ] = float(
                    result[
                        "average_communication"
                    ] or 0
                )


                analytics_data[
                    "average_technical"
                ] = float(
                    result[
                        "average_technical"
                    ] or 0
                )


            # =================================================
            # PREDICTION ANALYTICS
            # =================================================

            cursor.execute("""
                SELECT
                    COUNT(*) AS total_predictions,

                    SUM(
                        CASE
                            WHEN prediction = 'Placed'
                            THEN 1
                            ELSE 0
                        END
                    ) AS placed_count,

                    SUM(
                        CASE
                            WHEN prediction = 'Not Placed'
                            THEN 1
                            ELSE 0
                        END
                    ) AS not_placed_count

                FROM prediction_history
            """)


            result = cursor.fetchone()


            if result:

                total_predictions = (
                    result[
                        "total_predictions"
                    ] or 0
                )


                placed_count = (
                    result[
                        "placed_count"
                    ] or 0
                )


                not_placed_count = (
                    result[
                        "not_placed_count"
                    ] or 0
                )


                analytics_data[
                    "prediction_count"
                ] = total_predictions


                analytics_data[
                    "placed_count"
                ] = placed_count


                analytics_data[
                    "not_placed_count"
                ] = not_placed_count


                if total_predictions > 0:

                    analytics_data[
                        "placement_rate"
                    ] = (
                        placed_count
                        / total_predictions
                    ) * 100


            # =================================================
            # READINESS ANALYTICS
            # =================================================

            cursor.execute("""
                SELECT
                    SUM(
                        CASE
                            WHEN readiness_level = 'Excellent'
                            THEN 1
                            ELSE 0
                        END
                    ) AS excellent_count,

                    SUM(
                        CASE
                            WHEN readiness_level = 'Good'
                            THEN 1
                            ELSE 0
                        END
                    ) AS good_count,

                    SUM(
                        CASE
                            WHEN readiness_level = 'Moderate'
                            THEN 1
                            ELSE 0
                        END
                    ) AS moderate_count

                FROM readiness_history
            """)


            result = cursor.fetchone()


            if result:

                analytics_data[
                    "excellent_count"
                ] = (
                    result[
                        "excellent_count"
                    ] or 0
                )


                analytics_data[
                    "good_count"
                ] = (
                    result[
                        "good_count"
                    ] or 0
                )


                analytics_data[
                    "moderate_count"
                ] = (
                    result[
                        "moderate_count"
                    ] or 0
                )


        return render_template(
            "admin/analytics.html",
            **analytics_data
        )


    except Exception as error:

        print(
            "Analytics Error:",
            error
        )

        flash(
            "Unable to load analytics.",
            "error"
        )

        return render_template(
            "admin/analytics.html",
            **analytics_data
        )


    finally:

        if connection:
            connection.close()