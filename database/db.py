"""Database access layer.

Exposes one small API that works on both MySQL (PyMySQL) and SQLite:

    get_connection()            -> connection with dict cursors (legacy-compatible)
    query_one / query_all       -> read helpers returning plain dicts
    execute / execute_many      -> write helpers (execute returns lastrowid)
    transaction()               -> context manager for multi-statement writes

SQL is written once using ``%s`` placeholders (MySQL style); the SQLite adapter
translates them. Keep queries portable: no engine-specific functions.
"""
import datetime as _dt
import sqlite3
from contextlib import contextmanager
from decimal import Decimal

from config import Config

# ---------------------------------------------------------------------------
# SQLite adapter
# ---------------------------------------------------------------------------


def _parse_ts(raw):
    text = raw.decode() if isinstance(raw, bytes) else raw
    text = text.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return _dt.datetime.strptime(text, fmt)
        except ValueError:
            continue
    return text


def _parse_date(raw):
    text = raw.decode() if isinstance(raw, bytes) else raw
    try:
        return _dt.date.fromisoformat(text.strip()[:10])
    except ValueError:
        return text


sqlite3.register_converter("TIMESTAMP", _parse_ts)
sqlite3.register_converter("DATETIME", _parse_ts)
sqlite3.register_converter("DATE", _parse_date)
sqlite3.register_adapter(_dt.datetime, lambda v: v.strftime("%Y-%m-%d %H:%M:%S"))
sqlite3.register_adapter(_dt.date, lambda v: v.isoformat())


def _translate(sql):
    """MySQL placeholder style -> SQLite."""
    return sql.replace("%%", "\0").replace("%s", "?").replace("\0", "%")


class _SQLiteCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        self._cursor.execute(_translate(sql), tuple(params or ()))
        return self

    def executemany(self, sql, seq):
        self._cursor.executemany(_translate(sql), [tuple(p) for p in seq])
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(r) for r in self._cursor.fetchall()]

    def fetchmany(self, size=None):
        rows = self._cursor.fetchmany(size or self._cursor.arraysize)
        return [dict(r) for r in rows]

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class _SQLiteConnection:
    """Mimics the subset of the PyMySQL connection API this project uses."""

    def __init__(self, path):
        self._conn = sqlite3.connect(
            path, timeout=30, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA synchronous = NORMAL")

    def cursor(self):
        return _SQLiteCursor(self._conn.cursor())

    def begin(self):
        self._conn.execute("BEGIN")

    def commit(self):
        if self._conn.in_transaction:
            self._conn.execute("COMMIT")

    def rollback(self):
        if self._conn.in_transaction:
            self._conn.execute("ROLLBACK")

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------


def is_sqlite():
    return Config.DB_ENGINE == "sqlite"


def get_connection(database=True):
    """Open a new connection. Callers are responsible for closing it."""
    if is_sqlite():
        import os

        os.makedirs(os.path.dirname(Config.SQLITE_PATH) or ".", exist_ok=True)
        return _SQLiteConnection(Config.SQLITE_PATH)

    import pymysql

    kwargs = dict(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset="utf8mb4",
    )
    if database:
        kwargs["database"] = Config.MYSQL_DATABASE
    return pymysql.connect(**kwargs)


def check_connection():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS test")
            cursor.fetchone()
        connection.close()
        label = "SQLite" if is_sqlite() else "MySQL"
        return True, f"{label} connection successful."
    except Exception as error:  # noqa: BLE001 - surfaced to the health endpoint
        return False, str(error)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clean(row):
    if row is None:
        return None
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in row.items()}


def query_all(sql, params=()):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return [_clean(r) for r in cursor.fetchall()]
    finally:
        connection.close()


def query_one(sql, params=()):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return _clean(cursor.fetchone())
    finally:
        connection.close()


def scalar(sql, params=(), default=0):
    row = query_one(sql, params)
    if not row:
        return default
    value = next(iter(row.values()))
    return default if value is None else value


def execute(sql, params=()):
    """Run a write statement and return the new row id (or 0)."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid
    finally:
        connection.close()


def execute_count(sql, params=()):
    """Run a write statement and return the affected row count."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
    finally:
        connection.close()


def execute_many(sql, rows):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.executemany(sql, rows)
    finally:
        connection.close()


@contextmanager
def transaction():
    """Yield a connection inside a transaction; commit on success, else roll back."""
    connection = get_connection()
    try:
        connection.begin()
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
