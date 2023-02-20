from fastapi import status
from httpx import AsyncClient
from pytest import MonkeyPatch

from dripdrop.services.google_api import google_api
from dripdrop import rq

ACCOUNT_URL = "/api/youtube/account"
GOOGLEOAUTH2_URL = "/api/youtube/googleoauth2"


async def test_googleoauth2_when_not_logged_in(client: AsyncClient):
    response = await client.get(GOOGLEOAUTH2_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_googleoauth2_with_error(client: AsyncClient, create_and_login_user):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        GOOGLEOAUTH2_URL,
        params={
            "state": user.email,
            "code": "random_code",
            "error": "Failed to get access token",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_googleoauth2_with_user_with_no_google_account(
    monkeypatch: MonkeyPatch, client: AsyncClient, create_and_login_user
):
    async def mock_get_oauth_tokens(url: str = ..., code: str = ...):
        return {
            "refresh_token": "new_token",
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

    async def mock_get_user_email(code: str = ...):
        return "google@gmail.com"

    async def mock_enqueue(*args, **kwargs):
        return None

    monkeypatch.setattr(google_api, "get_oauth_tokens", mock_get_oauth_tokens)
    monkeypatch.setattr(google_api, "get_user_email", mock_get_user_email)
    monkeypatch.setattr(rq, "enqueue", mock_enqueue)
    user = await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        GOOGLEOAUTH2_URL,
        params={
            "state": user.email,
            "error": None,
            "code": "random_code",
        },
    )
    # Response redirects to react app, but this doesn't exist in tests
    response = await client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"email": "google@gmail.com", "refresh": False}


async def test_googleoauth2_with_user_with_google_account(
    monkeypatch: MonkeyPatch,
    client: AsyncClient,
    create_and_login_user,
    create_google_account,
):
    async def mock_get_oauth_tokens(url: str = ..., code: str = ...):
        return {
            "refresh_token": "new_token",
            "access_token": "new_access_token",
            "expires_in": 3600,
        }

    async def mock_get_user_email(code: str = ...):
        return "google@gmail.com"

    async def mock_enqueue(*args, **kwargs):
        return None

    monkeypatch.setattr(google_api, "get_oauth_tokens", mock_get_oauth_tokens)
    monkeypatch.setattr(google_api, "get_user_email", mock_get_user_email)
    monkeypatch.setattr(rq, "enqueue", mock_enqueue)
    user = await create_and_login_user(email="user@gmail.com", password="password")
    google_account = await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access_token",
        refresh_token="old_token",
        expires=1000,
    )
    # Response redirects to react app, but this doesn't exist in tests
    response = await client.get(ACCOUNT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"email": google_account.email, "refresh": False}
