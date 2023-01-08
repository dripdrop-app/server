from fastapi import status
from fastapi.testclient import TestClient


CREATE_URL = "/api/auth/create"
LOGIN_URL = "/api/auth/login"
SESSION_URL = "/api/auth/session"


def test_session_when_not_logged_in(client: TestClient):
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_session_after_creating_account(
    client: TestClient, test_email, test_password, assert_session_response
):
    response = client.post(
        CREATE_URL, json={"email": test_email, "password": test_password}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_200_OK
    assert_session_response(json=response.json(), email=test_email, admin=False)


def test_session_after_login(
    client: TestClient,
    create_and_login_user,
    test_email,
    test_password,
    assert_session_response,
):
    create_and_login_user(email=test_email, password=test_password)
    response = client.get(SESSION_URL)
    assert response.status_code == status.HTTP_200_OK
    assert_session_response(json=response.json(), email=test_email, admin=False)
