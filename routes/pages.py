from flask import Blueprint, render_template, session, redirect, url_for

pages_bp = Blueprint("pages", __name__)


# =========================================================
# Home Page
# =========================================================
@pages_bp.route("/")
def home():
    return render_template("index.html")


# =========================================================
# Login Page
# =========================================================
@pages_bp.route("/login")
def login_page():
    return render_template("login.html")


# =========================================================
# Register Page
# =========================================================
@pages_bp.route("/register")
def register_page():
    return render_template("register.html")


# =========================================================
# Student Dashboard
# =========================================================
@pages_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("pages.login_page"))

    return render_template("student/dashboard.html")


# =========================================================
# Student Profile
# =========================================================
@pages_bp.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("pages.login_page"))

    return render_template("student/profile.html")


# =========================================================
# Prediction
# =========================================================
@pages_bp.route("/prediction")
def prediction():
    if "user_id" not in session:
        return redirect(url_for("pages.login_page"))

    return render_template("student/prediction.html")


# =========================================================
# Skill Gaps
# =========================================================
@pages_bp.route("/skill-gaps")
def skill_gaps():
    if "user_id" not in session:
        return redirect(url_for("pages.login_page"))

    return render_template("student/skill_gaps.html")


# =========================================================
# Recommendations
# =========================================================
@pages_bp.route("/recommendations")
def recommendations():
    if "user_id" not in session:
        return redirect(url_for("pages.login_page"))

    return render_template("student/recommendations.html")


# =========================================================
# Prediction History
# =========================================================
@pages_bp.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("pages.login_page"))

    return render_template("student/history.html")