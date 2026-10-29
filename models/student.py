from database.db import execute, execute_count, query_all, query_one

PROFILE_FIELDS = [
    "enrollment_no", "phone", "branch", "year", "cgpa", "attendance", "backlogs",
    "aptitude_score", "coding_score", "communication_score", "technical_score",
    "projects", "internships", "certifications", "skills",
]
SCORE_FIELDS = ["cgpa", "attendance", "aptitude_score", "coding_score",
                "communication_score", "technical_score"]

_SELECT = """
    SELECT s.*, u.full_name, u.email, u.is_active
    FROM students s INNER JOIN users u ON s.user_id = u.id
"""


class Student:
    @staticmethod
    def create_profile(user_id):
        execute("INSERT INTO students (user_id) VALUES (%s)", (user_id,))

    @staticmethod
    def get_by_user_id(user_id):
        return query_one(_SELECT + " WHERE s.user_id = %s", (user_id,))

    @staticmethod
    def all(search="", branch="", status=""):
        sql, params = _SELECT + " WHERE 1=1", []
        if search:
            sql += " AND (LOWER(u.full_name) LIKE %s OR LOWER(u.email) LIKE %s OR LOWER(COALESCE(s.enrollment_no,'')) LIKE %s)"
            like = f"%{search.lower()}%"
            params += [like, like, like]
        if branch:
            sql += " AND s.branch = %s"
            params.append(branch)
        if status:
            sql += " AND s.placement_status = %s"
            params.append(status)
        return query_all(sql + " ORDER BY u.id DESC", params)

    @staticmethod
    def update_profile(user_id, data):
        fields = [f for f in PROFILE_FIELDS if f in data]
        if not fields:
            return 0
        sets = ", ".join(f"{f} = %s" for f in fields) + ", updated_at = CURRENT_TIMESTAMP"
        return execute_count(f"UPDATE students SET {sets} WHERE user_id = %s",
                             [data[f] for f in fields] + [user_id])

    @staticmethod
    def set_placement(user_id, status, company=None, package=None):
        execute("UPDATE students SET placement_status = %s, placed_company = %s, package_lpa = %s "
                "WHERE user_id = %s", (status, company, package, user_id))

    @staticmethod
    def completeness(student):
        """Percentage of profile fields filled in."""
        if not student:
            return 0
        keys = ["enrollment_no", "phone", "branch", "year", "cgpa", "attendance",
                "aptitude_score", "coding_score", "communication_score",
                "technical_score", "skills"]
        done = sum(1 for k in keys if student.get(k) not in (None, ""))
        return round(done * 100 / len(keys))

    @staticmethod
    def has_scores(student):
        return bool(student) and all(student.get(k) is not None for k in SCORE_FIELDS)
