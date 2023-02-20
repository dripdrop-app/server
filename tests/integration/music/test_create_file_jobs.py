from fastapi import status
from httpx import AsyncClient

CREATE_URL = "/api/music/jobs/create"


async def test_creating_file_job_with_invalid_content_type(
    client: AsyncClient, create_and_login_user, test_audio_file
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
        files={
            "file": ("tun suh.mp3", test_audio_file, "image/png"),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_creating_file_job_with_invalid_file(
    client: AsyncClient,
    create_and_login_user,
    test_image_file,
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
            "file": ("dripdrop.mp3", test_image_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = await get_completed_job(email=user.email)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is False
    assert job.failed is True


async def test_creating_file_job_with_valid_file(
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
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    assert job.filename_url is not None
    response = await http_client.get(job.filename_url)
    assert response.status_code == status.HTTP_200_OK


async def test_creating_file_job_with_valid_file_and_artwork_url(
    client: AsyncClient,
    http_client: AsyncClient,
    create_and_login_user,
    test_audio_file,
    test_image_url,
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
            "artwork_url": test_image_url,
        },
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    job = await get_completed_job(email=user.email)
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    assert job.filename_url is not None
    response = await http_client.get(job.filename_url)
    assert response.status_code == status.HTTP_200_OK
    assert job.download_url is not None
    response = await http_client.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK


async def test_creating_file_job_with_valid_file_and_base64_artwork(
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
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    assert job.filename_url is not None
    response = await http_client.get(job.filename_url)
    assert response.status_code == status.HTTP_200_OK
    assert job.artwork_url is not None
    response = await http_client.get(job.artwork_url)
    assert response.status_code == status.HTTP_200_OK
    assert job.download_url is not None
    response = await http_client.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK
