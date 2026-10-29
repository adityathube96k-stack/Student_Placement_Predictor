"""Application configuration.

All settings can be overridden with environment variables (see .env.example).
"""
import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _detect_db_engine():
    """Explicit DB_ENGINE wins; otherwise use MySQL only when it is configured."""
    explicit = os.getenv("DB_ENGINE", "").strip().lower()
    if explicit in {"mysql", "sqlite"}:
        return explicit
    if os.getenv("MYSQL_HOST") or os.getenv("MYSQL_USER"):
        return "mysql"
    return "sqlite"


class Config:
    APP_NAME = "Student Placement Predictor"
    ENV = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")).lower()
    IS_PRODUCTION = ENV == "production"
    DEBUG = _bool("FLASK_DEBUG", False)

    # --- Security -----------------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY") or (
        None if IS_PRODUCTION else "dev-only-secret-change-me"
    )
    if SECRET_KEY is None:  # production without a key: fail safe, not predictable
        SECRET_KEY = secrets.token_hex(32)
        print("WARNING: SECRET_KEY is not set. Using a random key; "
              "sessions will reset on every restart.")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", IS_PRODUCTION)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv("SESSION_HOURS", "12")))
    CSRF_ENABLED = _bool("CSRF_ENABLED", True)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
    LOGIN_LOCK_MINUTES = int(os.getenv("LOGIN_LOCK_MINUTES", "5"))
    PASSWORD_RESET_MINUTES = int(os.getenv("PASSWORD_RESET_MINUTES", "60"))

    # --- Database -----------------------------------------------------------
    DB_ENGINE = _detect_db_engine()
    SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(BASE_DIR, "instance", "placement.db"))
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "placement_predictor")

    # Create tables (and, outside production, demo data) when the app starts.
    AUTO_INIT_DB = _bool("AUTO_INIT_DB", True)
    SEED_DEMO_DATA = _bool("SEED_DEMO_DATA", not IS_PRODUCTION)

    # --- Files --------------------------------------------------------------
    DATASET_DIR = os.path.join(BASE_DIR, "dataset")
    DATASET_UPLOAD_DIR = os.getenv("DATASET_UPLOAD_DIR", os.path.join(BASE_DIR, "dataset", "uploads"))
    # Resumes live outside /static so they are never publicly downloadable.
    RESUME_UPLOAD_DIR = os.getenv("RESUME_UPLOAD_DIR", os.path.join(BASE_DIR, "instance", "resumes"))
    MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "ml", "models"))
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    # --- Email / SMS (optional) --------------------------------------------
    MAIL_ENABLED = _bool("MAIL_ENABLED", False)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "Placement Cell <no-reply@placement.local>")
    SMS_ENABLED = _bool("SMS_ENABLED", False)
    SMS_WEBHOOK_URL = os.getenv("SMS_WEBHOOK_URL", "")
    # When mail is not configured, show reset links on screen (demo/dev only).
    SHOW_RESET_LINK = _bool("SHOW_RESET_LINK", not IS_PRODUCTION)

    # Optional: create this admin on startup when none exists (useful for production).
    BOOTSTRAP_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    BOOTSTRAP_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:5000")


class TestConfig(Config):
    TESTING = True
    CSRF_ENABLED = False
    SECRET_KEY = "test-secret"
    SEED_DEMO_DATA = True
    LOGIN_MAX_ATTEMPTS = 50
