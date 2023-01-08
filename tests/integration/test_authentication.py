from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.dependencies import COOKIE_NAME


class AuthEndpoints:
    base_path = "/api/auth"
    create = f"{base_path}/create"
    login = f"{base_path}/login"
    session = f"{base_path}/session"
    logout = f"{base_path}/logout"


class TestCreate:
    def test_create_duplicate_user(
        self, client: TestClient, create_user, test_email, test_password
    ):
        create_user(email=test_email, password=test_password)
        response = client.post(
            AuthEndpoints.create, json={"email": test_email, "password": test_password}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user(
        self, client: TestClient, test_email, test_password, assert_user_auth_response
    ):
        response = client.post(
            AuthEndpoints.create, json={"email": test_email, "password": test_password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None
        assert_user_auth_response(json=response.json(), email=test_email, admin=False)


class TestLogin:
    def test_login_with_incorrect_password(
        self, client: TestClient, create_user, test_email, test_password
    ):
        create_user(email=test_email, password=test_password)
        response = client.post(
            AuthEndpoints.login,
            json={"email": test_email, "password": "incorrectpassword"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_non_existent_email(
        self, client: TestClient, test_email, test_password
    ):
        response = client.post(
            AuthEndpoints.login,
            json={"email": test_email, "password": test_password},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_login_user(
        self,
        client: TestClient,
        create_user,
        test_email,
        test_password,
        assert_user_auth_response,
    ):
        create_user(email=test_email, password=test_password)
        response = client.post(
            AuthEndpoints.login, json={"email": test_email, "password": test_password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None
        assert_user_auth_response(json=response.json(), email=test_email, admin=False)


class TestSession:
    def test_session_when_not_logged_in(self, client: TestClient):
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_session_after_creating_account(
        self, client: TestClient, test_email, test_password, assert_session_response
    ):
        response = client.post(
            AuthEndpoints.create, json={"email": test_email, "password": test_password}
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_200_OK
        assert_session_response(json=response.json(), email=test_email, admin=False)

    def test_session_after_login(
        self,
        client: TestClient,
        create_user,
        test_email,
        test_password,
        assert_session_response,
    ):
        create_user(email=test_email, password=test_password)
        response = client.post(
            AuthEndpoints.login, json={"email": test_email, "password": test_password}
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_200_OK
        assert_session_response(json=response.json(), email=test_email, admin=False)


class TestLogout:
    def test_logout_when_not_logged_in(self, client: TestClient):
        response = client.get(AuthEndpoints.logout)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_when_logged_in(
        self,
        client: TestClient,
        create_user,
        test_email,
        test_password,
    ):
        create_user(email=test_email, password=test_password)
        response = client.post(
            AuthEndpoints.login, json={"email": test_email, "password": test_password}
        )
        assert response.status_code == status.HTTP_200_OK
        response = client.get(AuthEndpoints.logout)
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is None
        response = client.get(AuthEndpoints.session)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
