import base64
import io
import os
import pytest
import requests
import subprocess
import time
from datetime import datetime, timezone
from fastapi import status
from sqlalchemy import select, insert
from sqlalchemy.engine import Connection

from dripdrop.apps.music.models import MusicJob
from dripdrop.services.audio_tag import AudioTagService
from dripdrop.services.boto3 import boto3_service
from dripdrop.settings import settings


@pytest.fixture(autouse=True)
def create_default_user(create_and_login_user, test_email, test_password, request):
    if "noauth" in request.keywords:
        return
    create_and_login_user(test_email, test_password, admin=False)


@pytest.fixture
def clean_test_s3_folders():
    def _clean_test_s3_folders():
        try:
            for keys in boto3_service.list_objects():
                for key in keys:
                    if key.startswith("test"):
                        continue
                    boto3_service.delete_file(filename=key)
        except Exception as e:
            print(e)
            pass

    return _clean_test_s3_folders


@pytest.fixture
def run_worker(clean_test_s3_folders):
    clean_test_s3_folders()
    process = subprocess.Popen(
        ["python", "worker.py"],
        env={
            **os.environ,
            "ASYNC_DATABASE_URL": settings.test_async_database_url,
            "DATABASE_URL": settings.test_database_url,
        },
    )
    yield process
    process.kill()
    while process.poll() is None:
        time.sleep(1)
    clean_test_s3_folders()


@pytest.fixture
def test_image_url():
    return "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"


@pytest.fixture
def test_audio_file_url():
    return "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/07%20tun%20suh.mp3"


@pytest.fixture
def test_youtube_url():
    return "https://www.youtube.com/watch?v=wX49jNyqq04"


@pytest.fixture
def test_image_file(test_image_url):
    response = requests.get(test_image_url)
    assert response.status_code == status.HTTP_200_OK
    return response.content


@pytest.fixture
def test_audio_file(test_audio_file_url):
    response = requests.get(test_audio_file_url)
    assert response.status_code == status.HTTP_200_OK
    return response.content


@pytest.fixture
def test_base64_image(test_image_file):
    buffer = io.BytesIO(test_image_file)
    base64_string = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{base64_string}"


@pytest.fixture
def test_file_params():
    return {
        "title": "test",
        "artist": "test artist",
        "album": "test album",
        "grouping": "test grouping",
    }


@pytest.fixture
def test_music_job(test_email, test_file_params):
    return {
        "id": "testid",
        "email": test_email,
        **test_file_params,
    }


@pytest.fixture
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


@pytest.fixture
def wait_for_running_job_to_complete(db: Connection, test_email, function_timeout):
    def _check_job():
        results = db.execute(select(MusicJob).where(MusicJob.user_email == test_email))
        job: MusicJob | None = results.first()
        assert job is not None
        if job.completed or job.failed:
            return job

    def _wait_for_job_to_complete(timeout: int = ...):
        return function_timeout(timeout=timeout, function=_check_job)

    return _wait_for_job_to_complete


@pytest.fixture
def assert_job(wait_for_running_job_to_complete):
    def _assert_job(
        title: str = ...,
        artist: str = ...,
        album: str = ...,
        grouping: str | None = None,
        artwork: bytes | None = None,
        completed: bool | None = None,
        failed: bool | None = None,
    ):
        job: MusicJob = wait_for_running_job_to_complete(timeout=60)
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

    return _assert_job


@pytest.fixture
def assert_jobs_response():
    def _assert_jobs_response(
        json: dict = ..., jobs_length: int = ..., total_pages: int = ...
    ):
        assert len(json["jobs"]) == jobs_length
        assert json.get("totalPages") == total_pages

    return _assert_jobs_response


@pytest.fixture
def assert_tag_response():
    def _assert_tag_response(json=..., title=..., artist=..., album=..., grouping=...):
        assert json["title"] == title
        assert json["artist"] == artist
        assert json["album"] == album
        assert json["grouping"] == grouping

    return _assert_tag_response
