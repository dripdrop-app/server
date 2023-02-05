import requests
from fastapi import status
from fastapi.testclient import TestClient

TAGS_URL = "/api/music/tags"


def test_tags_when_not_logged_in(client: TestClient):
    response = client.post(TAGS_URL, files={"file": b"test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_tags_with_an_invalid_file(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = requests.get(
        "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
    )
    file = response.content
    assert response.status_code == status.HTTP_200_OK
    response = client.post(TAGS_URL, files={"file": file})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": None,
        "artist": None,
        "album": None,
        "grouping": None,
        "artworkUrl": None,
    }


def test_tags_with_a_mp3_without_tags(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = requests.get(
        "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/sample4.mp3"
    )
    assert response.status_code == status.HTTP_200_OK
    file = response.content
    response = client.post(TAGS_URL, files={"file": file})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": None,
        "artist": None,
        "album": None,
        "grouping": None,
        "artworkUrl": None,
    }


def test_tags_with_a_valid_mp3_file(
    client: TestClient, create_and_login_user, get_tags_from_file
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = requests.get(
        "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/"
        + "test/Criminal%20Sinny%20&%20Fako.mp3"
    )
    assert response.status_code == status.HTTP_200_OK
    file = response.content
    with get_tags_from_file(file=file) as tags:
        response = client.post(TAGS_URL, files={"file": file})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "title": "Criminal",
            "artist": "Sinny & Fako",
            "album": "Criminal - Single",
            "grouping": "Tribal Trap",
            "artworkUrl": tags.get_artwork_as_base64(),
        }
