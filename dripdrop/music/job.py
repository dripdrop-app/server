import asyncio
import re
import uuid
from fastapi import (
    APIRouter,
    Depends,
    Path,
    Response,
    UploadFile,
    HTTPException,
    status,
    Form,
    File,
    BackgroundTasks,
)
from fastapi.responses import StreamingResponse
from pydantic import HttpUrl
from sqlalchemy import select
from typing import Optional

from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.music import utils, tasks
from dripdrop.music.models import MusicJob
from dripdrop.music.responses import (
    MusicJobUpdateResponse,
    MusicJobResponse,
    ErrorMessages,
)
from dripdrop.services import http_client, rq_client
from dripdrop.services.websocket_channel import (
    RedisChannels,
    WebsocketChannel,
)
from dripdrop.utils import get_current_time


api = APIRouter(
    prefix="/job",
    tags=["Music Job"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job(
    user: AuthenticatedUser,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    video_url: Optional[HttpUrl] = Form(None),
    artwork_url: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: Optional[str] = Form(None),
):
    if file and video_url:
        raise HTTPException(
            detail=ErrorMessages.CREATE_JOB_BOTH_DEFINED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    elif file is None and video_url is None:
        raise HTTPException(
            detail=ErrorMessages.CREATE_JOB_NOT_DEFINED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if file:
        if not re.match("audio/", file.content_type):
            raise HTTPException(
                detail=ErrorMessages.FILE_INCORRECT_FORMAT,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    job_id = str(uuid.uuid4())
    music_job = MusicJob(
        id=job_id,
        user_email=user.email,
        video_url=video_url.unicode_string() if video_url else None,
        title=title,
        artist=artist,
        album=album,
        grouping=grouping,
        completed=False,
        failed=False,
    )
    session.add(music_job)
    await session.commit()
    await WebsocketChannel(channel=RedisChannels.MUSIC_JOB_UPDATE).publish(
        message=MusicJobUpdateResponse(id=job_id, status="STARTED")
    )
    background_tasks.add_task(
        utils.handle_files, job_id=job_id, file=file, artwork_url=artwork_url
    )
    background_tasks.add_task(
        rq_client.high.enqueue, tasks.run_music_job, music_job_id=job_id
    )
    return MusicJobResponse.model_validate(music_job)


@api.delete(
    "/{job_id}/delete",
    responses={status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.JOB_NOT_FOUND}},
)
async def delete_job(session: DatabaseSession, job_id: str = Path(...)):
    query = select(MusicJob).where(MusicJob.id == job_id)
    results = await session.scalars(query)
    music_job = results.first()
    if not music_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.JOB_NOT_FOUND
        )
    await asyncio.to_thread(rq_client.stop_job, job_id=job_id)
    await utils.cleanup_music_job(music_job=music_job)
    music_job.deleted_at = get_current_time()
    await session.commit()
    return Response(None)


@api.get("/{job_id}/download", responses={status.HTTP_404_NOT_FOUND: {}})
async def download_job(session: DatabaseSession, job_id: str = Path(...)):
    query = select(MusicJob).where(MusicJob.id == job_id)
    results = await session.scalars(query)
    music_job = results.first()
    if not music_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.JOB_NOT_FOUND
        )
    if not music_job.download_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.DOWNLOAD_NOT_FOUND,
        )
    filename = music_job.download_filename.split("/")[-1]
    async with http_client.create_client() as client:
        response = await client.get(music_job.download_url)
        return StreamingResponse(
            content=response.aiter_bytes(chunk_size=500),
            media_type=response.headers.get("content-type"),
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
