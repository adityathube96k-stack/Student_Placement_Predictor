
from database.db import check_connection


def test_database_connection():
    connected, message = check_connection()
    assert connected is True, message
