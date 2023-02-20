from fastapi import status
from httpx import AsyncClient

CREATE_URL = "/api/music/jobs/create"
DELETE_URL = "/api/music/jobs/delete"


async def test_deleting_job_when_not_logged_in(client: AsyncClient):
    response = await client.delete(DELETE_URL, params={"job_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_deleting_non_existent_job(client: AsyncClient, create_and_login_user):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.delete(DELETE_URL, params={"job_id": "1"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_deleting_failed_job(
    client: AsyncClient, create_and_login_user, create_music_job
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    job = await create_music_job(
        id="1",
        email=user.email,
        title="title",
        artist="artist",
        album="album",
        failed=True,
    )
    response = await client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK


async def test_deleting_file_job(
    client: AsyncClient,
    http_client: AsyncClient,
    create_and_login_user,
    test_audio_file,
    get_completed_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.post(
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
    job = await get_completed_job(email=user.email)
    response = await client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK
    response = await http_client.get(job.filename_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_deleting_file_job_with_uploaded_artwork(
    client: AsyncClient,
    http_client: AsyncClient,
    create_and_login_user,
    test_audio_file,
    test_base64_image,
    get_completed_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.post(
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
    job = await get_completed_job(email=user.email)
    response = await client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK
    response = await http_client.get(job.filename_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = await http_client.get(job.artwork_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_deleting_youtube_job(
    client: AsyncClient, create_and_login_user, test_video_url, get_completed_job
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
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
    assert response.status_code == status.HTTP_201_CREATED
    job = await get_completed_job(email=user.email)
    response = await client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK


async def test_deleting_youtube_job_with_artwork(
    client: AsyncClient,
    http_client: AsyncClient,
    create_and_login_user,
    test_video_url,
    test_base64_image,
    get_completed_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.post(
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
    job = await get_completed_job(email=user.email)
    response = await client.delete(DELETE_URL, params={"job_id": job.id})
    assert response.status_code == status.HTTP_200_OK
    response = await http_client.get(job.artwork_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
