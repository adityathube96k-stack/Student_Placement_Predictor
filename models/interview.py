import json

from database.db import execute, query_all, query_one


class Interview:
    @staticmethod
    def save(user_id, category, total, score, level, details):
        return execute(
            "INSERT INTO interview_history (user_id, category, total_questions, interview_score, "
            "performance_level, details) VALUES (%s,%s,%s,%s,%s,%s)",
            (user_id, category, total, score, level, json.dumps(details)))

    @staticmethod
    def history(user_id):
        return query_all(
            "SELECT id, category, total_questions, interview_score, performance_level, created_at "
            "FROM interview_history WHERE user_id = %s ORDER BY created_at DESC, id DESC", (user_id,))

    @staticmethod
    def get(user_id, interview_id):
        return query_one("SELECT * FROM interview_history WHERE id = %s AND user_id = %s",
                         (interview_id, user_id))
