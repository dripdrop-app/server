import base64
import io
import os
from datetime import datetime
from sqlalchemy import select

from dripdrop.base.test import BaseTest
from dripdrop.music.models import MusicJob
from dripdrop.services import s3, temp_files
from dripdrop.services.audio_tag import AudioTags


class MusicBaseTest(BaseTest):
    test_image_file: bytes | None = None
    test_audio_file: bytes | None = None
    test_base64_image: bytes | None = None

    async def asyncSetUp(self):
        await super().asyncSetUp()
        await self.clean_test_s3_folders()

        self.test_image_url = (
            "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )
        self.test_audio_file_url = (
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com"
            + "/test/07%20tun%20suh.mp3"
        )
        self.test_video_url = "https://vimeo.com/56282283"

        if not MusicBaseTest.test_image_file:
            response = await self.http_client.get(self.test_image_url)
            response.raise_for_status()
            MusicBaseTest.test_image_file = response.content

        if not MusicBaseTest.test_audio_file:
            response = await self.http_client.get(self.test_audio_file_url)
            response.raise_for_status()
            MusicBaseTest.test_audio_file = response.content

        if not MusicBaseTest.test_base64_image:
            buffer = io.BytesIO(MusicBaseTest.test_image_file)
            base64_string = base64.b64encode(buffer.getvalue()).decode()
            MusicBaseTest.test_base64_image = f"data:image/png;base64,{base64_string}"

    async def asyncTearDown(self):
        await super().asyncTearDown()
        await self.clean_test_s3_folders()

    async def clean_test_s3_folders(self):
        try:
            async for keys in s3.list_objects():
                for key in keys:
                    if key.startswith("test"):
                        continue
                    await s3.delete_file(filename=key)
        except Exception:
            pass

    async def create_music_job(
        self,
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
        self.session.add(job)
        await self.session.commit()
        return job

    async def get_music_job(self, email: str, music_job_id: str):
        results = await self.session.scalars(
            select(MusicJob).where(
                MusicJob.user_email == email, MusicJob.id == music_job_id
            )
        )
        job = results.first()
        self.assertIsNotNone(job)
        return job

    async def get_tags_from_file(self, file: bytes):
        path = os.path.join(temp_files.TEMP_DIRECTORY, "test.mp3")
        with open(path, "wb") as f:
            f.write(file)
        return AudioTags(file_path=path)
