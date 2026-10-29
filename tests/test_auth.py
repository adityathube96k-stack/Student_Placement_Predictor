import re
import unittest

from tests.base import AppTestCase, get_app
from config import TestConfig
from models.user import User


class AuthTests(AppTestCase):
    def register(self, email, password="Passw0rdX", **extra):
        data = {"full_name": "Test Student", "email": email, "password": password, "confirm_password": password}
        data.update(extra)
        return self.client.post("/auth/register", data=data)

    def test_register_login_logout(self):
        self.assertEqual(self.register("new1@example.com").status_code, 302)
        r = self.client.post("/auth/login", data={"email": "new1@example.com", "password": "Passw0rdX"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("/student/dashboard", r.headers["Location"])
        self.assertEqual(self.client.get("/student/dashboard").status_code, 200)
        self.client.get("/auth/logout")
        self.assertEqual(self.client.get("/student/dashboard").status_code, 302)

    def test_register_validation(self):
        self.assertEqual(self.register("dup@example.com").status_code, 302)
        self.assertEqual(self.register("dup@example.com").status_code, 400)          # duplicate
        self.assertEqual(self.register("weak@example.com", "short1").status_code, 400)   # too short
        self.assertEqual(self.register("weak2@example.com", "onlyletters").status_code, 400)
        self.assertEqual(self.register("bad-email").status_code, 400)
        r = self.client.post("/auth/register", data={"full_name": "A B", "email": "m@example.com",
                                                      "password": "Passw0rdX", "confirm_password": "other1234"})
        self.assertEqual(r.status_code, 400)

    def test_wrong_password_and_unknown_user(self):
        self.assertEqual(self.client.post("/auth/login", data={"email": "student@placement.com", "password": "nope"}).status_code, 401)
        self.assertEqual(self.client.post("/auth/login", data={"email": "ghost@example.com", "password": "x"}).status_code, 401)

    def test_inactive_user_blocked(self):
        self.register("inactive@example.com")
        user = User.find_by_email("inactive@example.com")
        User.set_active(user["id"], False)
        r = self.client.post("/auth/login", data={"email": "inactive@example.com", "password": "Passw0rdX"})
        self.assertEqual(r.status_code, 403)

    def test_login_lockout(self):
        self.app.config["LOGIN_MAX_ATTEMPTS"] = 3
        try:
            for _ in range(3):
                self.client.post("/auth/login", data={"email": "lock@example.com", "password": "bad"})
            r = self.client.post("/auth/login", data={"email": "lock@example.com", "password": "bad"})
            self.assertEqual(r.status_code, 429)
        finally:
            self.app.config["LOGIN_MAX_ATTEMPTS"] = TestConfig.LOGIN_MAX_ATTEMPTS

    def test_password_reset_flow_is_single_use(self):
        self.register("reset@example.com")
        page = self.client.post("/auth/forgot-password", data={"email": "reset@example.com"})
        link = re.search(r'href="([^"]*/auth/reset-password/[^"]+)"', page.get_data(as_text=True))
        self.assertIsNotNone(link, "demo reset link should be shown when email is not configured")
        path = "/auth/reset-password/" + link.group(1).split("/auth/reset-password/")[1]
        self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.client.post(path, data={"password": "x", "confirm_password": "x"}).status_code, 400)
        self.assertEqual(self.client.post(path, data={"password": "BrandNew123", "confirm_password": "BrandNew123"}).status_code, 302)
        ok = self.client.post("/auth/login", data={"email": "reset@example.com", "password": "BrandNew123"})
        self.assertEqual(ok.status_code, 302)
        self.assertEqual(self.client.get(path).status_code, 302)  # token no longer valid

    def test_unknown_email_reset_does_not_leak(self):
        r = self.client.post("/auth/forgot-password", data={"email": "nobody@example.com"})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("reset-password", r.get_data(as_text=True))

    def test_role_isolation(self):
        self.login("student")
        for path in ("/admin/dashboard", "/tpo/dashboard", "/admin/students"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 302, path)
            self.assertIn("/student/dashboard", r.headers["Location"])
        self.login("tpo")
        self.assertEqual(self.client.get("/student/dashboard").status_code, 302)
        self.assertEqual(self.client.get("/admin/dashboard").status_code, 302)
        self.login("admin")
        self.assertEqual(self.client.get("/tpo/dashboard").status_code, 302)

    def test_anonymous_redirected_to_login(self):
        r = self.client.get("/student/prediction")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/auth/login", r.headers["Location"])

    def test_open_redirect_is_blocked(self):
        r = self.client.post("/auth/login?next=https://evil.example", data={"email": "student@placement.com", "password": "Student@123"})
        self.assertNotIn("evil.example", r.headers["Location"])


class CsrfTests(unittest.TestCase):
    def test_csrf_enforced_when_enabled(self):
        from app import create_app

        class Cfg(TestConfig):
            CSRF_ENABLED = True
        client = create_app(Cfg).test_client()
        r = client.post("/auth/login", data={"email": "student@placement.com", "password": "Student@123"})
        self.assertEqual(r.status_code, 400)
        page = client.get("/auth/login").get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        r = client.post("/auth/login", data={"email": "student@placement.com", "password": "Student@123", "csrf_token": token})
        self.assertEqual(r.status_code, 302)


if __name__ == "__main__":
    unittest.main()
