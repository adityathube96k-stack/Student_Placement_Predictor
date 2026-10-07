from app import app


def test_login_page():
    client = app.test_client()

    response = client.get("/auth/login")

    assert response.status_code == 200


def test_register_page():
    client = app.test_client()

    response = client.get("/auth/register")

    assert response.status_code == 200


def test_forgot_password_page():
    client = app.test_client()

    response = client.get("/auth/forgot-password")

    assert response.status_code == 200