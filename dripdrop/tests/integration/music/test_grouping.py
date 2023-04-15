from fastapi import status
from httpx import AsyncClient

GROUPING_URL = "/api/music/grouping"


async def test_grouping_when_not_logged_in(client: AsyncClient):
    response = await client.get(
        GROUPING_URL,
        params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_grouping_with_invalid_video_url(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        GROUPING_URL, params={"video_url": "https://invalidurl"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_grouping_with_valid_video_url(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        GROUPING_URL,
        params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"grouping": "Food Dip"}
