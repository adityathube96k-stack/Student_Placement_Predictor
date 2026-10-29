from database.db import execute, query_all, query_one


class Prediction:
    @staticmethod
    def save(user_id, inputs, result):
        return execute(
            "INSERT INTO prediction_history (user_id, cgpa, attendance, aptitude_score, coding_score, "
            "communication_score, technical_score, projects, internships, certifications, prediction, "
            "placement_probability, not_placed_probability, model_version) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_id, inputs["cgpa"], inputs["attendance"], inputs["aptitude_score"],
             inputs["coding_score"], inputs["communication_score"], inputs["technical_score"],
             inputs.get("projects"), inputs.get("internships"), inputs.get("certifications"),
             result["result"], result["placement_probability"], result["not_placed_probability"],
             result.get("model_version")))

    @staticmethod
    def history(user_id, limit=None):
        sql = "SELECT * FROM prediction_history WHERE user_id = %s ORDER BY created_at DESC, id DESC"
        params = [user_id]
        if limit:
            sql += " LIMIT %s"
            params.append(limit)
        return query_all(sql, params)

    @staticmethod
    def latest(user_id):
        return query_one("SELECT * FROM prediction_history WHERE user_id = %s "
                         "ORDER BY created_at DESC, id DESC LIMIT 1", (user_id,))
