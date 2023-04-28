from fastapi import status
from httpx import AsyncClient

from dripdrop.apps.authentication.dependencies import COOKIE_NAME

CREATE_URL = "/api/auth/create"


async def test_create_duplicate_user(client: AsyncClient, create_user):
    user = await create_user(email="user@gmail.com", password="password")
    response = await client.post(
        CREATE_URL, json={"email": user.email, "password": "password"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_create_user(client: AsyncClient):
    TEST_EMAIL = "user@gmail.com"
    response = await client.post(
        CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is not None
    json = response.json()
    assert json.get("accessToken") is not None
    assert json.get("tokenType") is not None
    assert json.get("user") == {"email": TEST_EMAIL, "admin": False}
