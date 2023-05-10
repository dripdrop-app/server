from fastapi import status
from httpx import AsyncClient

from dripdrop.authentication.dependencies import COOKIE_NAME

LOGIN_URL = "/api/auth/login"


async def test_login_with_incorrect_password(client: AsyncClient, create_user):
    user = await create_user(email="user@gmail.com", password="password")
    response = await client.post(
        LOGIN_URL, json={"email": user.email, "password": "incorrectpassword"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_login_with_nonexistent_email(client: AsyncClient):
    response = await client.post(
        LOGIN_URL, json={"email": "user@gmail.com", "password": "password"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_login_user(client: AsyncClient, create_user):
    TEST_PASSWORD = "password"
    user = await create_user(email="user@gmail.com", password=TEST_PASSWORD)
    response = await client.post(
        LOGIN_URL, json={"email": user.email, "password": TEST_PASSWORD}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is not None
    json = response.json()
    assert json.get("accessToken") is not None
    assert json.get("tokenType") is not None
    assert json.get("user") == {"email": user.email, "admin": False}
