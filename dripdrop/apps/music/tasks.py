import json
import os
import shutil
import traceback
from datetime import datetime, timedelta
from pydub import AudioSegment
from sqlalchemy import select
from typing import Union
from yt_dlp.utils import sanitize_filename

from dripdrop.database import AsyncSession
from dripdrop.http_client import http_client
from dripdrop.logging import logger
from dripdrop.services.s3 import s3, S3
from dripdrop.services.audio_tag import AudioTags
from dripdrop.services.image_downloader import image_downloader
from dripdrop.services.websocket_handler import RedisChannels
from dripdrop.services.ytdlp import ytdlp
from dripdrop.settings import settings
from dripdrop.redis import redis
from dripdrop.rq import enqueue
from dripdrop.utils import worker_task

from .models import MusicJob
from .responses import MusicChannelResponse
from .utils import cleanup_job


class MusicTasker:
    def __init__(self) -> None:
        self.JOB_DIR = "music_jobs"

    def _create_job_folder(self, job: MusicJob = ...):
        job_path = os.path.join(self.JOB_DIR, job.id)
        try:
            os.mkdir(self.JOB_DIR)
        except FileExistsError:
            logger.exception(traceback.format_exc())
        os.mkdir(job_path)
        return job_path

    async def _retrieve_audio_file(self, job_path: str = ..., job: MusicJob = ...):
        filename = None
        if job.filename_url:
            res = await http_client.get(job.filename_url)
            audio_file_path = os.path.join(
                job_path, f"temp{os.path.splitext(job.original_filename)[1]}"
            )
            with open(audio_file_path, "wb") as f:
                f.write(res.content)

            filename = f"{os.path.splitext(audio_file_path)[0]}.mp3"
            AudioSegment.from_file(file=audio_file_path).export(
                filename, format="mp3", bitrate="320k"
            )
        elif job.video_url:
            filename = os.path.join(job_path, "temp.mp3")
            await ytdlp.download_audio_from_video(
                url=job.video_url, download_path=f"{os.path.splitext(filename)[0]}"
            )
        return filename

    async def _retrieve_artwork(self, job: MusicJob = ...):
        if job.artwork_url:
            try:
                imageData = await image_downloader.download_image(
                    artwork=job.artwork_url
                )
                extension = os.path.splitext(job.artwork_url)[0]
                return {"image": imageData, "extension": extension}
            except Exception:
                logger.exception(traceback.format_exc())
        return None

    def _update_audio_tags(
        self,
        job: MusicJob = ...,
        filename: str = ...,
        artwork_info: Union[dict, None] = None,
    ):
        audio_tag_service = AudioTags(file_path=filename)
        audio_tag_service.title = job.title
        audio_tag_service.artist = job.artist
        audio_tag_service.album = job.album
        audio_tag_service.grouping = job.grouping
        if artwork_info:
            audio_tag_service.set_artwork(
                data=artwork_info["image"],
                mime_type=f'image/{artwork_info["extension"]}',
            )

    @worker_task
    async def run_job(self, job_id: str = ..., session: AsyncSession = ...):
        query = select(MusicJob).where(MusicJob.id == job_id)
        results = await session.scalars(query)
        job = results.first()
        if not job:
            raise Exception(f"Job with id ({job_id}) not found")
        job_path = None
        try:
            job_path = self._create_job_folder(job=job)
            filename = await self._retrieve_audio_file(job_path=job_path, job=job)
            artwork_info = await self._retrieve_artwork(job=job)
            self._update_audio_tags(
                job=job,
                filename=filename,
                artwork_info=artwork_info,
            )
            new_filename = sanitize_filename(f"{job.title} {job.artist}") + ".mp3"
            new_filename = f"{S3.MUSIC_FOLDER}/{job.id}/{new_filename}"
            with open(filename, "rb") as file:
                await s3.upload_file(
                    filename=new_filename,
                    body=file.read(),
                    content_type="audio/mpeg",
                )
            job.completed = True
            job.download_filename = new_filename
            job.download_url = S3.resolve_url(filename=new_filename)
        except Exception:
            job.failed = True
            logger.exception(traceback.format_exc())
        finally:
            await session.commit()
            await redis.publish(
                RedisChannels.MUSIC_JOB_CHANNEL,
                json.dumps(
                    MusicChannelResponse(job_id=job_id, status="COMPLETED").dict()
                ),
            )
            if job_path:
                shutil.rmtree(job_path)

    @worker_task
    async def _delete_job(self, job_id: str = ..., session: AsyncSession = ...):
        query = select(MusicJob).where(MusicJob.id == job_id)
        results = await session.scalars(query)
        job = results.first()
        if not job:
            raise Exception(f"Job ({job_id}) could not be found")
        await cleanup_job(job=job)
        job.deleted_at = datetime.now(tz=settings.timezone)
        await session.commit()

    @worker_task
    async def delete_old_jobs(self, session: AsyncSession = ...):
        limit = datetime.now(tz=settings.timezone) - timedelta(days=14)
        query = select(MusicJob).where(
            MusicJob.created_at < limit,
            MusicJob.completed.is_(True),
            MusicJob.deleted_at.is_(None),
        )
        stream = await session.stream_scalars(query)
        async for job in stream:
            await enqueue(
                function=self._delete_job, kwargs={"job_id": job.id}, at_front=True
            )


music_tasker = MusicTasker()
