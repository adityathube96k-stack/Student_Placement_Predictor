from database.db import execute, execute_count, query_all, scalar


class Notification:
    @staticmethod
    def create(user_id, title, message="", category="info", link=None):
        return execute(
            "INSERT INTO notifications (user_id, title, message, category, link) "
            "VALUES (%s, %s, %s, %s, %s)", (user_id, title, message, category, link))

    @staticmethod
    def recent(user_id, limit=8):
        return query_all("SELECT * FROM notifications WHERE user_id = %s "
                         "ORDER BY id DESC LIMIT %s", (user_id, limit))

    @staticmethod
    def all(user_id):
        return query_all("SELECT * FROM notifications WHERE user_id = %s ORDER BY id DESC", (user_id,))

    @staticmethod
    def unread_count(user_id):
        return scalar("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = 0", (user_id,))

    @staticmethod
    def mark_read(user_id, notification_id):
        return execute_count("UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s",
                             (notification_id, user_id))

    @staticmethod
    def mark_all_read(user_id):
        return execute_count("UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0",
                             (user_id,))

    @staticmethod
    def delete(user_id, notification_id):
        return execute_count("DELETE FROM notifications WHERE id = %s AND user_id = %s",
                             (notification_id, user_id))
