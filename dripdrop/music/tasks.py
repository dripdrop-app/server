import asyncio
import json
import mutagen
import os
import re
import requests
import traceback
from .models import MusicJobs, MusicJob
from .responses import MusicChannelResponse
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta, timezone
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from dripdrop.database import AsyncSession
from dripdrop.logging import logger
from dripdrop.services.boto3 import boto3_service, Boto3Service
from dripdrop.services.image_downloader import image_downloader_service
from dripdrop.services.redis import redis, RedisChannels
from dripdrop.services.youtube_downloader import youtuber_downloader_service
from dripdrop.utils import worker_task
from sqlalchemy import select


class MusicTasker:
    def __init__(self) -> None:
        self.JOB_DIR = "music_jobs"

    async def create_job_folder(self, job: MusicJob = ...):
        job_path = os.path.join(self.JOB_DIR, job.id)
        try:
            os.mkdir(self.JOB_DIR)
        except FileExistsError:
            logger.exception(traceback.format_exc())
        os.mkdir(job_path)

    async def retrieve_audio_file(self, job: MusicJob = ...):
        job_path = os.path.join(self.JOB_DIR, job.id)
        filename = None
        if job.filename:
            res = requests.get(
                boto3_service.resolve_music_url(filename=f"{job.id}/{job.filename}")
            )
            filename = job.filename.split("/")[-1]
            file_path = os.path.join(job_path, filename)
            f = open(file_path, "wb")
            f.write(res.content)
            f.close()
            boto3_service.delete_file(
                bucket=Boto3Service.S3_MUSIC_BUCKET, filename=f"{job.id}/{job.filename}"
            )
            file_path = os.path.join(job_path, filename)
            new_filename = f"{os.path.splitext(file_path)[0]}.mp3"
            AudioSegment.from_file(file_path).export(
                new_filename,
                format="mp3",
                bitrate="320k",
            )
            filename = new_filename
        elif job.youtube_url:

            def updateProgress(d):
                nonlocal filename
                if d["status"] == "finished":
                    filename = f'{".".join(d["filename"].split(".")[:-1])}.mp3'

            youtuber_downloader_service.yt_download(
                link=job.youtube_url,
                progress_hooks=[updateProgress],
                folder=job_path,
            )
        return filename

    async def retrieve_artwork(self, job: MusicJob = ...):
        artwork_url = job.artwork_url
        if artwork_url:
            try:
                if not re.search("^http(s)?://", artwork_url):
                    artwork_url = boto3_service.resolve_artwork_url(
                        filename=f"{job.id}/{artwork_url}"
                    )
                imageData = image_downloader_service.download_image(artwork=artwork_url)
                extension = artwork_url.split(".")[-1]
                boto3_service.delete_file(
                    bucket=Boto3Service.S3_ARTWORK_BUCKET,
                    filename=f"{job.id}/{artwork_url}",
                )
                return {"image": imageData, "extension": extension}
            except Exception:
                logger.exception(traceback.format_exc())
        return None

    async def update_audio_tags(
        self,
        job: MusicJob = ...,
        filename: str = ...,
        artwork_info: Union[dict, None] = None,
    ):
        audio_file = mutagen.File(filename)
        if artwork_info:
            audio_file.tags.add(
                mutagen.id3.APIC(
                    mime=f"image/{artwork_info['extension']}",
                    data=artwork_info["image"],
                )
            )
        audio_file.tags.add(mutagen.id3.TIT2(text=job.title))
        audio_file.tags.add(mutagen.id3.TPE1(text=job.artist))
        audio_file.tags.add(mutagen.id3.TALB(text=job.album))
        audio_file.tags.add(mutagen.id3.TIT1(text=job.grouping))
        audio_file.save()
        new_filename = (
            f"{job.id}/" + sanitize_filename(f"{job.title} {job.artist}") + ".mp3"
        )
        return new_filename

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
            return
        try:
            music_job = MusicJob.from_orm(job)
            await self.create_job_folder(job=music_job)
            filename = await self.retrieve_audio_file(job=music_job)
            artwork_info = await self.retrieve_artwork(job=music_job)
            new_filename = await self.update_audio_tags(
                job=music_job,
                filename=filename,
                artwork_info=artwork_info,
            )
            file = open(filename, "rb")
            boto3_service.upload_file(
                bucket=Boto3Service.S3_MUSIC_BUCKET,
                filename=new_filename,
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
            await asyncio.create_subprocess_shell(f"rm -rf {self.JOB_DIR}/{job_id}")

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
                delete_file = sync_to_async(boto3_service.delete_file)
                await delete_file(
                    bucket=Boto3Service.S3_ARTWORK_BUCKET,
                    filename=boto3_service.resolve_artwork_url(music_job.artwork_url),
                )
                await delete_file(
                    bucket=Boto3Service.S3_MUSIC_BUCKET,
                    filename=boto3_service.resolve_music_url(music_job.download_url),
                )
            except Exception:
                logger.exception(traceback.format_exc())
            job.deleted_at = True
            await db.commit()


music_tasker = MusicTasker()
