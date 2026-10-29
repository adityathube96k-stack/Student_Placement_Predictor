import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email):
    return bool(email and EMAIL_RE.match(email))


def password_problem(password):
    """Return a human-readable problem, or None when the password is acceptable."""
    if not password or len(password) < 8:
        return "Password must be at least 8 characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must include at least one letter and one number."
    return None


def validate_password(password):
    return password_problem(password) is None


def validate_name(name):
    return bool(name and len(name.strip()) >= 2)


def validate_phone(phone):
    return not phone or bool(re.fullmatch(r"[+\d][\d\s\-]{7,17}", phone))
