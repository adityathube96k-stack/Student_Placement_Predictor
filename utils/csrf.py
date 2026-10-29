"""Minimal CSRF protection (synchroniser token stored in the session)."""
import hmac
import secrets

from flask import abort, current_app, request, session

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def protect():
    """Call from before_request."""
    if not current_app.config.get("CSRF_ENABLED", True) or request.method in SAFE_METHODS:
        return
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRFToken", "")
    expected = session.get("_csrf", "")
    if not expected or not hmac.compare_digest(sent, expected):
        abort(400, description="Your session expired. Reload the page and try again.")
