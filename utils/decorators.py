from functools import wraps

from flask import flash, redirect, request, session, url_for

HOME_BY_ROLE = {"student": "dashboard.dashboard", "admin": "admin.dashboard", "tpo": "tpo.dashboard"}


def home_for(role):
    return url_for(HOME_BY_ROLE.get(role, "auth.login"))


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return function(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            role = session.get("role")
            if role not in allowed_roles:
                flash("You do not have access to that page.", "danger")
                return redirect(home_for(role))
            return function(*args, **kwargs)
        return wrapper
    return decorator


student_required = role_required("student")
admin_required = role_required("admin")
tpo_required = role_required("tpo")
