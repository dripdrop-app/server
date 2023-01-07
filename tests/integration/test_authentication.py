from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME

from .conftest import TEST_EMAIL, TEST_PASSWORD


class AuthEndpoints:
    base_path = "/api/auth"
    create = f"{base_path}/create"
    login = f"{base_path}/login"
    session = f"{base_path}/session"
    logout = f"{base_path}/logout"


def check_session_response(json: dict = ..., email: str = ..., admin: bool = ...):
    assert "email" in json
    assert json["email"] == email
    assert "admin" in json
    assert json["admin"] is admin


def check_user_auth_response(json: dict = ..., email: str = ..., admin: bool = ...):
    assert "accessToken" in json
    assert "tokenType" in json
    assert "user" in json
    check_session_response(json=json["user"], email=email, admin=admin)


class TestCreate:
    def test_create_duplicate_user(self, client: TestClient, create_user):
        create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.post(
            AuthEndpoints.create, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user(self, client: TestClient):
        response = client.post(
            AuthEndpoints.create, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None
        check_user_auth_response(json=response.json(), email=TEST_EMAIL, admin=False)


class TestLogin:
    def test_login_with_incorrect_password(self, client: TestClient, create_user):
        create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.post(
            AuthEndpoints.login,
            json={"email": TEST_EMAIL, "password": "incorrectpassword"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_non_existent_email(self, client: TestClient):
        response = client.post(
            AuthEndpoints.login,
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_login_user(self, client: TestClient, create_user):
        create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.post(
            AuthEndpoints.login, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None
        check_user_auth_response(json=response.json(), email=TEST_EMAIL, admin=False)


class TestSession:
    def test_session_when_not_logged_in(self, client: TestClient):
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_session_after_creating_account(self, client: TestClient):
        response = client.post(
            AuthEndpoints.create, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_200_OK
        check_session_response(json=response.json(), email=TEST_EMAIL, admin=False)

    def test_session_after_login(self, client: TestClient, create_user):
        create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.post(
            AuthEndpoints.login, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_200_OK
        check_session_response(json=response.json(), email=TEST_EMAIL, admin=False)


class TestLogout:
    def test_logout_when_not_logged_in(self, client: TestClient):
        response = client.get(AuthEndpoints.logout)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_when_logged_in(self, client: TestClient, create_user):
        create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.post(
            AuthEndpoints.login, json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.get(AuthEndpoints.logout)
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is None
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
