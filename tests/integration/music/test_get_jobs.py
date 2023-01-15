from datetime import datetime, timezone
from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.settings import settings

JOBS_URL = "/api/music/jobs"


def test_get_jobs_when_not_logged_in(client: TestClient):
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_jobs_with_no_results(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_jobs_with_out_of_range_page(
    client: TestClient, create_and_login_user, create_music_job
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    for i in range(2):
        create_music_job(
            id=i,
            email=user.email,
            title="title",
            artist="artist",
            album="album",
        )
    response = client.get(f"{JOBS_URL}/3/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_jobs_with_single_result(
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
    json = response.json()
    assert json.get("totalPages") == 1
    assert json.get("jobs") == [
        {
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
                tzinfo=settings.test_timezone
            ).isoformat(),
        }
    ]


def test_get_jobs_with_multiple_pages(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    jobs = list(
        map(
            lambda i: create_music_job(
                id=i,
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            ),
            range(5),
        )
    )
    response = client.get(f"{JOBS_URL}/2/2")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("totalPages") == 3
    assert json.get("jobs") == list(
        map(
            lambda i: {
                "artworkUrl": jobs[i].artwork_url,
                "artworkFilename": jobs[i].artwork_filename,
                "originalFilename": jobs[i].original_filename,
                "filenameUrl": jobs[i].filename_url,
                "youtubeUrl": jobs[i].youtube_url,
                "downloadFilename": jobs[i].download_filename,
                "downloadUrl": jobs[i].download_url,
                "title": jobs[i].title,
                "artist": jobs[i].artist,
                "album": jobs[i].album,
                "grouping": jobs[i].grouping,
                "completed": jobs[i].completed,
                "failed": jobs[i].failed,
                "createdAt": jobs[i]
                .created_at.replace(tzinfo=settings.test_timezone)
                .isoformat(),
            },
            range(2, 0, -1),
        )
    )


def test_get_jobs_with_deleted_jobs(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    jobs = list(
        map(
            lambda i: create_music_job(
                id=i,
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
                deleted_at=datetime.now(timezone.utc) if i % 2 else None,
            ),
            range(4),
        )
    )
    response = client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("totalPages") == 1
    assert json.get("jobs") == list(
        map(
            lambda i: {
                "artworkUrl": jobs[i].artwork_url,
                "artworkFilename": jobs[i].artwork_filename,
                "originalFilename": jobs[i].original_filename,
                "filenameUrl": jobs[i].filename_url,
                "youtubeUrl": jobs[i].youtube_url,
                "downloadFilename": jobs[i].download_filename,
                "downloadUrl": jobs[i].download_url,
                "title": jobs[i].title,
                "artist": jobs[i].artist,
                "album": jobs[i].album,
                "grouping": jobs[i].grouping,
                "completed": jobs[i].completed,
                "failed": jobs[i].failed,
                "createdAt": jobs[i]
                .created_at.replace(tzinfo=settings.test_timezone)
                .isoformat(),
            },
            range(2, -1, -2),
        )
    )


def test_get_jobs_only_for_logged_in_user(
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
    json = response.json()
    assert json.get("totalPages") == 1
    assert json.get("jobs") == [
        {
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
                tzinfo=settings.test_timezone
            ).isoformat(),
        }
    ]


def test_get_jobs_are_in_descending_order(
    client: TestClient,
    create_and_login_user,
    create_music_job,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    jobs = list(
        map(
            lambda i: create_music_job(
                id=i,
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
                deleted_at=datetime.now(timezone.utc) if i % 2 else None,
            ),
            range(4),
        )
    )
    response = client.get(f"{JOBS_URL}/1/4")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("totalPages") == 1
    jobs = json.get("jobs", [])
    for i in range(1, len(jobs)):
        assert jobs[i]["createdAt"] < jobs[i - 1]["createdAt"]
