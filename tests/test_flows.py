import io
import os
import unittest

from tests.base import AppTestCase, CREDENTIALS
from database.db import query_all, query_one, scalar
from models.company import Company, Drive
from models.user import User

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "sample_resume.pdf")
SCORES = {"cgpa": "7.5", "attendance": "82", "aptitude_score": "70", "coding_score": "72",
          "communication_score": "66", "technical_score": "74", "projects": "3", "internships": "1",
          "certifications": "2"}


def student_id():
    return User.find_by_email("student@placement.com")["id"]


class StudentFlowTests(AppTestCase):
    def setUp(self):
        super().setUp()
        self.login("student")

    def test_profile_update_and_validation(self):
        data = dict(SCORES, full_name="Satish Dhangar", email="student@placement.com", phone="9876543210",
                    enrollment_no="20220001", branch="Artificial intelligence and data sciences ", year="Final Year",
                    backlogs="0", skills="Python, SQL, Git")
        self.assertEqual(self.client.post("/student/profile", data=data).status_code, 302)
        self.assertEqual(query_one("SELECT cgpa FROM students WHERE user_id = %s", (student_id(),))["cgpa"], 7.5)
        self.assertEqual(self.client.post("/student/profile", data=dict(data, cgpa="11")).status_code, 400)
        self.assertEqual(self.client.post("/student/profile", data=dict(data, email="admin@placement.com")).status_code, 400)
        self.assertEqual(self.client.post("/student/profile", data=dict(data, phone="abc")).status_code, 400)

    def test_prediction_saved_and_preview(self):
        before = scalar("SELECT COUNT(*) FROM prediction_history WHERE user_id = %s", (student_id(),))
        r = self.client.post("/student/prediction", data=SCORES)
        self.assertEqual(r.status_code, 200)
        self.assertIn("What moved your probability", r.get_data(as_text=True))
        self.assertEqual(scalar("SELECT COUNT(*) FROM prediction_history WHERE user_id = %s", (student_id(),)), before + 1)
        self.assertEqual(self.client.post("/student/prediction", data=dict(SCORES, cgpa="-1")).status_code, 400)
        preview = self.client.post("/student/prediction/preview", json=SCORES)
        self.assertTrue(preview.get_json()["ok"])
        self.assertEqual(self.client.post("/student/prediction/preview", json={"cgpa": "x"}).status_code, 400)

    def test_readiness_and_skill_gap_saved(self):
        six = {k: v for k, v in SCORES.items() if k not in ("projects", "internships", "certifications")}
        n1 = scalar("SELECT COUNT(*) FROM readiness_history WHERE user_id = %s", (student_id(),))
        self.assertEqual(self.client.post("/student/readiness-score", data=six).status_code, 200)
        self.assertEqual(scalar("SELECT COUNT(*) FROM readiness_history WHERE user_id = %s", (student_id(),)), n1 + 1)
        n2 = scalar("SELECT COUNT(*) FROM skill_gap_history WHERE user_id = %s", (student_id(),))
        self.assertEqual(self.client.post("/student/skill-gap", data=six).status_code, 200)
        self.assertEqual(scalar("SELECT COUNT(*) FROM skill_gap_history WHERE user_id = %s", (student_id(),)), n2 + 1)

    def test_resume_upload_is_private(self):
        with open(FIXTURE, "rb") as handle:
            r = self.client.post("/student/resume", data={"resume": (handle, "my resume.pdf")},
                                 content_type="multipart/form-data")
        self.assertEqual(r.status_code, 302)
        row = query_one("SELECT * FROM resume_analysis WHERE user_id = %s ORDER BY id DESC LIMIT 1", (student_id(),))
        self.assertGreater(row["overall_score"], 50)
        self.assertEqual(self.client.get(f"/student/resume/{row['id']}").status_code, 200)
        file_response = self.client.get(f"/student/resume/{row['id']}/file")
        self.assertEqual(file_response.mimetype, "application/pdf")
        # Not reachable through /static and not downloadable by another student.
        self.assertEqual(self.app.test_client().get("/static/uploads/resumes/" + row["stored_filename"]).status_code, 404)
        other = self.app.test_client()
        other.post("/auth/register", data={"full_name": "Other Person", "email": "other@example.com",
                                            "password": "Passw0rdX", "confirm_password": "Passw0rdX"})
        other.post("/auth/login", data={"email": "other@example.com", "password": "Passw0rdX"})
        self.assertEqual(other.get(f"/student/resume/{row['id']}/file").status_code, 302)
        self.assertEqual(other.get(f"/student/resume/{row['id']}").status_code, 302)

    def test_resume_rejects_non_pdf(self):
        r = self.client.post("/student/resume", data={"resume": (io.BytesIO(b"not a pdf"), "evil.pdf")},
                             content_type="multipart/form-data")
        self.assertEqual(r.status_code, 302)
        self.assertNotIn("/student/resume/", r.headers["Location"].replace("/student/resume", "", 1) or "x")
        r = self.client.post("/student/resume", data={"resume": (io.BytesIO(b"%PDF-1.4 junk"), "x.txt")},
                             content_type="multipart/form-data")
        self.assertEqual(r.status_code, 302)

    def test_mock_interview_round_trip(self):
        r = self.client.get("/student/mock-interview/start?category=Technical&count=3")
        self.assertEqual(r.status_code, 200)
        with self.client.session_transaction() as sess:
            ids = sess["interview"]["ids"]
        data = {f"answer_{i}": "A stack is lifo and a queue is fifo; recursion uses a function that calls itself with a base case" for i in ids}
        r = self.client.post("/student/mock-interview/submit", data=data)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get(r.headers["Location"]).status_code, 200)
        self.assertEqual(self.client.post("/student/mock-interview/submit", data=data).status_code, 302)  # expired session

    def test_reports(self):
        pdf = self.client.get("/reports/student/pdf")
        self.assertEqual(pdf.mimetype, "application/pdf")
        self.assertTrue(pdf.data.startswith(b"%PDF"))
        xlsx = self.client.get("/reports/student/history.xlsx")
        self.assertTrue(xlsx.data.startswith(b"PK"))

    def test_notifications(self):
        self.assertIn("count", self.client.get("/notifications/unread-count").get_json())
        self.assertEqual(self.client.post("/notifications/read-all").status_code, 302)
        self.assertEqual(self.client.get("/notifications/unread-count").get_json()["count"], 0)


class PlacementChainTests(AppTestCase):
    """TPO creates a drive, a student applies, TPO selects them."""

    def test_drive_to_placement(self):
        tpo = self.login("tpo", self.app.test_client())
        company_id = Company.create({"name": "Open Door Ltd", "min_cgpa": 0, "min_attendance": 0, "min_aptitude": 0,
                                     "min_coding": 0, "min_communication": 0, "min_technical": 0,
                                     "max_backlogs": 30, "required_skills": "", "package_lpa": 12, "is_active": 1})
        r = tpo.post("/tpo/drives/new", data={"company_id": company_id, "job_role": "Engineer", "drive_date": "2030-01-15",
                                                "openings": "3", "package_lpa": "12", "status": "Upcoming"})
        self.assertEqual(r.status_code, 302)
        drive = query_one("SELECT * FROM drives WHERE company_id = %s", (company_id,))
        self.assertGreater(scalar("SELECT COUNT(*) FROM notifications WHERE title LIKE 'New placement drive: Open Door%'"), 0)

        student = self.login("student", self.app.test_client())
        self.assertEqual(student.post(f"/student/drives/{drive['id']}/apply").status_code, 302)
        self.assertIsNotNone(Drive.application(drive["id"], student_id()))
        student.post(f"/student/drives/{drive['id']}/apply")  # duplicate is harmless
        self.assertEqual(scalar("SELECT COUNT(*) FROM drive_applications WHERE drive_id = %s", (drive["id"],)), 1)

        application = Drive.application(drive["id"], student_id())
        tpo.post(f"/tpo/applications/{application['id']}/status", data={"status": "Selected"})
        placed = query_one("SELECT placement_status, placed_company, package_lpa FROM students WHERE user_id = %s", (student_id(),))
        self.assertEqual((placed["placement_status"], placed["placed_company"], placed["package_lpa"]), ("Placed", "Open Door Ltd", 12))
        self.assertGreater(scalar("SELECT COUNT(*) FROM notifications WHERE user_id = %s AND title LIKE 'Congratulations%'", (student_id(),)), 0)

        tpo.post(f"/tpo/applications/{application['id']}/status", data={"status": "Rejected"})
        self.assertEqual(query_one("SELECT placement_status FROM students WHERE user_id = %s", (student_id(),))["placement_status"], "Not Placed")

    def test_ineligible_student_cannot_apply(self):
        company_id = Company.create({"name": "Elite Corp", "min_cgpa": 9.9, "min_attendance": 99, "min_aptitude": 99,
                                     "min_coding": 99, "min_communication": 99, "min_technical": 99, "max_backlogs": 0,
                                     "required_skills": "COBOL", "package_lpa": 40, "is_active": 1})
        drive_id = Drive.create({"company_id": company_id, "job_role": "Wizard", "drive_date": "2030-02-01",
                                 "openings": 1, "package_lpa": 40, "status": "Upcoming"})
        student = self.login("student", self.app.test_client())
        student.post(f"/student/drives/{drive_id}/apply")
        self.assertIsNone(Drive.application(drive_id, student_id()))


class AdminFlowTests(AppTestCase):
    def setUp(self):
        super().setUp()
        self.login("admin")

    def student_form(self, **over):
        data = dict(SCORES, full_name="Created By Admin", email="created@example.com", password="Passw0rdX",
                    phone="9000000000", enrollment_no="ADM001", branch="Information Technology", year="Final Year",
                    backlogs="0", skills="Python")
        data.update(over)
        return data

    def test_student_crud(self):
        self.assertEqual(self.client.post("/admin/students/new", data=self.student_form()).status_code, 302)
        user = User.find_by_email("created@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(self.client.post("/admin/students/new", data=self.student_form()).status_code, 400)  # duplicate
        edit = dict(self.student_form(full_name="Renamed", placement_status="Placed", placed_company="Acme", package_lpa="6.5"))
        edit.pop("password")
        self.assertEqual(self.client.post(f"/admin/students/{user['id']}/edit", data=edit).status_code, 302)
        row = query_one("SELECT placement_status, package_lpa FROM students WHERE user_id = %s", (user["id"],))
        self.assertEqual((row["placement_status"], row["package_lpa"]), ("Placed", 6.5))
        self.client.post(f"/admin/students/{user['id']}/toggle")
        self.assertFalse(User.find_by_id(user["id"])["is_active"])
        self.client.post(f"/admin/students/{user['id']}/delete")
        self.assertIsNone(User.find_by_id(user["id"]))
        self.assertEqual(scalar("SELECT COUNT(*) FROM students WHERE user_id = %s", (user["id"],)), 0)  # cascade

    def company_form(self, **over):
        data = {"name": "Tester Inc", "industry": "QA", "location": "Pune", "package_lpa": "5", "min_cgpa": "6",
                "min_attendance": "70", "min_aptitude": "50", "min_coding": "50", "min_communication": "50",
                "min_technical": "50", "max_backlogs": "1", "required_skills": "Python, SQL", "is_active": "1"}
        data.update(over)
        return data

    def test_company_crud(self):
        self.assertEqual(self.client.post("/admin/companies/new", data=self.company_form()).status_code, 302)
        company = query_one("SELECT * FROM companies WHERE name = 'Tester Inc'")
        self.assertEqual(self.client.post("/admin/companies/new", data=self.company_form()).status_code, 400)
        self.assertEqual(self.client.post("/admin/companies/new", data=self.company_form(name="X2", min_cgpa="15")).status_code, 400)
        self.client.post(f"/admin/companies/{company['id']}/edit", data=self.company_form(min_cgpa="8"))
        self.assertEqual(Company.get(company["id"])["min_cgpa"], 8)
        self.client.post(f"/admin/companies/{company['id']}/toggle")
        self.assertEqual(Company.get(company["id"])["is_active"], 0)
        self.client.post(f"/admin/companies/{company['id']}/delete")
        self.assertIsNone(Company.get(company["id"]))

    def test_dataset_upload_and_retrain(self):
        import random
        rng = random.Random(3)
        lines = ["cgpa,attendance,aptitude_score,coding_score,communication_score,technical_score,placed"]
        for _ in range(80):
            ability = rng.gauss(0, 1)
            vals = [round(7 + ability, 1), round(76 + 8 * ability), round(67 + 10 * ability), round(70 + 11 * ability),
                    round(68 + 9 * ability), round(72 + 10 * ability)]
            lines.append(",".join(map(str, vals)) + f",{1 if ability + rng.gauss(0, .5) > 0 else 0}")
        csv = "\n".join(lines).encode()
        r = self.client.post("/admin/upload-dataset", data={"dataset": (io.BytesIO(csv), "campus.csv")},
                             content_type="multipart/form-data")
        self.assertEqual(r.status_code, 302)
        dataset = query_one("SELECT * FROM datasets WHERE original_name = 'campus.csv'")
        self.assertTrue(50 <= dataset["rows_count"] <= 80)  # duplicates are removed
        bad = self.client.post("/admin/upload-dataset", data={"dataset": (io.BytesIO(b"a,b\n1,2\n"), "bad.csv")},
                               content_type="multipart/form-data", follow_redirects=True)
        self.assertIn("Dataset rejected", bad.get_data(as_text=True))
        self.assertIsNone(query_one("SELECT id FROM datasets WHERE original_name = 'bad.csv'"))

        versions = scalar("SELECT COUNT(*) FROM model_versions")
        r = self.client.post("/admin/model-training", data={"include_base": "1"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(scalar("SELECT COUNT(*) FROM model_versions"), versions + 1)
        self.assertEqual(scalar("SELECT COUNT(*) FROM model_versions WHERE is_active = 1"), 1)
        from ml.predict import predict_placement
        self.assertIn("model_version", predict_placement(7, 75, 65, 65, 65, 65))  # new model serves predictions
        self.client.post(f"/admin/datasets/{dataset['id']}/delete")
        self.assertIsNone(query_one("SELECT id FROM datasets WHERE id = %s", (dataset["id"],)))

    def test_staff_exports(self):
        for path in ("students.xlsx", "students.csv", "predictions.xlsx", "placements.xlsx", "companies.xlsx"):
            self.assertEqual(self.client.get(f"/reports/staff/{path}").status_code, 200, path)
        student = self.login("student", self.app.test_client())
        self.assertEqual(student.get("/reports/staff/students.csv").status_code, 302)


class ContactTests(AppTestCase):
    def test_contact_form_notifies_admins(self):
        admin_id = User.find_by_email("admin@placement.com")["id"]
        before = scalar("SELECT COUNT(*) FROM notifications WHERE user_id = %s", (admin_id,))
        bad = self.client.post("/contact", data={"name": "A", "email": "x", "message": "hi"})
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post("/contact", data={"name": "Ravi", "email": "ravi@example.com", "subject": "Hello",
                                                 "message": "I would like a demo for my college."})
        self.assertEqual(ok.status_code, 302)
        self.assertEqual(scalar("SELECT COUNT(*) FROM notifications WHERE user_id = %s", (admin_id,)), before + 1)
        self.assertEqual(scalar("SELECT COUNT(*) FROM contact_messages WHERE email = 'ravi@example.com'"), 1)


if __name__ == "__main__":
    unittest.main()
