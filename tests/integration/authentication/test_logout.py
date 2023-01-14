from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME

LOGIN_URL = "/api/auth/login"
LOGOUT_URL = "/api/auth/logout"
SESSION_URL = "/api/auth/session"


def test_logout_when_not_logged_in(client: TestClient):
    response = client.get(LOGOUT_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_when_logged_in(client: TestClient, create_user):
    TEST_EMAIL = "user@gmail.com"
    TEST_PASSWORD = "password"
    create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
    response = client.post(
        LOGIN_URL, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(LOGOUT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is None
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
