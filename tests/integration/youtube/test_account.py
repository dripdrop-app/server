from fastapi import status
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from dripdrop.services.google_api import google_api_service

ACCOUNT_URL = "/api/youtube/account"


def test_get_account_when_not_logged_in(client: TestClient):
    response = client.get(ACCOUNT_URL)
    response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_account_with_no_google_account(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_account_with_expired_token(
    monkeypatch: MonkeyPatch,
    client: TestClient,
    create_and_login_user,
    create_google_account,
):
    def mock_refresh_token(refresh_token: str = ...):
        raise Exception("No refresh")

    monkeypatch.setattr(google_api_service, "refresh_access_token", mock_refresh_token)
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_account = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="old_token",
        expires=0,
    )
    response = client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"email": google_account.email, "refresh": True}


def test_get_account(
    monkeypatch: MonkeyPatch,
    client: TestClient,
    create_and_login_user,
    create_google_account,
):
    def mock_refresh_token(refresh_token: str = ...):
        return {
            "refresh_token": "new_token",
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

    monkeypatch.setattr(google_api_service, "refresh_access_token", mock_refresh_token)
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_account = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="old_access_token",
        refresh_token="old_token",
        expires=0,
    )
    response = client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"email": google_account.email, "refresh": False}
