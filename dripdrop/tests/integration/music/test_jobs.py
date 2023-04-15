from datetime import datetime
from fastapi import status
from httpx import AsyncClient

from dripdrop.settings import settings

JOBS_URL = "/api/music/jobs"


async def test_jobs_when_not_logged_in(client: AsyncClient):
    response = await client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_jobs_with_no_results(client: AsyncClient, create_and_login_user):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"totalPages": 0, "musicJobs": []}


async def test_jobs_with_out_of_range_page(
    client: AsyncClient, create_and_login_user, create_music_job
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    for i in range(2):
        await create_music_job(
            id=str(i),
            email=user.email,
            title="title",
            artist="artist",
            album="album",
        )
    response = await client.get(f"{JOBS_URL}/3/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_jobs_with_single_result(
    client: AsyncClient,
    create_and_login_user,
    create_music_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    music_job = await create_music_job(
        id="1",
        email=user.email,
        title="title",
        artist="artist",
        album="album",
    )
    response = await client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "musicJobs": [
            {
                "id": music_job.id,
                "artworkUrl": music_job.artwork_url,
                "artworkFilename": music_job.artwork_filename,
                "originalFilename": music_job.original_filename,
                "filenameUrl": music_job.filename_url,
                "videoUrl": music_job.video_url,
                "downloadFilename": music_job.download_filename,
                "downloadUrl": music_job.download_url,
                "title": music_job.title,
                "artist": music_job.artist,
                "album": music_job.album,
                "grouping": music_job.grouping,
                "completed": music_job.completed,
                "failed": music_job.failed,
                "createdAt": music_job.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


async def test_jobs_with_multiple_pages(
    client: AsyncClient,
    create_and_login_user,
    create_music_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    music_jobs = []
    for i in range(5):
        music_jobs.append(
            await create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            )
        )
    music_jobs.sort(key=lambda music_job: music_job.created_at, reverse=True)
    response = await client.get(f"{JOBS_URL}/2/2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 3,
        "musicJobs": list(
            map(
                lambda music_job: {
                    "id": music_job.id,
                    "artworkUrl": music_job.artwork_url,
                    "artworkFilename": music_job.artwork_filename,
                    "originalFilename": music_job.original_filename,
                    "filenameUrl": music_job.filename_url,
                    "videoUrl": music_job.video_url,
                    "downloadFilename": music_job.download_filename,
                    "downloadUrl": music_job.download_url,
                    "title": music_job.title,
                    "artist": music_job.artist,
                    "album": music_job.album,
                    "grouping": music_job.grouping,
                    "completed": music_job.completed,
                    "failed": music_job.failed,
                    "createdAt": music_job.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                },
                music_jobs[2:4],
            )
        ),
    }


async def test_jobs_with_deleted_jobs(
    client: AsyncClient,
    create_and_login_user,
    create_music_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    music_jobs = []
    for i in range(4):
        music_jobs.append(
            await create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
                deleted_at=datetime.now(tz=settings.timezone) if i % 2 else None,
            )
        )
    music_jobs = list(filter(lambda music_job: not music_job.deleted_at, music_jobs))
    music_jobs.sort(key=lambda music_job: music_job.created_at, reverse=True)
    response = await client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "musicJobs": list(
            map(
                lambda music_job: {
                    "id": music_job.id,
                    "artworkUrl": music_job.artwork_url,
                    "artworkFilename": music_job.artwork_filename,
                    "originalFilename": music_job.original_filename,
                    "filenameUrl": music_job.filename_url,
                    "videoUrl": music_job.video_url,
                    "downloadFilename": music_job.download_filename,
                    "downloadUrl": music_job.download_url,
                    "title": music_job.title,
                    "artist": music_job.artist,
                    "album": music_job.album,
                    "grouping": music_job.grouping,
                    "completed": music_job.completed,
                    "failed": music_job.failed,
                    "createdAt": music_job.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                },
                music_jobs,
            )
        ),
    }


async def test_jobs_only_for_logged_in_user(
    client: AsyncClient, create_and_login_user, create_user, create_music_job
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    other_user = await create_user(email="other@gmail.com", password="password")
    music_job = await create_music_job(
        id="1",
        email=user.email,
        title="title_1",
        artist="artist",
        album="album",
    )
    await create_music_job(
        id="2",
        email=other_user.email,
        title="title_2",
        artist="artist",
        album="album",
    )
    response = await client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "musicJobs": [
            {
                "id": music_job.id,
                "artworkUrl": music_job.artwork_url,
                "artworkFilename": music_job.artwork_filename,
                "originalFilename": music_job.original_filename,
                "filenameUrl": music_job.filename_url,
                "videoUrl": music_job.video_url,
                "downloadFilename": music_job.download_filename,
                "downloadUrl": music_job.download_url,
                "title": music_job.title,
                "artist": music_job.artist,
                "album": music_job.album,
                "grouping": music_job.grouping,
                "completed": music_job.completed,
                "failed": music_job.failed,
                "createdAt": music_job.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


async def test_jobs_are_in_descending_order(
    client: AsyncClient,
    create_and_login_user,
    create_music_job,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    music_jobs = []
    for i in range(4):
        music_jobs.append(
            await create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            )
        )
    music_jobs.sort(key=lambda music_job: music_job.created_at, reverse=True)
    response = await client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "musicJobs": list(
            map(
                lambda music_job: {
                    "id": music_job.id,
                    "artworkUrl": music_job.artwork_url,
                    "artworkFilename": music_job.artwork_filename,
                    "originalFilename": music_job.original_filename,
                    "filenameUrl": music_job.filename_url,
                    "videoUrl": music_job.video_url,
                    "downloadFilename": music_job.download_filename,
                    "downloadUrl": music_job.download_url,
                    "title": music_job.title,
                    "artist": music_job.artist,
                    "album": music_job.album,
                    "grouping": music_job.grouping,
                    "completed": music_job.completed,
                    "failed": music_job.failed,
                    "createdAt": music_job.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                },
                music_jobs,
            )
        ),
    }
