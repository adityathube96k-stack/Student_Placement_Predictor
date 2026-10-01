from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from models.user import User
from models.student import Student

from utils.security import verify_password
from utils.validators import (
    validate_email,
    validate_password,
    validate_name
)


# =====================================================
# AUTH BLUEPRINT
# =====================================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =====================================================
# REGISTER
# =====================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Validate name
        if not validate_name(full_name):

            flash(
                "Please enter a valid full name.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # Validate email
        if not validate_email(email):

            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # Validate password
        if not validate_password(password):

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # Confirm password
        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

        # Check existing user
        existing_user = User.find_by_email(email)

        if existing_user:

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        try:

            # Create user
            user_id = User.create(
                full_name,
                email,
                password
            )

            # Create student profile
            Student.create_profile(user_id)

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("auth.login")
            )

        except Exception as error:

            print(
                "Registration Error:",
                error
            )

            flash(
                "Registration failed. Please try again.",
                "danger"
            )

            return redirect(
                url_for("auth.register")
            )

    return render_template(
        "auth/register.html"
    )


# =====================================================
# LOGIN
# =====================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # Validate fields
        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # Find user
        user = User.find_by_email(email)

        if not user:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # Check account status
        if not user["is_active"]:

            flash(
                "Your account has been disabled.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # Verify password
        if not verify_password(
            password,
            user["password_hash"]
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # Create session
        session.clear()

        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        flash(
            "Login successful.",
            "success"
        )

        # =================================================
        # ROLE BASED REDIRECT
        # =================================================

        if user["role"] == "admin":

            return redirect(
                "/admin/dashboard"
            )

        if user["role"] == "tpo":

            return redirect(
                "/tpo/dashboard"
            )

        # Student
        return redirect(
            url_for(
                "dashboard.dashboard"
            )
        )

    # =================================================
    # IMPORTANT:
    # This handles GET /auth/login
    # =================================================

    return render_template(
        "auth/login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )


# =====================================================
# FORGOT PASSWORD
# =====================================================

@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not validate_email(email):

            flash(
                "Please enter a valid email.",
                "danger"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        user = User.find_by_email(email)

        # Don't reveal whether email exists
        flash(
            "If an account exists for this email, password reset instructions will be provided.",
            "info"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/forgot_password.html"
    )