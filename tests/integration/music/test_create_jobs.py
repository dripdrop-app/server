from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"


def test_creating_job_when_not_logged_in(client: TestClient, test_youtube_url):
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "youtube_url": test_youtube_url,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_creating_job_with_file_and_youtube_url(
    client: TestClient,
    create_and_login_user,
    test_audio_file,
    test_youtube_url,
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "youtube_url": test_youtube_url,
        },
        files={
            "file": ("dripdrop.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_creating_job_with_no_file_and_no_youtube_url(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
