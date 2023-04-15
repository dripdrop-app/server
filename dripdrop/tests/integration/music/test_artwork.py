import re
from fastapi import status
from httpx import AsyncClient

ARTWORK_URL = "/api/music/artwork"


async def test_artwork_when_not_logged_in(client: AsyncClient):
    response = await client.get(
        ARTWORK_URL,
        params={"artwork_url": "https://testimage.jpeg"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_artwork_with_invalid_url(client: AsyncClient, create_and_login_user):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        ARTWORK_URL, params={"artwork_url": "https://invalidurl"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_artwork_with_valid_image_url(
    client: AsyncClient, create_and_login_user, test_image_url
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        ARTWORK_URL,
        params={"artwork_url": test_image_url},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"resolvedArtworkUrl": test_image_url}


async def test_artwork_with_valid_soundcloud_url(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        ARTWORK_URL,
        params={
            "artwork_url": "https://soundcloud.com/badbunny15/bad-bunny-buscabulla-andrea"
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    resolved_artwork_url = json.get("resolvedArtworkUrl")
    assert (
        re.match(
            r"https:\/\/i1\.sndcdn\.com\/artworks-[a-zA-Z0-9]+-0-t500x500\.jpg",
            resolved_artwork_url,
        )
        is not None
    )