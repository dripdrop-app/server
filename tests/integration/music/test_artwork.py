import pytest
from fastapi import status
from fastapi.testclient import TestClient

ARTWORK_URL = "/api/music/artwork"


@pytest.mark.noauth
def test_artwork_when_not_logged_in(
    client: TestClient, test_image_url, clean_test_s3_folders
):
    response = client.get(
        ARTWORK_URL,
        params={"artwork_url": test_image_url},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    clean_test_s3_folders()


def test_artwork_with_invalid_url(client: TestClient):
    response = client.get(ARTWORK_URL, params={"artwork_url": "https://invalidurl"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_artwork_with_valid_image_url(client: TestClient, test_image_url):
    response = client.get(
        ARTWORK_URL,
        params={"artwork_url": test_image_url},
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["artworkUrl"] == test_image_url


def test_artwork_with_valid_soundcloud_url(client: TestClient):
    response = client.get(
        ARTWORK_URL,
        params={
            "artwork_url": "https://soundcloud.com/badbunny15/bad-bunny-buscabulla-andrea"
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert (
        json["artworkUrl"]
        == "https://i1.sndcdn.com/artworks-ExnE7PpUZSJl-0-t500x500.jpg"
    )
