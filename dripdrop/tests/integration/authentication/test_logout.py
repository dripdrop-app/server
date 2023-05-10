from fastapi import status
from httpx import AsyncClient

from dripdrop.authentication.dependencies import COOKIE_NAME

LOGIN_URL = "/api/auth/login"
LOGOUT_URL = "/api/auth/logout"
SESSION_URL = "/api/auth/session"


async def test_logout_when_not_logged_in(client: AsyncClient):
    response = await client.get(LOGOUT_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_when_logged_in(client: AsyncClient, create_user):
    TEST_PASSWORD = "password"
    user = await create_user(email="user@gmail.com", password=TEST_PASSWORD)
    response = await client.post(
        LOGIN_URL, json={"email": user.email, "password": TEST_PASSWORD}
    )
    assert response.status_code == status.HTTP_200_OK
    response = await client.get(LOGOUT_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get(COOKIE_NAME, None) is None
    response = await client.get(SESSION_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
