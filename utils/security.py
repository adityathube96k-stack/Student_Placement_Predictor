"""Password hashing, reset tokens and login throttling."""
import threading
import time

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)


# --- password reset tokens (single use: bound to the current password hash) ---

def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="password-reset")


def make_reset_token(user):
    return _serializer().dumps({"uid": user["id"], "fp": user["password_hash"][-12:]})


def read_reset_token(token, loader):
    """Return the user for a valid token, else None. ``loader(uid)`` fetches the user."""
    try:
        data = _serializer().loads(
            token, max_age=current_app.config["PASSWORD_RESET_MINUTES"] * 60)
    except (BadSignature, SignatureExpired):
        return None
    user = loader(data.get("uid"))
    if not user or user["password_hash"][-12:] != data.get("fp"):
        return None
    return user


# --- login throttling (in-memory; per process) --------------------------------

_attempts = {}
_lock = threading.Lock()


def _key(email, ip):
    return f"{(email or '').lower()}|{ip}"


def login_locked(email, ip):
    """Seconds remaining if locked, else 0."""
    with _lock:
        entry = _attempts.get(_key(email, ip))
        if entry and entry["until"] > time.time():
            return int(entry["until"] - time.time())
    return 0


def register_failure(email, ip):
    cfg = current_app.config
    with _lock:
        entry = _attempts.setdefault(_key(email, ip), {"count": 0, "until": 0})
        if entry["until"] and entry["until"] <= time.time():
            entry.update(count=0, until=0)
        entry["count"] += 1
        if entry["count"] >= cfg["LOGIN_MAX_ATTEMPTS"]:
            entry["until"] = time.time() + cfg["LOGIN_LOCK_MINUTES"] * 60
            entry["count"] = 0


def clear_failures(email, ip):
    with _lock:
        _attempts.pop(_key(email, ip), None)
