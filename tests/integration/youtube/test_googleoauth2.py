from fastapi import status
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from dripdrop.services.google_api import google_api_service
from dripdrop.rq import queue

ACCOUNT_URL = "/api/youtube/account"
GOOGLEOAUTH2_URL = "/api/youtube/googleoauth2"


def test_googleoauth2_when_not_logged_in(client: TestClient):
    response = client.get(GOOGLEOAUTH2_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_googleoauth2_with_error(client: TestClient, create_and_login_user):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(
        GOOGLEOAUTH2_URL,
        params={
            "state": user.email,
            "code": "random_code",
            "error": "Failed to get access token",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_googleoauth2_with_user_with_no_google_account(
    monkeypatch: MonkeyPatch, client: TestClient, create_and_login_user
):
    def mock_get_oauth_tokens(url: str = ..., code: str = ...):
        return {
            "refresh_token": "new_token",
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

    def mock_get_user_email(code: str = ...):
        return "google@gmail.com"

    monkeypatch.setattr(google_api_service, "get_oauth_tokens", mock_get_oauth_tokens)
    monkeypatch.setattr(google_api_service, "get_user_email", mock_get_user_email)
    monkeypatch.setattr(queue, "enqueue", lambda *args, **kwargs: None)
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(
        GOOGLEOAUTH2_URL,
        params={
            "state": user.email,
            "error": None,
            "code": "random_code",
        },
    )
    # Response redirects to react app, but this doesn't exist in tests
    response = client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {"email": "google@gmail.com", "refresh": False}


def test_googleoauth2_with_user_with_google_account(
    monkeypatch: MonkeyPatch,
    client: TestClient,
    create_and_login_user,
    create_google_account,
):
    def mock_get_oauth_tokens(url: str = ..., code: str = ...):
        return {
            "refresh_token": "new_token",
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

    def mock_get_user_email(code: str = ...):
        return "google@gmail.com"

    monkeypatch.setattr(google_api_service, "get_oauth_tokens", mock_get_oauth_tokens)
    monkeypatch.setattr(google_api_service, "get_user_email", mock_get_user_email)
    monkeypatch.setattr(queue, "enqueue", lambda *args, **kwargs: None)
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_account = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access_token",
        refresh_token="old_token",
        expires=1000,
    )
    # Response redirects to react app, but this doesn't exist in tests
    response = client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {"email": google_account.email, "refresh": False}
