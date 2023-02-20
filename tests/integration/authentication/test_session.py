from fastapi import status
from httpx import AsyncClient

CREATE_URL = "/api/auth/create"
LOGIN_URL = "/api/auth/login"
SESSION_URL = "/api/auth/session"


async def test_session_when_not_logged_in(client: AsyncClient):
    response = await client.get(SESSION_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_session_after_creating_account(client: AsyncClient):
    TEST_EMAIL = "user@gmail.com"
    response = await client.post(
        CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    response = await client.get(SESSION_URL)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("email") == TEST_EMAIL
    assert json.get("admin") is False


async def test_session_after_login(client: AsyncClient, create_and_login_user):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(SESSION_URL)
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("email") == user.email
    assert json.get("admin") is False
