"""Every page renders for the right role, and the right roles only."""
import unittest

from tests.base import AppTestCase

PREFIXES = {"student": ("/student", "/reports/student", "/notifications"),
            "tpo": ("/tpo",), "admin": ("/admin",)}
SKIP = {"/student/mock-interview/start"}


class PageTests(AppTestCase):
    def pages_for(self, role):
        rules = [str(r) for r in self.app.url_map.iter_rules()
                 if "GET" in r.methods and "<" not in str(r) and str(r).startswith(PREFIXES[role])]
        return sorted(set(rules) - SKIP)

    def test_public_pages(self):
        client = self.app.test_client()
        for path in ("/", "/about", "/contact", "/auth/login", "/auth/register", "/auth/forgot-password"):
            self.assertEqual(client.get(path).status_code, 200, path)
        self.assertEqual(client.get("/does-not-exist").status_code, 404)

    def test_every_role_page_renders(self):
        for role in PREFIXES:
            client = self.login(role)
            pages = self.pages_for(role)
            self.assertGreater(len(pages), 4)
            for path in pages:
                response = client.get(path)
                self.assertEqual(response.status_code, 200, f"{role}: {path}")

    def test_parameterised_pages(self):
        admin = self.login("admin")
        self.assertEqual(admin.get("/admin/companies/1/edit").status_code, 200)
        student_id = self.app.test_client() and __import__("models.user", fromlist=["User"]).User.find_by_email("student@placement.com")["id"]
        self.assertEqual(admin.get(f"/admin/students/{student_id}/edit").status_code, 200)
        tpo = self.login("tpo")
        self.assertEqual(tpo.get("/tpo/drives/1/applicants").status_code, 200)
        self.assertEqual(tpo.get("/tpo/drives/1/edit").status_code, 200)
        self.assertEqual(tpo.get("/tpo/eligible-students?company_id=6").status_code, 200)
        student = self.login("student")
        self.assertEqual(student.get("/student/mock-interview/start?category=Aptitude&count=3").status_code, 200)

    def test_security_headers_and_health(self):
        r = self.app.test_client().get("/")
        self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(r.headers["X-Frame-Options"], "DENY")
        self.assertIn("script-src 'self'", r.headers["Content-Security-Policy"])
        health = self.app.test_client().get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["status"], "ok")

    def test_no_inline_scripts(self):
        """CSP forbids inline JS; make sure templates do not rely on it."""
        client = self.login("student")
        for path in ("/student/dashboard", "/student/prediction", "/student/company-eligibility"):
            html = client.get(path).get_data(as_text=True)
            import re
            for tag in re.findall(r"<script\b[^>]*>", html):
                self.assertIn("src=", tag, f"inline script on {path}")


if __name__ == "__main__":
    unittest.main()
