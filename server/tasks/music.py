import asyncio
import json
import mutagen
import os
import re
import requests
import traceback
from asgiref.sync import sync_to_async
from databases import Database
from datetime import datetime, timedelta, timezone
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from server.logging import logger
from server.models.main import MusicJob, MusicJobs
from server.models.api import RedisResponses
from server.services.boto3 import boto3_service, Boto3Service
from server.services.image_downloader import image_downloader_service
from server.services.redis import redis, RedisChannels
from server.services.rq import queue
from server.services.youtube_downloader import youtuber_downloader_service
from server.utils.decorators import decorators
from sqlalchemy import select, update


class MusicTasker:
    JOB_DIR = "music_jobs"

    async def create_job_folder(self, job: MusicJob = ...):
        job_path = os.path.join(MusicTasker.JOB_DIR, job.id)
        try:
            os.mkdir(MusicTasker.JOB_DIR)
        except FileExistsError:
            logger.exception(traceback.format_exc())
        os.mkdir(job_path)

    async def retrieve_audio_file(self, job: MusicJob = ...):
        job_path = os.path.join(MusicTasker.JOB_DIR, job.id)
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
                new_filename, format="mp3", bitrate="320k"
            )
            filename = new_filename
        elif job.youtube_url:

            def updateProgress(d):
                nonlocal filename
                if d["status"] == "finished":
                    filename = f'{".".join(d["filename"].split(".")[:-1])}.mp3'

            youtuber_downloader_service.yt_download(
                link=job.youtube_url, progress_hooks=[updateProgress], folder=job_path
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

    @decorators.worker_task
    async def run_job(self, job_id: str = ..., db: Database = ...):
        query = select(MusicJobs).where(MusicJobs.id == job_id)
        row = await db.fetch_one(query)
        if not row:
            return
        try:
            job = MusicJob.parse_obj(row)
            await self.create_job_folder(job=job)
            filename = await self.retrieve_audio_file(job=job)
            artwork_info = await self.retrieve_artwork(job=job)
            new_filename = await self.update_audio_tags(
                job=job, filename=filename, artwork_info=artwork_info
            )
            file = open(filename, "rb")
            boto3_service.upload_file(
                bucket=Boto3Service.S3_MUSIC_BUCKET,
                filename=new_filename,
                body=file.read(),
                content_type="audio/mpeg",
            )
            query = (
                update(MusicJobs)
                .where(MusicJobs.id == job_id)
                .values(completed=True, download_url=new_filename)
            )
            await db.execute(query)
        except Exception:
            query = update(MusicJobs).where(MusicJobs.id == job_id).values(failed=True)
            await db.execute(query)
            logger.exception(traceback.format_exc())
        finally:
            await redis.publish(
                RedisChannels.MUSIC_JOB_CHANNEL.value,
                json.dumps(
                    RedisResponses.MusicChannel(job_id=job_id, type="COMPLETED").dict()
                ),
            )
            await asyncio.create_subprocess_shell(
                f"rm -rf {MusicTasker.JOB_DIR}/{job_id}"
            )

    @decorators.worker_task
    @decorators.exception_handler
    async def clean_job(self, job: MusicJob = ..., db: Database = ...):
        try:
            delete_file = sync_to_async(boto3_service.delete_file)
            await delete_file(
                bucket=Boto3Service.S3_ARTWORK_BUCKET,
                filename=boto3_service.resolve_artwork_url(job.id),
            )
            await delete_file(
                bucket=Boto3Service.S3_MUSIC_BUCKET,
                filename=boto3_service.resolve_music_url(job.id),
            )
        except Exception:
            logger.exception(traceback.format_exc())
        query = (
            update(MusicJobs)
            .where(MusicJobs.id == job.id)
            .values(failed=True, completed=False)
        )
        await db.execute(query)

    @decorators.worker_task
    @decorators.exception_handler
    async def cleanup_jobs(self, db: Database = ...):
        limit = datetime.now(timezone.utc) - timedelta(days=14)
        query = select(MusicJobs).where(
            MusicJobs.created_at < limit, MusicJobs.completed.is_(True)
        )
        async for row in db.iterate(query):
            job = MusicJob.parse_obj(row)
            queue.enqueue(self.clean_job, kwargs={"job": job}, at_front=True)


music_tasker = MusicTasker()
