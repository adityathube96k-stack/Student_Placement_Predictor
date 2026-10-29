from database.db import execute, execute_count, query_all, query_one
from utils.security import hash_password


class User:
    @staticmethod
    def find_by_email(email):
        return query_one("SELECT * FROM users WHERE email = %s", (email,))

    @staticmethod
    def find_by_id(user_id):
        return query_one("SELECT * FROM users WHERE id = %s", (user_id,))

    @staticmethod
    def create(full_name, email, password, role="student", is_active=True, password_hash=None):
        return execute(
            "INSERT INTO users (full_name, email, password_hash, role, is_active) "
            "VALUES (%s, %s, %s, %s, %s)",
            (full_name, email, password_hash or hash_password(password), role, 1 if is_active else 0))

    @staticmethod
    def set_password(user_id, password):
        execute("UPDATE users SET password_hash = %s WHERE id = %s",
                (hash_password(password), user_id))

    @staticmethod
    def set_active(user_id, active):
        return execute_count("UPDATE users SET is_active = %s WHERE id = %s",
                             (1 if active else 0, user_id))

    @staticmethod
    def touch_login(user_id):
        execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s", (user_id,))

    @staticmethod
    def update_name_email(user_id, full_name, email):
        execute("UPDATE users SET full_name = %s, email = %s WHERE id = %s",
                (full_name, email, user_id))

    @staticmethod
    def ids_by_role(role):
        return [r["id"] for r in query_all("SELECT id FROM users WHERE role = %s AND is_active = 1", (role,))]
