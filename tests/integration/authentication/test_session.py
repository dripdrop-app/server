from fastapi import status
from fastapi.testclient import TestClient


CREATE_URL = "/api/auth/create"
LOGIN_URL = "/api/auth/login"
SESSION_URL = "/api/auth/session"


def test_session_when_not_logged_in(client: TestClient):
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_session_after_creating_account(client: TestClient):
    TEST_EMAIL = "user@gmail.com"
    response = client.post(
        CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("email") == TEST_EMAIL
    assert json.get("admin") is False


def test_session_after_login(client: TestClient, create_and_login_user):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("email") == user.email
    assert json.get("admin") is False
