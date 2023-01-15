import base64
import io
import os
import pytest
import requests
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from dripdrop.apps.music.models import MusicJob
from dripdrop.services.audio_tag import AudioTagService
from dripdrop.services.boto3 import boto3_service
from dripdrop.settings import settings


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
def create_music_job(session: Session):
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
        deleted_at: datetime | None = None,
    ):
        job = MusicJob(
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
            deleted_at=deleted_at,
        )
        session.add(job)
        session.commit()
        return job

    return _create_music_job


@pytest.fixture
def wait_for_running_job_to_complete(session: Session, function_timeout):
    def _wait_for_job_to_complete(email: str = ..., timeout: int = ...):
        def _check_job():
            results = session.scalars(
                select(MusicJob).where(MusicJob.user_email == email)
            )
            job: MusicJob | None = results.first()
            assert job is not None
            if job.completed or job.failed:
                return job

        return function_timeout(timeout=timeout, function=_check_job)

    return _wait_for_job_to_complete


@pytest.fixture
def get_tags_from_job():
    @contextmanager
    def _get_tags_from_job(job: MusicJob = ...):
        response = requests.get(job.download_url)
        assert response.status_code == status.HTTP_200_OK

        with open("test.mp3", "wb") as file:
            file.write(response.content)

        yield AudioTagService(file_path="test.mp3")
        os.remove("test.mp3")

    return _get_tags_from_job
