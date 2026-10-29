from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from database.db import get_db_connection

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")

    if not full_name or not email or not password:
        return jsonify({
            "success": False,
            "message": "All required fields must be provided."
        }), 400

    if role not in ["student", "faculty", "admin"]:
        return jsonify({
            "success": False,
            "message": "Invalid role."
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
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            """,
            (full_name, email, password_hash, role)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful."
        }), 201

    except Exception as e:
        connection.rollback()

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500

    finally:
        cursor.close()
        connection.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
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
            """
            SELECT id, full_name, email, password_hash, role, is_active
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        if not user["is_active"]:
            return jsonify({
                "success": False,
                "message": "Account is inactive."
            }), 403

        if not bcrypt.check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    finally:
        cursor.close()
        connection.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logout successful."
    }), 200