from database.db import execute, execute_count, query_all, query_one, scalar
from utils.helpers import split_skills

FIELDS = ["name", "industry", "location", "website", "description", "min_cgpa", "min_attendance",
          "min_aptitude", "min_coding", "min_communication", "min_technical", "max_backlogs",
          "required_skills", "package_lpa", "is_active"]


class Company:
    @staticmethod
    def all(active_only=False):
        sql = "SELECT * FROM companies"
        if active_only:
            sql += " WHERE is_active = 1"
        return query_all(sql + " ORDER BY name")

    @staticmethod
    def get(company_id):
        return query_one("SELECT * FROM companies WHERE id = %s", (company_id,))

    @staticmethod
    def name_exists(name, exclude_id=None):
        row = query_one("SELECT id FROM companies WHERE LOWER(name) = %s", (name.lower(),))
        return bool(row) and row["id"] != exclude_id

    @staticmethod
    def create(data):
        cols = [f for f in FIELDS if f in data]
        return execute(
            f"INSERT INTO companies ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})",
            [data[c] for c in cols])

    @staticmethod
    def update(company_id, data):
        cols = [f for f in FIELDS if f in data]
        sets = ", ".join(f"{c} = %s" for c in cols) + ", updated_at = CURRENT_TIMESTAMP"
        return execute_count(f"UPDATE companies SET {sets} WHERE id = %s",
                             [data[c] for c in cols] + [company_id])

    @staticmethod
    def delete(company_id):
        return execute_count("DELETE FROM companies WHERE id = %s", (company_id,))

    @staticmethod
    def as_rule(row):
        """Convert a DB row to the dict shape used by the eligibility checker."""
        return {
            "id": row["id"], "name": row["name"], "industry": row.get("industry"),
            "location": row.get("location"), "package_lpa": row.get("package_lpa"),
            "min_cgpa": row["min_cgpa"], "min_attendance": row["min_attendance"],
            "min_aptitude": row["min_aptitude"], "min_coding": row["min_coding"],
            "min_communication": row["min_communication"], "min_technical": row["min_technical"],
            "max_backlogs": row.get("max_backlogs") or 0,
            "required_skills": split_skills(row.get("required_skills")),
        }

    @staticmethod
    def count():
        return scalar("SELECT COUNT(*) FROM companies WHERE is_active = 1")


class Drive:
    BASE = """
        SELECT d.*, c.name AS company_name, c.industry, c.min_cgpa, c.required_skills,
               (SELECT COUNT(*) FROM drive_applications a WHERE a.drive_id = d.id) AS applicants
        FROM drives d INNER JOIN companies c ON c.id = d.company_id
    """

    @staticmethod
    def all(status=None):
        sql, params = Drive.BASE, []
        if status:
            sql += " WHERE d.status = %s"
            params.append(status)
        return query_all(sql + " ORDER BY d.drive_date DESC, d.id DESC", params)

    @staticmethod
    def open_drives():
        return query_all(Drive.BASE + " WHERE d.status IN ('Upcoming', 'Active') "
                         "ORDER BY d.drive_date ASC, d.id ASC")

    @staticmethod
    def get(drive_id):
        return query_one(Drive.BASE + " WHERE d.id = %s", (drive_id,))

    @staticmethod
    def create(data, created_by=None):
        return execute(
            "INSERT INTO drives (company_id, job_role, drive_date, location, openings, "
            "package_lpa, status, description, created_by) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (data["company_id"], data["job_role"], data["drive_date"], data.get("location"),
             data["openings"], data.get("package_lpa"), data["status"],
             data.get("description"), created_by))

    @staticmethod
    def update(drive_id, data):
        return execute_count(
            "UPDATE drives SET company_id=%s, job_role=%s, drive_date=%s, location=%s, openings=%s, "
            "package_lpa=%s, status=%s, description=%s WHERE id=%s",
            (data["company_id"], data["job_role"], data["drive_date"], data.get("location"),
             data["openings"], data.get("package_lpa"), data["status"],
             data.get("description"), drive_id))

    @staticmethod
    def delete(drive_id):
        return execute_count("DELETE FROM drives WHERE id = %s", (drive_id,))

    @staticmethod
    def applicants(drive_id):
        return query_all(
            "SELECT a.id AS application_id, a.status, a.applied_at, s.user_id, u.full_name, u.email, "
            "s.enrollment_no, s.branch, s.cgpa, s.coding_score, s.technical_score "
            "FROM drive_applications a JOIN users u ON u.id = a.user_id "
            "JOIN students s ON s.user_id = a.user_id WHERE a.drive_id = %s "
            "ORDER BY s.cgpa DESC", (drive_id,))

    @staticmethod
    def application(drive_id, user_id):
        return query_one("SELECT * FROM drive_applications WHERE drive_id=%s AND user_id=%s",
                         (drive_id, user_id))

    @staticmethod
    def apply(drive_id, user_id):
        return execute("INSERT INTO drive_applications (drive_id, user_id) VALUES (%s, %s)",
                       (drive_id, user_id))

    @staticmethod
    def set_application_status(application_id, status):
        execute("UPDATE drive_applications SET status = %s, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = %s", (status, application_id))

    @staticmethod
    def get_application(application_id):
        return query_one(
            "SELECT a.*, d.job_role, d.package_lpa, d.company_id, c.name AS company_name "
            "FROM drive_applications a JOIN drives d ON d.id = a.drive_id "
            "JOIN companies c ON c.id = d.company_id WHERE a.id = %s", (application_id,))

    @staticmethod
    def for_student(user_id):
        return query_all(
            "SELECT a.id AS application_id, a.status AS application_status, a.applied_at, d.*, "
            "c.name AS company_name FROM drive_applications a JOIN drives d ON d.id = a.drive_id "
            "JOIN companies c ON c.id = d.company_id WHERE a.user_id = %s "
            "ORDER BY a.applied_at DESC", (user_id,))
