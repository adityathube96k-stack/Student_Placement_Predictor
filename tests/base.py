"""Shared test fixtures. Uses an isolated SQLite database seeded once per process."""
import os
import shutil
import tempfile
import unittest

_TMP = tempfile.mkdtemp(prefix="spp_tests_")
os.environ["DB_ENGINE"] = "sqlite"
os.environ["SQLITE_PATH"] = os.path.join(_TMP, "test.db")
os.environ["RESUME_UPLOAD_DIR"] = os.path.join(_TMP, "resumes")
os.environ["LOG_DIR"] = os.path.join(_TMP, "logs")
os.environ["DATASET_UPLOAD_DIR"] = os.path.join(_TMP, "datasets")
os.environ["MODEL_DIR"] = os.path.join(_TMP, "models")

# Start from the shipped model so tests are fast, but never modify the project's copy.
_SHIPPED = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "models")
if os.path.isdir(_SHIPPED):
    shutil.copytree(_SHIPPED, os.environ["MODEL_DIR"])

from app import create_app  # noqa: E402
from config import Config, TestConfig  # noqa: E402

CREDENTIALS = {
    "student": ("student@placement.com", "Student@123"),
    "tpo": ("tpo@placement.com", "Tpo@12345"),
    "admin": ("admin@placement.com", "Admin@123"),
}
_app = None


def get_app():
    global _app
    if _app is None:
        _app = create_app(TestConfig)
    return _app


class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_app()

    def setUp(self):
        self.client = self.app.test_client()

    def login(self, role="student", client=None):
        client = client or self.client
        email, password = CREDENTIALS[role]
        client.get("/auth/logout")
        response = client.post("/auth/login", data={"email": email, "password": password})
        self.assertEqual(response.status_code, 302, f"login failed for {role}")
        return client
