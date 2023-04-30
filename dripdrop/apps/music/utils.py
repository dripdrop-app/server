import asyncio
import base64
import os
import re
import shutil
import traceback
import uuid
from dataclasses import dataclass
from fastapi import UploadFile

from dripdrop.apps.music.models import MusicJob
from dripdrop.apps.music.responses import TagsResponse
from dripdrop.logger import logger
from dripdrop.services import http_client, image_downloader, s3, temp_files
from dripdrop.services.audio_tag import AudioTags


@dataclass
class UploadedFileInfo:
    url: str | None
    filename: str | None


async def handle_artwork_url(job_id: str, artwork_url: str | None = None):
    uploaded_file_info = UploadedFileInfo(url=artwork_url, filename=None)
    if artwork_url:
        if re.search("^data:image/", artwork_url):
            extension = artwork_url.split(";")[0].split("/")[1]
            dataString = ",".join(artwork_url.split(",")[1:])
            data = dataString.encode()
            data_bytes = base64.b64decode(data)
            uploaded_file_info.filename = (
                f"{s3.ARTWORK_FOLDER}/{job_id}/artwork.{extension}"
            )
            await s3.upload_file(
                filename=uploaded_file_info.filename,
                body=data_bytes,
                content_type=f"image/{extension}",
            )
            uploaded_file_info.url = s3.resolve_url(
                filename=uploaded_file_info.filename
            )
        else:
            async with http_client.create_client() as client:
                response = await client.get(artwork_url)
            if not response.is_success or not image_downloader.is_image_link(
                response=response
            ):
                return UploadedFileInfo(url=None, filename=None)
    return uploaded_file_info


async def handle_audio_file(job_id: str, file: UploadFile):
    uploaded_file_info = UploadedFileInfo(url=None, filename=None)
    if file:
        uploaded_file_info.filename = f"{s3.MUSIC_FOLDER}/{job_id}/old/{file.filename}"
        uploaded_file_info.url = s3.resolve_url(filename=uploaded_file_info.filename)
        await s3.upload_file(
            filename=uploaded_file_info.filename,
            body=await file.read(),
            content_type=file.content_type,
        )
    return uploaded_file_info


async def cleanup_music_job(music_job: MusicJob):
    if music_job.artwork_filename:
        await s3.delete_file(
            filename=music_job.artwork_filename,
        )
    if music_job.download_filename:
        await s3.delete_file(
            filename=music_job.download_filename,
        )
    if music_job.original_filename:
        await s3.delete_file(
            filename=music_job.original_filename,
        )


def _read_tags(file_path: str):
    audio_tags = AudioTags(file_path=file_path)
    title = audio_tags.title
    artist = audio_tags.artist
    album = audio_tags.album
    grouping = audio_tags.grouping
    artwork_url = audio_tags.get_artwork_as_base64()
    return TagsResponse(
        title=title,
        artist=artist,
        album=album,
        grouping=grouping,
        artwork_url=artwork_url,
    )


async def read_tags(file: bytes, filename: str):
    TAGS_DIRECTORY = "tags"

    tags_directory_path = await temp_files.create_new_directory(
        directory=TAGS_DIRECTORY, raise_on_exists=False
    )
    directory_id = str(uuid.uuid4())
    directory_path = os.path.join(tags_directory_path, directory_id)
    await asyncio.to_thread(os.mkdir, directory_path)
    file_path = os.path.join(directory_path, filename)
    tags = TagsResponse()
    try:
        with open(file_path, "wb") as f:
            await asyncio.to_thread(f.write, file)
        tags = await asyncio.to_thread(_read_tags, file_path)
    except Exception:
        logger.exception(traceback.format_exc())
    finally:
        await asyncio.to_thread(shutil.rmtree, directory_path)

    return tags
