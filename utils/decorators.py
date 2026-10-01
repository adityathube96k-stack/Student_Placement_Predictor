from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    flash
)


def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login to continue.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        return function(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:

                flash(
                    "Please login to continue.",
                    "warning"
                )

                return redirect(
                    url_for("auth.login")
                )

            user_role = session.get("role")

            if user_role not in allowed_roles:

                flash(
                    "You are not authorized to access this page.",
                    "danger"
                )

                return redirect(
                    url_for("dashboard.dashboard")
                )

            return function(*args, **kwargs)

        return wrapper

    return decorator