import re
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
    json = response.json()
    assert json.get("title") is None
    assert json.get("artist") is None
    assert json.get("album") is None
    assert json.get("grouping") is None


def test_tags_with_a_mp3_without_tags(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = requests.get(
        "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/sample4.mp3"
    )
    assert response.status_code == status.HTTP_200_OK
    file = response.content
    response = client.post(TAGS_URL, files={"file": file})
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("title") is None
    assert json.get("artist") is None
    assert json.get("album") is None
    assert json.get("grouping") is None


def test_tags_with_a_valid_mp3_file(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = requests.get(
        "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/"
        + "test/Criminal%20Sinny%20&%20Fako.mp3"
    )
    assert response.status_code == status.HTTP_200_OK
    file = response.content
    response = client.post(TAGS_URL, files={"file": file})
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("title") == "Criminal"
    assert json.get("artist") == "Sinny & Fako"
    assert json.get("album") == "Criminal - Single"
    assert json.get("grouping") == "Tribal Trap"
    assert re.match(r"data:image/[a-zA-Z]+;base64,", json.get("artworkUrl")) is not None
