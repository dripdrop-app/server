from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME

LOGIN_URL = "/api/auth/login"


def test_login_with_incorrect_password(client: TestClient, create_user):
    user = create_user(email="user@gmail.com", password="password")
    response = client.post(
        LOGIN_URL, json={"email": user.email, "password": "incorrectpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_with_non_existent_email(client: TestClient):
    response = client.post(
        LOGIN_URL, json={"email": "user@gmail.com", "password": "password"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_login_user(client: TestClient, create_user):
    TEST_PASSWORD = "password"
    user = create_user(email="user@gmail.com", password=TEST_PASSWORD)
    response = client.post(
        LOGIN_URL, json={"email": user.email, "password": TEST_PASSWORD}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is not None
    json = response.json()
    assert json.get("accessToken") is not None
    assert json.get("tokenType") is not None
    assert json.get("user") == {"email": user.email, "admin": False}