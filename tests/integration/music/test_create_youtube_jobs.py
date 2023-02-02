import requests
from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"


def test_creating_youtube_job_with_invalid_youtube_url(
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
            "youtube_url": "https://www.youtube.com/invalidurl",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_creating_youtube_job_with_valid_youtube_url(
    client: TestClient,
    create_and_login_user,
    test_youtube_url,
    get_completed_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
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
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False


def test_creating_youtube_job_with_valid_youtube_url_and_artwork_url(
    client: TestClient,
    create_and_login_user,
    test_youtube_url,
    test_image_url,
    get_completed_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "youtube_url": test_youtube_url,
            "artwork_url": test_image_url,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    response = requests.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK


def test_creating_youtube_job_with_valid_youtube_url_and_base64_artwork(
    client: TestClient,
    create_and_login_user,
    test_youtube_url,
    test_base64_image,
    get_completed_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "youtube_url": test_youtube_url,
            "artwork_url": test_base64_image,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    response = requests.get(job.artwork_url)
    assert response.status_code == status.HTTP_200_OK
    response = requests.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK
