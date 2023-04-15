from fastapi import status
from httpx import AsyncClient

CREATE_URL = "/api/music/jobs/create"


async def test_creating_video_job_with_invalid_video_url(
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
            "video_url": "not_valid",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_creating_video_job_with_valid_video_url(
    client: AsyncClient,
    create_and_login_user,
    test_video_url,
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


async def test_creating_video_job_with_valid_video_url_and_artwork_url(
    client: AsyncClient,
    http_client: AsyncClient,
    create_and_login_user,
    test_video_url,
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
            "video_url": test_video_url,
            "artwork_url": test_image_url,
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
    response = await http_client.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK


async def test_creating_video_job_with_valid_video_url_and_base64_artwork(
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
    assert job.title == "title"
    assert job.artist == "artist"
    assert job.album == "album"
    assert job.grouping == "grouping"
    assert job.completed is True
    assert job.failed is False
    response = await http_client.get(job.artwork_url)
    assert response.status_code == status.HTTP_200_OK
    response = await http_client.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK
