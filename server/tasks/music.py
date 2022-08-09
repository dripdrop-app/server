import asyncio
import base64
import io
import json
import logging
import mutagen
import os
import re
import requests
import server.utils.boto3 as boto3
import server.utils.decorators as decorators
import server.utils.imgdl as imgdl
import server.utils.mp3dl as mp3dl
import subprocess
import traceback
import uuid
from databases import Database
from datetime import datetime, timedelta, timezone
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from server.models.main import MusicJob, MusicJobs
from server.models.api import MusicResponses, RedisResponses
from server.redis import redis, RedisChannels
from sqlalchemy import select, update

JOB_DIR = "music_jobs"


@decorators.worker_task
async def run_job(job_id: str, db: Database = None):
    query = select(MusicJobs).where(MusicJobs.id == job_id)
    job = MusicJob.parse_obj(await db.fetch_one(query))
    try:
        if job:
            job_path = os.path.join(JOB_DIR, job_id)
            youtube_url = job.youtube_url
            filename = job.filename
            artwork_url = job.artwork_url
            title = job.title
            artist = job.artist
            album = job.album
            grouping = job.grouping

            job_path = os.path.join(JOB_DIR, job_id)
            try:
                os.mkdir(JOB_DIR)
            except FileExistsError:
                pass
            os.mkdir(job_path)

            if job.filename:
                res = requests.get(boto3.resolve_music_url(job.filename))
                filename = job.filename.split("/")[-1]
                file_path = os.path.join(job_path, filename)
                f = open(file_path, "wb")
                f.write(res.content)
                f.close()
                boto3.delete_file(bucket=boto3.S3_MUSIC_BUCKET, key=job.filename)
                file_path = os.path.join(job_path, filename)
                new_filename = f"{os.path.splitext(file_path)[0]}.mp3"
                AudioSegment.from_file(file_path).export(
                    new_filename, format="mp3", bitrate="320k"
                )
                filename = new_filename
            elif youtube_url:

                def updateProgress(d):
                    nonlocal filename
                    if d["status"] == "finished":
                        filename = f'{".".join(d["filename"].split(".")[:-1])}.mp3'

                mp3dl.yt_download(youtube_url, [updateProgress], job_path)

            audio_file = mutagen.File(filename)

            if artwork_url:
                try:
                    if not re.search("^http(s)+://", artwork_url):
                        artwork_url = boto3.resolve_artwork_url(artwork_url)
                    imageData = imgdl.download_image(artwork_url)
                    extension = artwork_url.split(".")[-1]
                    audio_file.tags.add(
                        mutagen.id3.APIC(mimetype=f"image/{extension}", data=imageData)
                    )
                    boto3.delete_file(
                        bucket=boto3.S3_ARTWORK_BUCKET, filename=artwork_url
                    )
                except Exception:
                    logging.exception(traceback.format_exc())

            audio_file.tags.add(mutagen.id3.TIT2(text=title))
            audio_file.tags.add(mutagen.id3.TPE1(text=artist))
            audio_file.tags.add(mutagen.id3.TALB(text=album))
            audio_file.tags.add(mutagen.id3.TIT1(text=grouping))
            audio_file.save()

            new_filename = (
                f"{job_id}/" + sanitize_filename(f"{title} {artist}") + ".mp3"
            )
            file = open(filename, "rb")
            boto3.upload_file(
                bucket=boto3.S3_MUSIC_BUCKET,
                filename=new_filename,
                body=file.read(),
            )

            query = (
                update(MusicJobs)
                .where(MusicJobs.id == job_id)
                .values(completed=True, download_url=new_filename)
            )
            await db.execute(query)
            await redis.publish(
                RedisChannels.MUSIC_JOB_CHANNEL.value,
                json.dumps(
                    RedisResponses.MusicChannel(job_id=job_id, type="COMPLETED").dict()
                ),
            )
            await asyncio.create_subprocess_shell(f"rm -rf {JOB_DIR}/{job_id}")
    except Exception as e:
        if job:
            query = update(MusicJobs).where(MusicJobs.id == job_id).values(failed=True)
            await db.execute(query)
            await asyncio.create_subprocess_shell(f"rm -rf {JOB_DIR}/{job_id}")
        raise e


def read_tags(file: Union[str, bytes, None], filename):
    folder_id = str(uuid.uuid4())
    tag_path = os.path.join("tags", folder_id)

    try:
        try:
            os.mkdir("tags")
        except FileExistsError:
            pass
        os.mkdir(tag_path)

        filepath = os.path.join(tag_path, filename)
        with open(filepath, "wb") as f:
            f.write(file)
        audio_file = mutagen.File(filepath)
        title = (
            audio_file.tags["TIT2"].text[0] if audio_file.tags.get("TIT2", None) else ""
        )
        artist = (
            audio_file.tags["TPE1"].text[0] if audio_file.tags.get("TPE1", None) else ""
        )
        album = (
            audio_file.tags["TALB"].text[0] if audio_file.tags.get("TALB", None) else ""
        )
        grouping = (
            audio_file.tags["TIT1"].text[0] if audio_file.tags.get("TIT1", None) else ""
        )
        imageKeys = list(filter(lambda key: key.find("APIC") != -1, audio_file.keys()))
        buffer = None
        mimeType = None
        if imageKeys:
            mimeType = audio_file[imageKeys[0]].mime
            buffer = io.BytesIO(audio_file[imageKeys[0]].data)
        subprocess.run(["rm", "-rf", tag_path])
        artwork_url = None
        if buffer:
            artwork_url = (
                f"data:{mimeType};base64,{base64.b64encode(buffer.getvalue()).decode()}"
            )
        return MusicResponses.Tags(
            title=title,
            artist=artist,
            album=album,
            grouping=grouping,
            artwork_url=artwork_url,
        )
    except Exception:
        subprocess.run(["rm", "-rf", tag_path])
        logging.exception(traceback.format_exc())
        return MusicResponses.Tags(
            title=None, artist=None, album=None, grouping=None, artwork_url=None
        )


@decorators.worker_task
@decorators.exception_handler
async def clean_job(job_id: str, db: Database = None):
    await asyncio.create_subprocess_shell(f"rm -rf {JOB_DIR}/{job_id}")
    query = update(MusicJobs).where(MusicJobs.id == job_id).values(failed=True)
    await db.execute(query)


@decorators.worker_task
@decorators.exception_handler
async def cleanup_jobs(db: Database = None):
    limit = datetime.now(timezone.utc) - timedelta(days=14)
    query = select(MusicJobs).where(MusicJobs.created_at < limit)
    for row in await db.fetch_all(query):
        job = MusicJob.parse_obj(row)
        await asyncio.create_subprocess_shell(f"rm -rf {JOB_DIR}/{job.id}")
