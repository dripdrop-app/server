from fastapi import status
from httpx import AsyncClient

OAUTH_URL = "/api/youtube/oauth"


async def test_get_oauth_link_when_not_logged_in(client: AsyncClient):
    response = await client.get(OAUTH_URL)
    response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_oauth_link(client: AsyncClient, create_and_login_user):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(OAUTH_URL)
    response.status_code == status.HTTP_200_OK
