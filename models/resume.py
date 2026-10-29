import json

from database.db import execute, query_all, query_one


class Resume:
    @staticmethod
    def save(user_id, original, stored, size, result):
        score = result["score"]
        return execute(
            "INSERT INTO resume_analysis (user_id, original_filename, stored_filename, file_size, "
            "word_count, overall_score, rating, section_score, skill_score, length_score, "
            "skills_json, recommendations_json, sections_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_id, original, stored, size, len(result["resume_text"].split()),
             score["overall_score"], score["rating"], score["section_score"], score["skill_score"],
             score["length_score"], json.dumps(result["skills"]),
             json.dumps(result["recommendations"]), json.dumps(score.get("sections", {}))))

    @staticmethod
    def history(user_id):
        return query_all("SELECT * FROM resume_analysis WHERE user_id = %s ORDER BY id DESC", (user_id,))

    @staticmethod
    def latest(user_id):
        return query_one("SELECT * FROM resume_analysis WHERE user_id = %s ORDER BY id DESC LIMIT 1",
                         (user_id,))

    @staticmethod
    def get(user_id, analysis_id):
        return query_one("SELECT * FROM resume_analysis WHERE id = %s AND user_id = %s",
                         (analysis_id, user_id))
