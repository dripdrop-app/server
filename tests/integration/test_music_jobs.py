import os
import pytest
import requests
import time
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
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


class MusicJobEndpoints:
    base_url = "/api/music/jobs"
    jobs = f"{base_url}/1/1"
    listen = f"{base_url}/listen"
    create_job = f"{base_url}/create"
    delete_job = f"{base_url}/delete"


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
