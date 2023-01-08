from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME

CREATE_URL = "/api/auth/create"


def test_create_duplicate_user(
    client: TestClient, create_user, test_email, test_password
):
    create_user(email=test_email, password=test_password)
    response = client.post(
        CREATE_URL, json={"email": test_email, "password": test_password}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user(
    client: TestClient, test_email, test_password, assert_user_auth_response
):
    response = client.post(
        CREATE_URL, json={"email": test_email, "password": test_password}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is not None
    assert_user_auth_response(json=response.json(), email=test_email, admin=False)
