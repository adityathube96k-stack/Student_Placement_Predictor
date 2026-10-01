import re


def validate_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(
        re.match(pattern, email)
    )


def validate_password(password):

    if not password:
        return False

    if len(password) < 6:
        return False

    return True


def validate_name(name):

    if not name:
        return False

    if len(name.strip()) < 2:
        return False

    return True