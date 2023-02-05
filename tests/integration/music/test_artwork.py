import re
from fastapi import status
from fastapi.testclient import TestClient

ARTWORK_URL = "/api/music/artwork"


def test_artwork_when_not_logged_in(client: TestClient):
    response = client.get(
        ARTWORK_URL,
        params={"artwork_url": "https://testimage.jpeg"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_artwork_with_invalid_url(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(ARTWORK_URL, params={"artwork_url": "https://invalidurl"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_artwork_with_valid_image_url(
    client: TestClient, create_and_login_user, test_image_url
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(
        ARTWORK_URL,
        params={"artwork_url": test_image_url},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"artworkUrl": test_image_url}


def test_artwork_with_valid_soundcloud_url(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(
        ARTWORK_URL,
        params={
            "artwork_url": "https://soundcloud.com/badbunny15/bad-bunny-buscabulla-andrea"
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    artwork_url = json.get("artworkUrl")
    assert (
        re.match(
            r"https:\/\/i1\.sndcdn\.com\/artworks-[a-zA-Z0-9]+-0-t500x500\.jpg",
            artwork_url,
        )
        is not None
    )
