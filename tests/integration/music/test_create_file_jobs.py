import requests
from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"


def test_creating_file_job_with_invalid_content_type(
    client: TestClient, create_and_login_user, test_audio_file
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
        files={
            "file": ("tun suh.mp3", test_audio_file, "image/png"),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_creating_file_job_with_invalid_file(
    client: TestClient,
    create_and_login_user,
    test_image_file,
    wait_for_running_job_to_complete,
    run_worker,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
        },
        files={
            "file": ("dripdrop.mp3", test_image_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = wait_for_running_job_to_complete(email=user.email, timeout=120)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is False
    assert job.failed is True


def test_creating_file_job_with_valid_file(
    client: TestClient,
    create_and_login_user,
    test_audio_file,
    wait_for_running_job_to_complete,
    run_worker,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
        },
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = wait_for_running_job_to_complete(email=user.email, timeout=120)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    assert job.filename_url is not None
    response = requests.get(job.filename_url)
    assert response.status_code == status.HTTP_200_OK


def test_creating_file_job_with_valid_file_and_artwork_url(
    client: TestClient,
    create_and_login_user,
    test_audio_file,
    test_image_url,
    wait_for_running_job_to_complete,
    run_worker,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "artwork_url": test_image_url,
        },
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = wait_for_running_job_to_complete(email=user.email, timeout=120)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    assert job.filename_url is not None
    response = requests.get(job.filename_url)
    assert response.status_code == status.HTTP_200_OK
    assert job.download_url is not None
    response = requests.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK


def test_creating_file_job_with_valid_file_and_base64_artwork(
    client: TestClient,
    create_and_login_user,
    test_audio_file,
    test_base64_image,
    wait_for_running_job_to_complete,
    run_worker,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "artwork_url": test_base64_image,
        },
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = wait_for_running_job_to_complete(email=user.email, timeout=120)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    assert job.filename_url is not None
    response = requests.get(job.filename_url)
    assert response.status_code == status.HTTP_200_OK
    assert job.artwork_url is not None
    response = requests.get(job.artwork_url)
    assert response.status_code == status.HTTP_200_OK
    assert job.download_url is not None
    response = requests.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK
