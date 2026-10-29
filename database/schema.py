"""Single source of truth for the database schema (MySQL + SQLite)."""
import re

from config import Config
from database.db import get_connection, is_sqlite

D = "DECIMAL"
SCORES = [
    ("aptitude_score", f"{D}(5,2)"),
    ("coding_score", f"{D}(5,2)"),
    ("communication_score", f"{D}(5,2)"),
    ("technical_score", f"{D}(5,2)"),
]


def _scores():
    return list(SCORES)


TABLES = [
    ("users", [
        ("id", "{PK}"),
        ("full_name", "VARCHAR(100) NOT NULL"),
        ("email", "VARCHAR(150) NOT NULL UNIQUE"),
        ("password_hash", "VARCHAR(255) NOT NULL"),
        ("role", "VARCHAR(20) NOT NULL DEFAULT 'student'"),
        ("is_active", "BOOLEAN NOT NULL DEFAULT 1"),
        ("last_login_at", "TIMESTAMP NULL DEFAULT NULL"),
        ("created_at", "{TS}"),
        ("updated_at", "{TS_UPD}"),
    ], []),
    ("students", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL UNIQUE"),
        ("enrollment_no", "VARCHAR(50) UNIQUE"),
        ("phone", "VARCHAR(20)"),
        ("branch", "VARCHAR(100)"),
        ("year", "VARCHAR(20)"),
        ("cgpa", f"{D}(4,2)"),
        ("attendance", f"{D}(5,2)"),
        ("backlogs", "INT NOT NULL DEFAULT 0"),
        *_scores(),
        ("projects", "INT NOT NULL DEFAULT 0"),
        ("internships", "INT NOT NULL DEFAULT 0"),
        ("certifications", "INT NOT NULL DEFAULT 0"),
        ("skills", "TEXT"),
        ("placement_status", "VARCHAR(30) NOT NULL DEFAULT 'Not Placed'"),
        ("placed_company", "VARCHAR(150)"),
        ("package_lpa", f"{D}(6,2)"),
        ("created_at", "{TS}"),
        ("updated_at", "{TS_UPD}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("prediction_history", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("cgpa", f"{D}(4,2)"),
        ("attendance", f"{D}(5,2)"),
        *_scores(),
        ("projects", "INT"),
        ("internships", "INT"),
        ("certifications", "INT"),
        ("prediction", "VARCHAR(50)"),
        ("placement_probability", f"{D}(5,2)"),
        ("not_placed_probability", f"{D}(5,2)"),
        ("model_version", "VARCHAR(40)"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("readiness_history", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("cgpa", f"{D}(4,2)"),
        ("attendance", f"{D}(5,2)"),
        *_scores(),
        ("readiness_score", f"{D}(5,2)"),
        ("readiness_level", "VARCHAR(100)"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("skill_gap_history", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("cgpa", f"{D}(4,2)"),
        ("attendance", f"{D}(5,2)"),
        *_scores(),
        ("total_gap", f"{D}(6,2)"),
        ("overall_status", "VARCHAR(100)"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("interview_history", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("category", "VARCHAR(50)"),
        ("total_questions", "INT"),
        ("interview_score", f"{D}(5,2)"),
        ("performance_level", "VARCHAR(50)"),
        ("details", "TEXT"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("companies", [
        ("id", "{PK}"),
        ("name", "VARCHAR(150) NOT NULL UNIQUE"),
        ("industry", "VARCHAR(100)"),
        ("location", "VARCHAR(150)"),
        ("website", "VARCHAR(200)"),
        ("description", "TEXT"),
        ("min_cgpa", f"{D}(4,2) NOT NULL DEFAULT 0"),
        ("min_attendance", f"{D}(5,2) NOT NULL DEFAULT 0"),
        ("min_aptitude", f"{D}(5,2) NOT NULL DEFAULT 0"),
        ("min_coding", f"{D}(5,2) NOT NULL DEFAULT 0"),
        ("min_communication", f"{D}(5,2) NOT NULL DEFAULT 0"),
        ("min_technical", f"{D}(5,2) NOT NULL DEFAULT 0"),
        ("max_backlogs", "INT NOT NULL DEFAULT 0"),
        ("required_skills", "TEXT"),
        ("package_lpa", f"{D}(6,2)"),
        ("is_active", "BOOLEAN NOT NULL DEFAULT 1"),
        ("created_at", "{TS}"),
        ("updated_at", "{TS_UPD}"),
    ], []),
    ("company_eligibility_history", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("company_name", "VARCHAR(150)"),
        ("eligible", "BOOLEAN NOT NULL DEFAULT 0"),
        ("missing_requirements", "TEXT"),
        ("missing_skills", "TEXT"),
        ("checked_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("drives", [
        ("id", "{PK}"),
        ("company_id", "INT NOT NULL"),
        ("job_role", "VARCHAR(150) NOT NULL"),
        ("drive_date", "DATE"),
        ("location", "VARCHAR(150)"),
        ("openings", "INT NOT NULL DEFAULT 1"),
        ("package_lpa", f"{D}(6,2)"),
        ("status", "VARCHAR(20) NOT NULL DEFAULT 'Upcoming'"),
        ("description", "TEXT"),
        ("created_by", "INT"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE"]),
    ("drive_applications", [
        ("id", "{PK}"),
        ("drive_id", "INT NOT NULL"),
        ("user_id", "INT NOT NULL"),
        ("status", "VARCHAR(20) NOT NULL DEFAULT 'Applied'"),
        ("applied_at", "{TS}"),
        ("updated_at", "{TS_UPD}"),
    ], ["FOREIGN KEY (drive_id) REFERENCES drives(id) ON DELETE CASCADE",
        "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE",
        "UNIQUE (drive_id, user_id)"]),
    ("resume_analysis", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("original_filename", "VARCHAR(255)"),
        ("stored_filename", "VARCHAR(255)"),
        ("file_size", "INT"),
        ("word_count", "INT"),
        ("overall_score", f"{D}(5,2)"),
        ("rating", "VARCHAR(50)"),
        ("section_score", f"{D}(5,2)"),
        ("skill_score", f"{D}(5,2)"),
        ("length_score", f"{D}(5,2)"),
        ("skills_json", "TEXT"),
        ("sections_json", "TEXT"),
        ("recommendations_json", "TEXT"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("notifications", [
        ("id", "{PK}"),
        ("user_id", "INT NOT NULL"),
        ("title", "VARCHAR(150) NOT NULL"),
        ("message", "TEXT"),
        ("category", "VARCHAR(30) NOT NULL DEFAULT 'info'"),
        ("link", "VARCHAR(255)"),
        ("is_read", "BOOLEAN NOT NULL DEFAULT 0"),
        ("created_at", "{TS}"),
    ], ["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"]),
    ("datasets", [
        ("id", "{PK}"),
        ("filename", "VARCHAR(255) NOT NULL"),
        ("original_name", "VARCHAR(255)"),
        ("rows_count", "INT"),
        ("placed_count", "INT"),
        ("extra_features", "VARCHAR(255)"),
        ("uploaded_by", "INT"),
        ("use_for_training", "BOOLEAN NOT NULL DEFAULT 1"),
        ("created_at", "{TS}"),
    ], []),
    ("model_versions", [
        ("id", "{PK}"),
        ("version", "VARCHAR(40) NOT NULL"),
        ("algorithm", "VARCHAR(80)"),
        ("accuracy", f"{D}(6,2)"),
        ("precision_score", f"{D}(6,2)"),
        ("recall_score", f"{D}(6,2)"),
        ("f1_score", f"{D}(6,2)"),
        ("roc_auc", f"{D}(6,2)"),
        ("train_rows", "INT"),
        ("test_rows", "INT"),
        ("features", "VARCHAR(255)"),
        ("is_active", "BOOLEAN NOT NULL DEFAULT 0"),
        ("trained_by", "INT"),
        ("created_at", "{TS}"),
    ], []),
    ("contact_messages", [
        ("id", "{PK}"),
        ("name", "VARCHAR(100) NOT NULL"),
        ("email", "VARCHAR(150) NOT NULL"),
        ("subject", "VARCHAR(150)"),
        ("message", "TEXT NOT NULL"),
        ("created_at", "{TS}"),
    ], []),
    ("report_log", [
        ("id", "{PK}"),
        ("user_id", "INT"),
        ("report_type", "VARCHAR(60)"),
        ("file_format", "VARCHAR(10)"),
        ("created_at", "{TS}"),
    ], []),
]

INDEXES = [
    ("idx_students_branch", "students", "branch"),
    ("idx_pred_user_created", "prediction_history", "user_id, created_at"),
    ("idx_ready_user_created", "readiness_history", "user_id, created_at"),
    ("idx_gap_user_created", "skill_gap_history", "user_id, created_at"),
    ("idx_interview_user_created", "interview_history", "user_id, created_at"),
    ("idx_elig_user", "company_eligibility_history", "user_id, checked_at"),
    ("idx_drives_status", "drives", "status, drive_date"),
    ("idx_apps_user", "drive_applications", "user_id"),
    ("idx_resume_user", "resume_analysis", "user_id, created_at"),
    ("idx_notif_user", "notifications", "user_id, is_read"),
]


def _render(defn, sqlite):
    tokens = {
        "{PK}": "INTEGER PRIMARY KEY AUTOINCREMENT" if sqlite else "INT AUTO_INCREMENT PRIMARY KEY",
        "{TS}": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "{TS_UPD}": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        if sqlite else "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    }
    for key, value in tokens.items():
        defn = defn.replace(key, value)
    if sqlite:
        defn = re.sub(r"DECIMAL\(\d+,\s*\d+\)", "REAL", defn)
    return defn


def create_statements(sqlite):
    suffix = "" if sqlite else " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    statements = []
    for name, columns, constraints in TABLES:
        parts = [f"    {col} {_render(defn, sqlite)}" for col, defn in columns]
        parts += [f"    {c}" for c in constraints]
        statements.append(f"CREATE TABLE IF NOT EXISTS {name} (\n" + ",\n".join(parts) + f"\n){suffix}")
    return statements


def export_mysql_sql():
    lines = [
        "-- Generated by `python manage.py export-schema`. Do not edit by hand.",
        f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4;",
        f"USE {Config.MYSQL_DATABASE};",
        "",
    ]
    lines += [s + ";\n" for s in create_statements(False)]
    lines += [f"CREATE INDEX {n} ON {t} ({c});" for n, t, c in INDEXES]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Initialisation / upgrades
# ---------------------------------------------------------------------------


def _existing_columns(cursor, table):
    if is_sqlite():
        cursor.execute(f"PRAGMA table_info({table})")
        return {row["name"] for row in cursor.fetchall()}
    cursor.execute(
        "SELECT column_name AS name FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s", (Config.MYSQL_DATABASE, table))
    return {row["name"] for row in cursor.fetchall()}


def _index_exists(cursor, name, table):
    if is_sqlite():
        cursor.execute("SELECT 1 AS x FROM sqlite_master WHERE type='index' AND name=%s", (name,))
    else:
        cursor.execute(
            "SELECT 1 AS x FROM information_schema.statistics "
            "WHERE table_schema=%s AND table_name=%s AND index_name=%s",
            (Config.MYSQL_DATABASE, table, name))
    return cursor.fetchone() is not None


def _ensure_mysql_database(retries=30, delay=2):
    """Create the database, waiting for MySQL to come up (useful in Docker)."""
    import time

    import pymysql

    for attempt in range(retries):
        try:
            connection = get_connection(database=False)
            break
        except pymysql.err.OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` CHARACTER SET utf8mb4")
    finally:
        connection.close()
    return pymysql


def create_schema():
    """Create missing tables/columns/indexes. Safe to run repeatedly."""
    sqlite = is_sqlite()
    if not sqlite:
        _ensure_mysql_database()
    connection = get_connection()
    added = []
    try:
        with connection.cursor() as cursor:
            if sqlite:
                cursor.execute("PRAGMA journal_mode = WAL")  # persistent; set once
            for statement in create_statements(sqlite):
                cursor.execute(statement)
            # Upgrade databases created by older versions of the project.
            for name, columns, _ in TABLES:
                existing = _existing_columns(cursor, name)
                for col, defn in columns:
                    if col in existing or "{PK}" in defn:
                        continue
                    rendered = _render(defn, sqlite).replace(" UNIQUE", "")
                    cursor.execute(f"ALTER TABLE {name} ADD COLUMN {col} {rendered}")
                    added.append(f"{name}.{col}")
            for idx, table, cols in INDEXES:
                if not _index_exists(cursor, idx, table):
                    cursor.execute(f"CREATE INDEX {idx} ON {table} ({cols})")
    finally:
        connection.close()
    return added
