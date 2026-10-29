from database.db import execute, query_all


class Report:
    @staticmethod
    def log(user_id, report_type, file_format):
        execute("INSERT INTO report_log (user_id, report_type, file_format) VALUES (%s,%s,%s)",
                (user_id, report_type, file_format))

    @staticmethod
    def recent(user_id=None, limit=10):
        if user_id:
            return query_all("SELECT * FROM report_log WHERE user_id = %s ORDER BY id DESC LIMIT %s",
                             (user_id, limit))
        return query_all("SELECT r.*, u.full_name FROM report_log r LEFT JOIN users u ON u.id = r.user_id "
                         "ORDER BY r.id DESC LIMIT %s", (limit,))
