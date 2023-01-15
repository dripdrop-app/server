from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME

CREATE_URL = "/api/auth/create"


def test_create_duplicate_user(client: TestClient, create_user):
    user = create_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL, json={"email": user.email, "password": "password"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user(client: TestClient):
    TEST_EMAIL = "user@gmail.com"
    response = client.post(
        CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is not None
    json = response.json()
    assert json.get("accessToken") is not None
    assert json.get("tokenType") is not None
    assert json.get("user") == {"email": TEST_EMAIL, "admin": False}
