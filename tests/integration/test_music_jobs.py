import os
import pytest
import requests
import time
from datetime import datetime, timezone
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select, insert
from sqlalchemy.engine import Connection

from dripdrop.apps.music.models import MusicJob
from dripdrop.services.boto3 import boto3_service, Boto3Service
from dripdrop.services.audio_tag import AudioTagService

from .conftest import TEST_EMAIL

TEST_IMAGE_URL = (
    "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
)
TEST_AUDIO_FILE_URL = (
    "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/07%20tun%20suh.mp3"
)
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=wX49jNyqq04"


@pytest.fixture()
def test_image_file():
    response = requests.get(TEST_IMAGE_URL)
    return response.content


@pytest.fixture()
def test_audio_file():
    response = requests.get(TEST_AUDIO_FILE_URL)
    return response.content


@pytest.fixture(autouse=True)
def create_user(create_default_user):
    pass


@pytest.fixture()
def create_music_job(db: Connection):
    def _create_music_job(
        id: str = ...,
        email: str = ...,
        artwork_url: str | None = None,
        artwork_filename: str | None = None,
        original_filename: str | None = None,
        filename_url: str | None = None,
        youtube_url: str | None = None,
        download_filename: str | None = None,
        download_url: str | None = None,
        title: str = ...,
        artist: str = ...,
        album: str = ...,
        grouping: str | None = None,
        completed: bool = False,
        failed: bool = False,
        deleted_at: datetime = None,
    ):
        db.execute(
            insert(MusicJob).values(
                id=id,
                user_email=email,
                artwork_url=artwork_url,
                artwork_filename=artwork_filename,
                original_filename=original_filename,
                filename_url=filename_url,
                youtube_url=youtube_url,
                download_filename=download_filename,
                download_url=download_url,
                title=title,
                artist=artist,
                album=album,
                grouping=grouping,
                completed=completed,
                failed=failed,
                created_at=datetime.now(timezone.utc),
                deleted_at=deleted_at,
            )
        )

    return _create_music_job


class MusicJobEndpoints:
    base_url = "/api/music/jobs"
    listen = f"{base_url}/listen"
    create_job = f"{base_url}/create"
    delete_job = f"{base_url}/delete"


def wait_for_job_completion(db: Connection = ...):
    job = None
    start_time = datetime.now()
    while True:
        results = db.execute(select(MusicJob).where(MusicJob.user_email == TEST_EMAIL))
        job: MusicJob | None = results.first()
        assert job is not None
        current_time = datetime.now()
        duration = current_time - start_time
        assert duration.seconds < 240
        if job.completed or job.failed:
            break
        time.sleep(1)
    return job


def assert_job(
    db: Connection = ...,
    title: str = ...,
    artist: str = ...,
    album: str = ...,
    grouping: str | None = None,
    artwork: bytes | None = None,
    completed: bool | None = None,
    failed: bool | None = None,
):
    job = wait_for_job_completion(db=db)
    if completed is not None:
        assert job.completed == completed
    if failed is not None:
        assert job.failed == failed
    if not failed:
        response = requests.get(job.download_url)
        assert response.status_code == status.HTTP_200_OK

        with open("test.mp3", "wb") as file:
            file.write(response.content)

        audio_tag_service = AudioTagService("test.mp3")
        assert audio_tag_service.title == title
        assert audio_tag_service.artist == artist
        assert audio_tag_service.album == album
        if grouping:
            assert audio_tag_service.grouping == grouping
        if artwork:
            assert audio_tag_service.artwork is not None
            assert audio_tag_service.artwork.data == artwork
        os.remove("test.mp3")

    if job.original_filename:
        boto3_service.delete_file(
            bucket=Boto3Service.S3_MUSIC_BUCKET,
            filename=job.original_filename,
        )
    if job.download_filename:
        boto3_service.delete_file(
            bucket=Boto3Service.S3_MUSIC_BUCKET,
            filename=job.download_filename,
        )


test_file_params = {
    "title": "test",
    "artist": "test artist",
    "album": "test album",
    "grouping": "test grouping",
}


class TestCreateJob:
    def test_creating_job_with_file_and_youtube_url(
        self, client: TestClient, test_audio_file
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={**test_file_params, "youtube_url": TEST_YOUTUBE_URL},
            files={
                "file": ("dripdrop.mp3", test_audio_file, "audio/mpeg"),
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_job_with_no_file_and_no_youtube_url(self, client: TestClient):
        response = client.post(MusicJobEndpoints.create_job, data=test_file_params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateFileJob:
    def test_creating_file_job_with_invalid_content_type(
        self, client: TestClient, test_audio_file
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data=test_file_params,
            files={
                "file": ("tun suh.mp3", test_audio_file, "image/png"),
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_file_job_with_invalid_file(
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_image_file,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data=test_file_params,
            files={
                "file": ("dripdrop.mp3", test_image_file, "audio/mpeg"),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert_job(
            db=db,
            title=test_file_params["title"],
            artist=test_file_params["artist"],
            album=test_file_params["album"],
            grouping=test_file_params["grouping"],
            completed=False,
            failed=True,
        )

    def test_creating_file_job_with_valid_file(
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_audio_file,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data=test_file_params,
            files={
                "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert_job(
            db=db,
            title=test_file_params["title"],
            artist=test_file_params["artist"],
            album=test_file_params["album"],
            grouping=test_file_params["grouping"],
            completed=True,
            failed=False,
        )

    def test_creating_file_job_with_valid_file_and_artwork_url(
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_audio_file,
        test_image_file,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={**test_file_params, "artwork_url": TEST_IMAGE_URL},
            files={
                "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert_job(
            db=db,
            title=test_file_params["title"],
            artist=test_file_params["artist"],
            album=test_file_params["album"],
            grouping=test_file_params["grouping"],
            artwork=test_image_file,
            completed=True,
            failed=False,
        )


class TestCreateYoutubeJob:
    def test_creating_youtube_job_with_invalid_youtube_url(self, client: TestClient):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={
                **test_file_params,
                "youtube_url": "https://www.youtube.com/invalidurl",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_youtube_job_with_valid_youtube_url(
        self, client: TestClient, db: Connection, run_worker
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={**test_file_params, "youtube_url": TEST_YOUTUBE_URL},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert_job(
            db=db,
            title=test_file_params["title"],
            artist=test_file_params["artist"],
            album=test_file_params["album"],
            grouping=test_file_params["grouping"],
            completed=True,
            failed=False,
        )

    def test_creating_youtube_job_with_valid_youtube_url_and_artwork_url(
        self, client: TestClient, db: Connection, run_worker, test_image_file
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={
                **test_file_params,
                "youtube_url": TEST_YOUTUBE_URL,
                "artwork_url": TEST_IMAGE_URL,
            },
        )
        print(response.text)
        assert response.status_code == status.HTTP_201_CREATED
        assert_job(
            db=db,
            title=test_file_params["title"],
            artist=test_file_params["artist"],
            album=test_file_params["album"],
            grouping=test_file_params["grouping"],
            artwork=test_image_file,
            completed=True,
            failed=False,
        )


test_music_job = {
    "id": "testid",
    "email": TEST_EMAIL,
    **test_file_params,
}


class TestGetJobs:
    def assert_jobs_response(
        self, json: dict = ..., jobs_length: int = ..., total_pages: int = ...
    ):
        assert len(json["jobs"]) == jobs_length
        assert json.get("totalPages") == total_pages

    def test_get_jobs_with_no_results(self, client: TestClient):
        response = client.get(f"{MusicJobEndpoints.base_url}/1/10")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_jobs_with_out_of_range_page(
        self, client: TestClient, create_music_job
    ):
        for i in range(15):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
        response = client.get(f"{MusicJobEndpoints.base_url}/3/10")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_jobs_with_single_result(self, client: TestClient, create_music_job):
        create_music_job(**test_music_job)
        response = client.get(f"{MusicJobEndpoints.base_url}/1/10")
        assert response.status_code == status.HTTP_200_OK
        self.assert_jobs_response(json=response.json(), jobs_length=1, total_pages=1)

    def test_get_jobs_with_partial_page(self, client: TestClient, create_music_job):
        for i in range(15):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
        response = client.get(f"{MusicJobEndpoints.base_url}/1/20")
        assert response.status_code == status.HTTP_200_OK
        self.assert_jobs_response(json=response.json(), jobs_length=15, total_pages=1)

    def test_get_jobs_with_multiple_pages(self, client: TestClient, create_music_job):
        for i in range(20):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
        response = client.get(f"{MusicJobEndpoints.base_url}/1/10")
        assert response.status_code == status.HTTP_200_OK
        self.assert_jobs_response(json=response.json(), jobs_length=10, total_pages=2)

    def test_get_jobs_with_deleted_jobs(self, client: TestClient, create_music_job):
        for i in range(10):
            create_music_job(
                **{
                    **test_music_job,
                    "id": f"test_{i}",
                    "deleted_at": datetime.now(timezone.utc) if i % 2 == 0 else None,
                }
            )
        response = client.get(f"{MusicJobEndpoints.base_url}/1/5")
        assert response.status_code == status.HTTP_200_OK
        self.assert_jobs_response(json=response.json(), jobs_length=5, total_pages=1)

    def test_get_jobs_are_in_descending_order(
        self, client: TestClient, create_music_job
    ):
        for i in range(5):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
            time.sleep(1)
        response = client.get(f"{MusicJobEndpoints.base_url}/1/5")
        assert response.status_code == status.HTTP_200_OK
        self.assert_jobs_response(json=response.json(), jobs_length=5, total_pages=1)
        jobs = response.json()["jobs"]
        for i in range(1, len(jobs)):
            assert jobs[i]["createdAt"] < jobs[i - 1]["createdAt"]
