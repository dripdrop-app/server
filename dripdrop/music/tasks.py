import json
import os
import requests
import shutil
import traceback
from .models import MusicJobs, MusicJob
from .responses import MusicChannelResponse
from datetime import datetime, timedelta, timezone
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from dripdrop.database import AsyncSession
from dripdrop.logging import logger
from dripdrop.services.boto3 import boto3_service, Boto3Service
from dripdrop.services.audio_tag import AudioTagService
from dripdrop.services.image_downloader import image_downloader_service
from dripdrop.services.redis import redis, RedisChannels
from dripdrop.services.youtube_downloader import youtuber_downloader_service
from dripdrop.utils import worker_task
from sqlalchemy import select


class MusicTasker:
    def __init__(self) -> None:
        self.JOB_DIR = "music_jobs"

    def create_job_folder(self, job: MusicJob = ...):
        job_path = os.path.join(self.JOB_DIR, job.id)
        try:
            os.mkdir(self.JOB_DIR)
        except FileExistsError:
            logger.exception(traceback.format_exc())
        os.mkdir(job_path)
        return job_path

    def retrieve_audio_file(self, job_path: str = ..., job: MusicJob = ...):
        if job.filename:
            res = requests.get(job.filename)
            audio_file_path = os.path.join(job_path, job.original_filename)
            with open(audio_file_path, "wb") as f:
                f.write(res.content)

            new_audio_file_path = f"{os.path.splitext(audio_file_path)[0]}.mp3"
            AudioSegment.from_file(audio_file_path).export(
                new_audio_file_path,
                format="mp3",
                bitrate="320k",
            )
            return new_audio_file_path
        elif job.youtube_url:
            filename = None

            def updateProgress(d):
                nonlocal filename
                if d["status"] == "finished":
                    filename = f'{os.path.splitext(d["filename"])[0]}.mp3'

            youtuber_downloader_service.yt_download(
                link=job.youtube_url,
                progress_hooks=[updateProgress],
                folder=job_path,
            )
        return filename

    def retrieve_artwork(self, job: MusicJob = ...):
        artwork_url = job.artwork_url
        if artwork_url:
            try:
                imageData = image_downloader_service.download_image(artwork=artwork_url)
                extension = os.path.splitext(artwork_url)[0]
                return {"image": imageData, "extension": extension}
            except Exception:
                logger.exception(traceback.format_exc())
        return None

    def update_audio_tags(
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
    async def run_job(
        self,
        job_id: str = ...,
        db: AsyncSession = ...,
    ):
        query = select(MusicJobs).where(MusicJobs.id == job_id)
        results = await db.scalars(query)
        job = results.first()
        if not job:
            raise Exception(f"Job with id ({job_id}) not found")

        job_path = None
        try:
            music_job = MusicJob.from_orm(job)
            job_path = self.create_job_folder(job=music_job)
            filename = self.retrieve_audio_file(job_path=job_path, job=music_job)
            artwork_info = self.retrieve_artwork(job=music_job)
            self.update_audio_tags(
                job=music_job,
                filename=filename,
                artwork_info=artwork_info,
            )
            new_filename = (
                sanitize_filename(f"{music_job.title} {music_job.artist}") + ".mp3"
            )

            with open(filename, "rb") as file:
                boto3_service.upload_file(
                    bucket=Boto3Service.S3_MUSIC_BUCKET,
                    filename=f"{music_job.id}/{new_filename}",
                    body=file.read(),
                    content_type="audio/mpeg",
                )
            job.completed = True
            job.download_url = new_filename
        except Exception:
            job.failed = True
            logger.exception(traceback.format_exc())
        finally:
            await db.commit()
            await redis.publish(
                RedisChannels.MUSIC_JOB_CHANNEL.value,
                json.dumps(
                    MusicChannelResponse(job_id=job_id, type="COMPLETED").dict()
                ),
            )
            if job_path:
                shutil.rmtree(job_path)

    @worker_task
    async def cleanup_jobs(self, db: AsyncSession = ...):
        limit = datetime.now(timezone.utc) - timedelta(days=14)
        query = select(MusicJobs).where(
            MusicJobs.created_at < limit,
            MusicJobs.completed.is_(True),
            MusicJobs.deleted_at.is_(None),
        )
        stream = await db.stream_scalars(query)
        async for job in stream:
            music_job = MusicJob.from_orm(job)
            try:
                await boto3_service.async_delete_file(
                    bucket=Boto3Service.S3_ARTWORK_BUCKET,
                    filename=f"{music_job.id}/{music_job.artwork_filename}",
                )
                await boto3_service.async_delete_file(
                    bucket=Boto3Service.S3_MUSIC_BUCKET,
                    filename=f"{music_job.id}/{music_job.download_url}",
                )
                await boto3_service.async_delete_file(
                    bucket=Boto3Service.S3_MUSIC_BUCKET,
                    filename=f"{music_job.id}/{music_job.original_filename}",
                )
            except Exception:
                logger.exception(traceback.format_exc())
            job.deleted_at = datetime.now(timezone.utc)
            await db.commit()


music_tasker = MusicTasker()
