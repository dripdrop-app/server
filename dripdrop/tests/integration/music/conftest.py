import base64
import io
import os
import pytest
from contextlib import contextmanager
from datetime import datetime
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dripdrop.apps.music.models import MusicJob
from dripdrop.services import temp_files
from dripdrop.services.audio_tag import AudioTags


@pytest.fixture(scope="session")
def test_image_url():
    return "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"


@pytest.fixture(scope="session")
def test_audio_file_url():
    return "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/07%20tun%20suh.mp3"


@pytest.fixture(scope="session")
def test_video_url():
    return "https://vimeo.com/56282283"


@pytest.fixture(scope="session")
async def test_image_file(http_client: AsyncClient, test_image_url):
    response = await http_client.get(test_image_url)
    assert response.status_code == status.HTTP_200_OK
    return response.content


@pytest.fixture(scope="session")
async def test_audio_file(http_client: AsyncClient, test_audio_file_url):
    response = await http_client.get(test_audio_file_url)
    assert response.status_code == status.HTTP_200_OK
    return response.content


@pytest.fixture(scope="session")
def test_base64_image(test_image_file):
    buffer = io.BytesIO(test_image_file)
    base64_string = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{base64_string}"


@pytest.fixture
def create_music_job(session: AsyncSession):
    async def _create_music_job(
        id: str,
        email: str,
        title: str,
        artist: str,
        album: str,
        artwork_url: str | None = None,
        artwork_filename: str | None = None,
        original_filename: str | None = None,
        filename_url: str | None = None,
        video_url: str | None = None,
        download_filename: str | None = None,
        download_url: str | None = None,
        grouping: str | None = None,
        completed: bool = False,
        failed: bool = False,
        deleted_at: datetime | None = None,
    ):
        job = MusicJob(
            id=id,
            user_email=email,
            title=title,
            artist=artist,
            album=album,
            artwork_url=artwork_url,
            artwork_filename=artwork_filename,
            original_filename=original_filename,
            filename_url=filename_url,
            video_url=video_url,
            download_filename=download_filename,
            download_url=download_url,
            grouping=grouping,
            completed=completed,
            failed=failed,
            deleted_at=deleted_at,
        )
        session.add(job)
        await session.commit()
        return job

    return _create_music_job


@pytest.fixture
def get_completed_job(session: AsyncSession):
    async def _get_completed_job(email: str):
        results = await session.scalars(
            select(MusicJob).where(MusicJob.user_email == email)
        )
        job = results.first()
        assert job is not None
        return job

    return _get_completed_job


@pytest.fixture
def get_tags_from_file():
    @contextmanager
    def _get_tags_from_file(file: bytes):
        path = os.path.join(temp_files.TEMP_DIRECTORY, "test.mp3")
        with open(path, "wb") as f:
            f.write(file)

        yield AudioTags(file_path=path)
        os.remove(path)

    return _get_tags_from_file
