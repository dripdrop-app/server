from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME

LOGIN_URL = "/api/auth/login"


def test_login_with_incorrect_password(
    client: TestClient, create_user, test_email, test_password
):
    create_user(email=test_email, password=test_password)
    response = client.post(
        LOGIN_URL, json={"email": test_email, "password": "incorrectpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_with_non_existent_email(client: TestClient, test_email, test_password):
    response = client.post(
        LOGIN_URL, json={"email": test_email, "password": test_password}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_login_user(
    client: TestClient,
    create_user,
    test_email,
    test_password,
    assert_user_auth_response,
):
    create_user(email=test_email, password=test_password)
    response = client.post(
        LOGIN_URL, json={"email": test_email, "password": test_password}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is not None
    assert_user_auth_response(json=response.json(), email=test_email, admin=False)
