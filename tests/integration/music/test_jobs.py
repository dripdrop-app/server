from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.settings import settings

JOBS_URL = "/api/music/jobs"


def test_jobs_when_not_logged_in(client: TestClient):
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_jobs_with_no_results(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"totalPages": 0, "jobs": []}


def test_jobs_with_out_of_range_page(
    client: TestClient, create_and_login_user, create_music_job
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    for i in range(2):
        create_music_job(
            id=str(i),
            email=user.email,
            title="title",
            artist="artist",
            album="album",
        )
    response = client.get(f"{JOBS_URL}/3/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_jobs_with_single_result(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    job = create_music_job(
        id="1",
        email=user.email,
        title="title",
        artist="artist",
        album="album",
    )
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "jobs": [
            {
                "id": job.id,
                "artworkUrl": job.artwork_url,
                "artworkFilename": job.artwork_filename,
                "originalFilename": job.original_filename,
                "filenameUrl": job.filename_url,
                "youtubeUrl": job.youtube_url,
                "downloadFilename": job.download_filename,
                "downloadUrl": job.download_url,
                "title": job.title,
                "artist": job.artist,
                "album": job.album,
                "grouping": job.grouping,
                "completed": job.completed,
                "failed": job.failed,
                "createdAt": job.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


def test_jobs_with_multiple_pages(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    jobs = list(
        map(
            lambda i: create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            ),
            range(5),
        )
    )
    jobs.sort(key=lambda job: job.created_at, reverse=True)
    response = client.get(f"{JOBS_URL}/2/2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 3,
        "jobs": list(
            map(
                lambda job: {
                    "id": job.id,
                    "artworkUrl": job.artwork_url,
                    "artworkFilename": job.artwork_filename,
                    "originalFilename": job.original_filename,
                    "filenameUrl": job.filename_url,
                    "youtubeUrl": job.youtube_url,
                    "downloadFilename": job.download_filename,
                    "downloadUrl": job.download_url,
                    "title": job.title,
                    "artist": job.artist,
                    "album": job.album,
                    "grouping": job.grouping,
                    "completed": job.completed,
                    "failed": job.failed,
                    "createdAt": job.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                },
                jobs[2:4],
            )
        ),
    }


def test_jobs_with_deleted_jobs(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    jobs = list(
        map(
            lambda i: create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
                deleted_at=datetime.now(tz=settings.timezone) if i % 2 else None,
            ),
            range(4),
        )
    )
    jobs = list(filter(lambda job: not job.deleted_at, jobs))
    jobs.sort(key=lambda job: job.created_at, reverse=True)
    response = client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "jobs": list(
            map(
                lambda job: {
                    "id": job.id,
                    "artworkUrl": job.artwork_url,
                    "artworkFilename": job.artwork_filename,
                    "originalFilename": job.original_filename,
                    "filenameUrl": job.filename_url,
                    "youtubeUrl": job.youtube_url,
                    "downloadFilename": job.download_filename,
                    "downloadUrl": job.download_url,
                    "title": job.title,
                    "artist": job.artist,
                    "album": job.album,
                    "grouping": job.grouping,
                    "completed": job.completed,
                    "failed": job.failed,
                    "createdAt": job.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                },
                jobs,
            )
        ),
    }


def test_jobs_only_for_logged_in_user(
    client: TestClient, create_and_login_user, create_user, create_music_job
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    other_user = create_user(email="other@gmail.com", password="password")
    job = create_music_job(
        id="1",
        email=user.email,
        title="title_1",
        artist="artist",
        album="album",
    )
    create_music_job(
        id="2",
        email=other_user.email,
        title="title_2",
        artist="artist",
        album="album",
    )
    response = client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "jobs": [
            {
                "id": job.id,
                "artworkUrl": job.artwork_url,
                "artworkFilename": job.artwork_filename,
                "originalFilename": job.original_filename,
                "filenameUrl": job.filename_url,
                "youtubeUrl": job.youtube_url,
                "downloadFilename": job.download_filename,
                "downloadUrl": job.download_url,
                "title": job.title,
                "artist": job.artist,
                "album": job.album,
                "grouping": job.grouping,
                "completed": job.completed,
                "failed": job.failed,
                "createdAt": job.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


def test_jobs_are_in_descending_order(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    jobs = list(
        map(
            lambda i: create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            ),
            range(4),
        )
    )
    jobs.sort(key=lambda job: job.created_at, reverse=True)
    response = client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "jobs": list(
            map(
                lambda job: {
                    "id": job.id,
                    "artworkUrl": job.artwork_url,
                    "artworkFilename": job.artwork_filename,
                    "originalFilename": job.original_filename,
                    "filenameUrl": job.filename_url,
                    "youtubeUrl": job.youtube_url,
                    "downloadFilename": job.download_filename,
                    "downloadUrl": job.download_url,
                    "title": job.title,
                    "artist": job.artist,
                    "album": job.album,
                    "grouping": job.grouping,
                    "completed": job.completed,
                    "failed": job.failed,
                    "createdAt": job.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                },
                jobs,
            )
        ),
    }
