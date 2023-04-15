from fastapi import status
from httpx import AsyncClient

CREATE_URL = "/api/music/jobs/create"


async def test_creating_job_when_not_logged_in(client: AsyncClient, test_video_url):
    response = await client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "video_url": test_video_url,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_creating_job_with_file_and_video_url(
    client: AsyncClient,
    create_and_login_user,
    test_audio_file,
    test_video_url,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
            "video_url": test_video_url,
        },
        files={
            "file": ("dripdrop.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_creating_job_with_no_file_and_no_video_url(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.post(
        CREATE_URL,
        data={
            "title": "title",
            "artist": "artist",
            "album": "album",
            "grouping": "grouping",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
