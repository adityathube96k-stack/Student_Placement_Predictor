from flask import (Blueprint, current_app, flash, redirect, render_template, request,
                   session, url_for)

from models.student import Student
from models.user import User
from notifications.email_service import send_email
from notifications.service import notify
from notifications.templates import render
from utils.decorators import home_for
from utils.helpers import safe_redirect_target
from utils.logger import log
from utils.security import (clear_failures, login_locked, make_reset_token, read_reset_token,
                            register_failure, verify_password)
from utils.validators import password_problem, validate_email, validate_name

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(home_for(session.get("role")))
    form = request.form
    if request.method == "POST":
        name = form.get("full_name", "").strip()
        email = form.get("email", "").strip().lower()
        password, confirm = form.get("password", ""), form.get("confirm_password", "")
        error = None
        if not validate_name(name):
            error = "Please enter your full name."
        elif not validate_email(email):
            error = "Please enter a valid email address."
        elif password_problem(password):
            error = password_problem(password)
        elif password != confirm:
            error = "Passwords do not match."
        elif User.find_by_email(email):
            error = "An account with this email already exists."
        if error:
            flash(error, "danger")
            return render_template("auth/register.html", form=form), 400
        try:
            user_id = User.create(name, email, password)
            Student.create_profile(user_id)
        except Exception as exc:  # noqa: BLE001
            log.error("Registration failed: %s", exc)
            flash("We could not create your account. Please try again.", "danger")
            return render_template("auth/register.html", form=form), 500
        notify(user_id, "welcome", "info", "/student/profile", name=name.split()[0])
        flash("Account created. Sign in to get started.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(home_for(session.get("role")))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        ip = request.remote_addr or "?"
        wait = login_locked(email, ip)
        if wait:
            flash(f"Too many failed attempts. Try again in {max(wait // 60, 1)} minute(s).", "danger")
            return render_template("auth/login.html", email=email), 429
        user = User.find_by_email(email) if validate_email(email) else None
        if not user or not verify_password(password, user["password_hash"]):
            register_failure(email, ip)
            flash("Incorrect email or password.", "danger")
            return render_template("auth/login.html", email=email), 401
        if not user["is_active"]:
            flash("This account has been deactivated. Contact the placement cell.", "danger")
            return render_template("auth/login.html", email=email), 403
        clear_failures(email, ip)
        session.clear()
        session.update(user_id=user["id"], role=user["role"], full_name=user["full_name"],
                       email=user["email"])
        User.touch_login(user["id"])
        flash(f"Welcome back, {user['full_name'].split()[0]}.", "success")
        return redirect(safe_redirect_target(request.args.get("next"), home_for(user["role"])))
    return render_template("auth/login.html", email="")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    dev_link = None
    sent = False
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not validate_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("auth/forgot_password.html"), 400
        sent = True
        user = User.find_by_email(email)
        if user and user["is_active"]:
            link = url_for("auth.reset_password", token=make_reset_token(user), _external=True)
            subject, body = render("reset", name=user["full_name"].split()[0], link=link,
                                   minutes=current_app.config["PASSWORD_RESET_MINUTES"])
            delivered = send_email(user["email"], subject, body)
            if not delivered and current_app.config["SHOW_RESET_LINK"]:
                dev_link = link  # email is not configured: surface the link (dev/demo only)
    return render_template("auth/forgot_password.html", sent=sent, dev_link=dev_link)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = read_reset_token(token, User.find_by_id)
    if not user:
        flash("This reset link is invalid or has expired. Request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password, confirm = request.form.get("password", ""), request.form.get("confirm_password", "")
        problem = password_problem(password) or (None if password == confirm else "Passwords do not match.")
        if problem:
            flash(problem, "danger")
            return render_template("auth/reset_password.html", token=token), 400
        User.set_password(user["id"], password)
        flash("Password updated. Sign in with your new password.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", token=token)
