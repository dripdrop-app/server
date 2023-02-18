import asyncio
import json
import os
import requests
import shutil
import traceback
from datetime import datetime, timedelta
from sqlalchemy import select
from typing import Union
from yt_dlp.utils import sanitize_filename

from dripdrop.database import Session
from dripdrop.logging import logger
from dripdrop.redis import redis
from dripdrop.services.boto3 import boto3_service, Boto3Service
from dripdrop.services.audio_tag import AudioTagService
from dripdrop.services.image_downloader import image_downloader_service
from dripdrop.services.redis import RedisChannels
from dripdrop.services.audio import audio_service
from dripdrop.settings import settings
from dripdrop.rq import queue
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

    def _retrieve_audio_file(self, job_path: str = ..., job: MusicJob = ...):
        filename = None
        if job.filename_url:
            res = requests.get(job.filename_url)
            audio_file_path = os.path.join(
                job_path, f"temp{os.path.splitext(job.original_filename)[1]}"
            )
            with open(audio_file_path, "wb") as f:
                f.write(res.content)

            new_audio_file_path = f"{os.path.splitext(audio_file_path)[0]}.mp3"
            audio_service.convert_to_mp3(
                file_path=audio_file_path, new_file_path=new_audio_file_path
            )
            return new_audio_file_path
        elif job.video_url:
            filename = audio_service.download(link=job.video_url, folder=job_path)
        return filename

    def _retrieve_artwork(self, job: MusicJob = ...):
        if job.artwork_url:
            try:
                imageData = image_downloader_service.download_image(
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
        audio_tag_service = AudioTagService(file_path=filename)
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
    def run_job(self, job_id: str = ..., session: Session = ...):
        query = select(MusicJob).where(MusicJob.id == job_id)
        results = session.scalars(query)
        job = results.first()
        if not job:
            raise Exception(f"Job with id ({job_id}) not found")
        job_path = None
        try:
            job_path = self._create_job_folder(job=job)
            filename = self._retrieve_audio_file(job_path=job_path, job=job)
            artwork_info = self._retrieve_artwork(job=job)
            self._update_audio_tags(
                job=job,
                filename=filename,
                artwork_info=artwork_info,
            )
            new_filename = sanitize_filename(f"{job.title} {job.artist}") + ".mp3"
            new_filename = f"{Boto3Service.S3_MUSIC_FOLDER}/{job.id}/{new_filename}"
            with open(filename, "rb") as file:
                boto3_service.upload_file(
                    filename=new_filename,
                    body=file.read(),
                    content_type="audio/mpeg",
                )
            job.completed = True
            job.download_filename = new_filename
            job.download_url = Boto3Service.resolve_url(filename=new_filename)
        except Exception:
            job.failed = True
            logger.exception(traceback.format_exc())
        finally:
            session.commit()
            redis.publish(
                RedisChannels.MUSIC_JOB_CHANNEL,
                json.dumps(MusicChannelResponse(job_id=job_id).dict()),
            )
            if job_path:
                shutil.rmtree(job_path)

    @worker_task
    def _delete_job(self, job_id: str = ..., session: Session = ...):
        query = select(MusicJob).where(MusicJob.id == job_id)
        results = session.scalars(query)
        job = results.first()
        if not job:
            raise Exception(f"Job ({job_id}) could not be found")
        asyncio.run(cleanup_job(job=job))
        job.deleted_at = datetime.now(tz=settings.timezone)
        session.commit()

    @worker_task
    def delete_old_jobs(self, session: Session = ...):
        limit = datetime.now(tz=settings.timezone) - timedelta(days=14)
        query = select(MusicJob).where(
            MusicJob.created_at < limit,
            MusicJob.completed.is_(True),
            MusicJob.deleted_at.is_(None),
        )
        stream = session.scalars(query)
        for job in stream.yield_per(10):
            queue.enqueue(self._delete_job, kwargs={"job_id": job.id}, at_front=True)


music_tasker = MusicTasker()
