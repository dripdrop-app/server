import asyncio
import base64
import os
import re
import shutil
import traceback
import uuid
from fastapi import UploadFile

from dataclasses import dataclass
from dripdrop.logging import logger
from dripdrop.services import image_downloader, s3
from dripdrop.services.audio_tag import AudioTags
from dripdrop.services.http_client import http_client

from .models import MusicJob
from .responses import TagsResponse


@dataclass
class UploadedFileInfo:
    url: str | None
    filename: str | None


async def handle_artwork_url(job_id: str = ..., artwork_url: str | None = None):
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
            response = await http_client.get(artwork_url)
            if not response.is_success or not image_downloader.is_image_link(
                response=response
            ):
                return UploadedFileInfo(url=None, filename=None)
    return uploaded_file_info


async def handle_audio_file(job_id: str = ..., file: UploadFile = ...):
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


async def cleanup_job(job: MusicJob):
    if job.artwork_filename:
        await s3.delete_file(
            filename=job.artwork_filename,
        )
    if job.download_filename:
        await s3.delete_file(
            filename=job.download_filename,
        )
    if job.original_filename:
        await s3.delete_file(
            filename=job.original_filename,
        )


async def read_tags(file: bytes = ..., filename: str = ...):
    def _create_tags_directory():
        TAGS_FOLDER = "tags"
        folder_id = str(uuid.uuid4())
        tag_path = os.path.join(TAGS_FOLDER, folder_id)
        try:
            os.mkdir("tags")
        except FileExistsError:
            logger.exception(traceback.format_exc())
        os.mkdir(tag_path)
        return tag_path

    def _clean_up(tag_path: str = ...):
        try:
            shutil.rmtree(tag_path)
        except Exception:
            pass

    def _read_tags(file: bytes = ..., filename: str = ...):
        tag_path = _create_tags_directory()
        try:
            file_path = os.path.join(tag_path, filename)
            with open(file_path, "wb") as f:
                f.write(file)

            audio_tags = AudioTags(file_path=file_path)
            title = audio_tags.title
            artist = audio_tags.artist
            album = audio_tags.album
            grouping = audio_tags.grouping
            artwork_url = audio_tags.get_artwork_as_base64()
            _clean_up(tag_path=tag_path)
            return TagsResponse(
                title=title,
                artist=artist,
                album=album,
                grouping=grouping,
                artwork_url=artwork_url,
            )
        except Exception:
            _clean_up(tag_path=tag_path)
            logger.exception(traceback.format_exc())
            return TagsResponse()

    return await asyncio.to_thread(_read_tags, file=file, filename=filename)
