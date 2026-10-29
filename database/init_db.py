"""Create tables and (optionally) demo data."""
from config import Config
from database.schema import create_schema


def init_database(seed=None):
    """Create/upgrade the schema; seed demo data when enabled. Returns a status dict."""
    added = create_schema()
    seeded = False
    if (Config.SEED_DEMO_DATA if seed is None else seed):
        from database.seed import seed_demo
        seeded = seed_demo()
    bootstrapped = _bootstrap_admin()
    return {"engine": Config.DB_ENGINE, "columns_added": added, "seeded": seeded, "admin_created": bootstrapped}


def _bootstrap_admin():
    """Create an admin from ADMIN_EMAIL / ADMIN_PASSWORD when no admin exists."""
    from database.db import scalar
    from models.user import User
    from utils.validators import password_problem, validate_email

    email, password = Config.BOOTSTRAP_ADMIN_EMAIL.strip().lower(), Config.BOOTSTRAP_ADMIN_PASSWORD
    if not email or not password or scalar("SELECT COUNT(*) FROM users WHERE role = 'admin'"):
        return False
    if not validate_email(email) or password_problem(password):
        print("ADMIN_EMAIL / ADMIN_PASSWORD ignored: invalid email or weak password.")
        return False
    User.create("Administrator", email, password, "admin")
    return True


if __name__ == "__main__":
    print(init_database())
