import asyncio
import os
import shutil
from datetime import timedelta
from pydub import AudioSegment
from sqlalchemy import select
from typing import Union
from yt_dlp.utils import sanitize_filename

from dripdrop.music import utils
from dripdrop.music.models import MusicJob
from dripdrop.music.responses import MusicJobUpdateResponse
from dripdrop.services import (
    database,
    http_client,
    image_downloader,
    rq_client,
    s3,
    temp_files,
    ytdlp,
)
from dripdrop.services.database import AsyncSession
from dripdrop.services.audio_tag import AudioTags
from dripdrop.services.websocket_channel import WebsocketChannel, RedisChannels
from dripdrop.utils import get_current_time


async def _retrieve_audio_file(music_job_path: str, music_job: MusicJob):
    filename = None
    if music_job.filename_url:
        async with http_client.create_client() as client:
            res = await client.get(music_job.filename_url)
        audio_file_path = os.path.join(
            music_job_path, f"temp{os.path.splitext(music_job.original_filename)[1]}"
        )
        with open(audio_file_path, "wb") as f:
            f.write(res.content)

        filename = f"{os.path.splitext(audio_file_path)[0]}.mp3"
        exported_file = AudioSegment.from_file(file=audio_file_path).export(
            filename, format="mp3", bitrate="320k"
        )
        exported_file.close()
    elif music_job.video_url:
        filename = os.path.join(music_job_path, "temp.mp3")
        await ytdlp.download_audio_from_video(
            url=music_job.video_url, download_path=f"{os.path.splitext(filename)[0]}"
        )
    return filename


async def _retrieve_artwork(music_job: MusicJob):
    if music_job.artwork_url:
        try:
            imageData = await image_downloader.download_image(
                artwork=music_job.artwork_url
            )
            extension = os.path.splitext(music_job.artwork_url)[0]
            return {"image": imageData, "extension": extension}
        except Exception:
            pass
    return None


def _update_audio_tags(
    music_job: MusicJob,
    filename: str,
    artwork_info: Union[dict, None] = None,
):
    audio_tag_service = AudioTags(file_path=filename)
    audio_tag_service.title = music_job.title
    audio_tag_service.artist = music_job.artist
    audio_tag_service.album = music_job.album
    audio_tag_service.grouping = music_job.grouping
    if artwork_info:
        audio_tag_service.set_artwork(
            data=artwork_info["image"],
            mime_type=f'image/{artwork_info["extension"]}',
        )


@rq_client.worker_task
async def run_music_job(music_job_id: str, session: AsyncSession):
    JOB_DIR = "music_jobs"

    job_id = music_job_id
    root_job_path = await temp_files.create_new_directory(
        directory=JOB_DIR, raise_on_exists=False
    )
    query = select(MusicJob).where(MusicJob.id == job_id)
    results = await session.scalars(query)
    music_job = results.first()
    if not music_job:
        raise Exception(f"Job with id ({job_id}) not found")
    websocket_channel = WebsocketChannel(channel=RedisChannels.MUSIC_JOB_UPDATE)
    await websocket_channel.publish(
        message=MusicJobUpdateResponse(id=job_id, status="STARTED")
    )
    job_path = None
    try:
        job_path = os.path.join(root_job_path, music_job.id)
        await asyncio.to_thread(os.mkdir, job_path)
        filename = await _retrieve_audio_file(
            music_job_path=job_path, music_job=music_job
        )
        artwork_info = await _retrieve_artwork(music_job=music_job)
        await asyncio.to_thread(
            _update_audio_tags,
            music_job=music_job,
            filename=filename,
            artwork_info=artwork_info,
        )
        new_filename = (
            sanitize_filename(f"{music_job.title} {music_job.artist}") + ".mp3"
        )
        new_filename = f"{s3.MUSIC_FOLDER}/{music_job.id}/{new_filename}"
        with open(filename, "rb") as file:
            await s3.upload_file(
                filename=new_filename,
                body=await asyncio.to_thread(file.read),
                content_type="audio/mpeg",
            )
        music_job.completed = True
        music_job.download_filename = new_filename
        music_job.download_url = s3.resolve_url(filename=new_filename)
    except Exception as e:
        music_job.failed = True
        raise e
    finally:
        await session.commit()
        await websocket_channel.publish(
            message=MusicJobUpdateResponse(id=job_id, status="COMPLETED")
        )
        if job_path:
            await asyncio.to_thread(shutil.rmtree, job_path)


@rq_client.worker_task
async def delete_music_job(music_job_id: str, session: AsyncSession = ...):
    query = select(MusicJob).where(MusicJob.id == music_job_id)
    results = await session.scalars(query)
    music_job = results.first()
    if not music_job:
        raise Exception(f"Music Job ({music_job_id}) could not be found")
    await utils.cleanup_music_job(music_job=music_job)
    music_job.deleted_at = get_current_time()
    await session.commit()


@rq_client.worker_task
async def delete_old_music_jobs(session: AsyncSession = ...):
    limit = get_current_time() - timedelta(days=14)
    query = select(MusicJob).where(
        MusicJob.created_at < limit,
        MusicJob.completed.is_(True),
        MusicJob.deleted_at.is_(None),
    )
    async for music_jobs in database.stream_scalars(
        query=query, yield_per=1, session=session
    ):
        music_job = music_jobs[0]

        await asyncio.to_thread(
            rq_client.default.enqueue, delete_music_job, music_job_id=music_job.id
        )