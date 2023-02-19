import base64
import os
import re
import shutil
import traceback
import uuid
from asgiref.sync import sync_to_async
from fastapi import UploadFile
from pydantic import HttpUrl

from dripdrop.logging import logger
from dripdrop.services.audio_tag import AudioTagService
from dripdrop.services.boto3 import Boto3Service, boto3_service

from .models import MusicJob
from .responses import TagsResponse


async def handle_artwork_url(job_id: str = ..., artwork_url: str | None = None):
    artwork_filename = None
    if artwork_url:
        is_base64 = re.search("^data:image/", artwork_url)
        if is_base64:
            extension = artwork_url.split(";")[0].split("/")[1]
            dataString = ",".join(artwork_url.split(",")[1:])
            data = dataString.encode()
            data_bytes = base64.b64decode(data)
            artwork_filename = (
                f"{Boto3Service.S3_ARTWORK_FOLDER}/{job_id}/artwork.{extension}"
            )
            await boto3_service.upload_file(
                filename=artwork_filename,
                body=data_bytes,
                content_type=f"image/{extension}",
            )
            artwork_url = Boto3Service.resolve_url(filename=artwork_filename)
        else:
            try:
                HttpUrl.validate(artwork_url)
            except Exception:
                artwork_url = None
    return artwork_url, artwork_filename


async def handle_audio_file(job_id: str = ..., file: UploadFile = ...):
    filename_url = None
    filename = None
    if file:
        filename = f"{Boto3Service.S3_MUSIC_FOLDER}/{job_id}/old/{file.filename}"
        filename_url = Boto3Service.resolve_url(filename=filename)
        await boto3_service.upload_file(
            filename=filename,
            body=await file.read(),
            content_type=file.content_type,
        )
    return filename_url, filename


async def cleanup_job(job: MusicJob):
    if job.artwork_filename:
        await boto3_service.delete_file(
            filename=job.artwork_filename,
        )
    if job.download_filename:
        await boto3_service.delete_file(
            filename=job.download_filename,
        )
    if job.original_filename:
        await boto3_service.delete_file(
            filename=job.original_filename,
        )


async def read_tags(file: bytes = ..., filename: str = ...) -> TagsResponse:
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

            audio_tags = AudioTagService(file_path=file_path)
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

    return await sync_to_async(_read_tags)(file=file, filename=filename)
