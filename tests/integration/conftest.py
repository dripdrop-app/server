import asyncio
import os
import pytest
import requests
import subprocess
import time
from datetime import datetime, timezone
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select, insert
from sqlalchemy.engine import create_engine, Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from dripdrop.app import app
from dripdrop.apps.authentication.app import password_context
from dripdrop.apps.authentication.models import User
from dripdrop.apps.music.models import MusicJob
from dripdrop.database import database
from dripdrop.dependencies import COOKIE_NAME
from dripdrop.models.base import Base
from dripdrop.services.audio_tag import AudioTagService
from dripdrop.services.boto3 import Boto3Service, boto3_service
from dripdrop.settings import settings


test_engine = create_engine(
    settings.test_database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)
async_test_engine = create_async_engine(
    settings.test_async_database_url, poolclass=NullPool, echo=False
)


# Fix found here https://github.com/pytest-dev/pytest-asyncio/issues/207
# Need to create a single event loop that all instances will use


@pytest.fixture(scope="session")
def client():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    with TestClient(app) as client:
        yield client
    loop.close()


@pytest.fixture(autouse=True)
def setup_database():
    database.async_session_maker.configure(bind=async_test_engine)
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def db():
    return test_engine.connect()


@pytest.fixture()
def run_worker():
    process = subprocess.Popen(
        ["python", "worker.py"],
        env={
            **os.environ,
            "ASYNC_DATABASE_URL": settings.test_async_database_url,
            "DATABASE_URL": settings.test_database_url,
        },
    )
    yield
    process.kill()
    while process.poll() is None:
        time.sleep(1)


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
def test_email():
    return "testuser@gmail.com"


@pytest.fixture
def test_password():
    return "testpassword"


@pytest.fixture
def test_image_file(test_image_url):
    response = requests.get(test_image_url)
    return response.content


@pytest.fixture
def test_audio_file(test_audio_file_url):
    response = requests.get(test_audio_file_url)
    return response.content


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
def create_user(db: Connection):
    def _create_user(email: str = ..., password: str = ..., admin=False):
        assert type(email) is str
        assert type(password) is str
        db.execute(
            insert(User).values(
                email=email, password=password_context.hash(password), admin=admin
            )
        )

    return _create_user


@pytest.fixture
def create_and_login_user(client: TestClient, create_user):
    def _create_and_login_user(email: str = ..., password: str = ..., admin=False):
        create_user(email, password, admin)
        response = client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None

    return _create_and_login_user


@pytest.fixture()
def create_default_user(create_and_login_user, test_email, test_password):
    def _create_default_user(admin=False):
        create_and_login_user(email=test_email, password=test_password, admin=admin)

    return _create_default_user


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


@pytest.fixture()
def check_job_completed(db: Connection, test_email):
    def _check_job_completed():
        results = db.execute(select(MusicJob).where(MusicJob.user_email == test_email))
        job: MusicJob | None = results.first()
        assert job is not None
        return job

    return _check_job_completed


@pytest.fixture()
def wait_for_running_job_to_complete(check_job_completed):
    def _wait_for_job_to_complete(timeout: int = ...):
        start_time = datetime.now()
        while True:
            job: MusicJob = check_job_completed()
            current_time = datetime.now()
            duration = current_time - start_time
            assert duration.seconds < timeout
            if job.completed or job.failed:
                break
            time.sleep(1)
        return job

    return _wait_for_job_to_complete


@pytest.fixture()
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
        job: MusicJob = wait_for_running_job_to_complete(timeout=240)
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

    return _assert_job


@pytest.fixture
def assert_session_response():
    def _assert_session_response(json: dict = ..., email: str = ..., admin: bool = ...):
        assert json.get("email") == email
        assert json.get("admin") == admin

    return _assert_session_response


@pytest.fixture
def assert_user_auth_response(assert_session_response):
    def _assert_user_auth_response(
        json: dict = ..., email: str = ..., admin: bool = ...
    ):
        assert "accessToken" in json
        assert "tokenType" in json
        assert "user" in json
        assert_session_response(json=json["user"], email=email, admin=admin)

    return _assert_user_auth_response


@pytest.fixture
def assert_jobs_response():
    def _assert_jobs_response(
        json: dict = ..., jobs_length: int = ..., total_pages: int = ...
    ):
        assert len(json["jobs"]) == jobs_length
        assert json.get("totalPages") == total_pages

    return _assert_jobs_response
