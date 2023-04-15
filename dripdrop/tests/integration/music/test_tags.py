from fastapi import status
from httpx import AsyncClient

TAGS_URL = "/api/music/tags"


async def test_tags_when_not_logged_in(client: AsyncClient):
    response = await client.post(TAGS_URL, files={"file": b"test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_tags_with_an_invalid_file(
    client: AsyncClient, http_client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await http_client.get(
        "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
    )
    file = response.content
    assert response.status_code == status.HTTP_200_OK
    response = await client.post(TAGS_URL, files={"file": file})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": None,
        "artist": None,
        "album": None,
        "grouping": None,
        "artworkUrl": None,
    }


async def test_tags_with_a_mp3_without_tags(
    client: AsyncClient, http_client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await http_client.get(
        "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/sample4.mp3"
    )
    assert response.status_code == status.HTTP_200_OK
    file = response.content
    response = await client.post(TAGS_URL, files={"file": file})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": None,
        "artist": None,
        "album": None,
        "grouping": None,
        "artworkUrl": None,
    }


async def test_tags_with_a_valid_mp3_file(
    client: AsyncClient,
    http_client: AsyncClient,
    create_and_login_user,
    get_tags_from_file,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await http_client.get(
        "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/"
        + "test/Criminal%20Sinny%20&%20Fako.mp3"
    )
    assert response.status_code == status.HTTP_200_OK
    file = response.content
    with get_tags_from_file(file=file) as tags:
        response = await client.post(TAGS_URL, files={"file": file})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "title": "Criminal",
            "artist": "Sinny & Fako",
            "album": "Criminal - Single",
            "grouping": "Tribal Trap",
            "artworkUrl": tags.get_artwork_as_base64(),
        }
