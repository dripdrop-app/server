import requests
from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"
DELETE_URL = "/api/music/jobs/delete"


def test_deleting_job_when_not_logged_in(client: TestClient):
    response = client.delete(DELETE_URL, params={"job_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_deleting_non_existent_job(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.delete(DELETE_URL, params={"job_id": "1"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_deleting_failed_job(
    client: TestClient, create_and_login_user, create_music_job
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    job = create_music_job(
        id="1",
        email=user.email,
        title="title",
        artist="artist",
        album="album",
        failed=True,
    )
    response = client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK


def test_deleting_file_job(
    client: TestClient,
    create_and_login_user,
    test_audio_file,
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
        },
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    response = client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK
    response = requests.get(job.filename_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_deleting_file_job_with_uploaded_artwork(
    client: TestClient,
    create_and_login_user,
    test_audio_file,
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
            "artwork_url": test_base64_image,
        },
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    response = client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK
    response = requests.get(job.filename_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = requests.get(job.artwork_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_deleting_youtube_job(
    client: TestClient, create_and_login_user, test_video_url, get_completed_job
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    response = client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "video_url": test_video_url,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    response = client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK


def test_deleting_youtube_job_with_artwork(
    client: TestClient,
    create_and_login_user,
    test_video_url,
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
            "video_url": test_video_url,
            "artwork_url": test_base64_image,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = get_completed_job(email=user.email)
    response = client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK
    response = requests.get(job.artwork_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
