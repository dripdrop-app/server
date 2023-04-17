import asyncio
import math
import re
import traceback
import uuid
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    Path,
    WebSocket,
    UploadFile,
    HTTPException,
    status,
    Form,
    File,
)
from fastapi.encoders import jsonable_encoder
from pydantic import HttpUrl
from sqlalchemy import select, func
from typing import Optional

import dripdrop.utils as dripdrop_utils
from dripdrop.apps.authentication.models import User
from dripdrop.dependencies import create_database_session, get_authenticated_user
from dripdrop.logger import logger
from dripdrop.services import rq_client
from dripdrop.services.database import AsyncSession
from dripdrop.services.websocket_channel import (
    RedisChannels,
    WebsocketChannel,
)

from . import utils, tasks
from .models import MusicJob
from .responses import MusicJobUpdateResponse, MusicJobsResponse, ErrorMessages


jobs_api = APIRouter(
    prefix="/jobs",
    tags=["Music Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@jobs_api.get(
    "/{page}/{per_page}",
    response_model=MusicJobsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.PAGE_NOT_FOUND}
    },
)
async def get_jobs(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_database_session),
):
    query = (
        select(MusicJob)
        .where(MusicJob.user_email == user.email, MusicJob.deleted_at.is_(None))
        .order_by(MusicJob.created_at.desc())
    )
    results = await session.scalars(query.offset((page - 1) * per_page))
    music_jobs = list(map(lambda job: job, results.fetchmany(per_page)))
    count_query = select(func.count(query.subquery().columns.id))
    count = await session.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    if page > total_pages and page != 1:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return MusicJobsResponse(music_jobs=music_jobs, total_pages=total_pages)


@jobs_api.websocket("/listen")
async def listen_jobs(
    websocket: WebSocket, user: User = Depends(get_authenticated_user)
):
    async def handler(msg):
        message = MusicJobUpdateResponse.parse_obj(msg)
        job_id = message.id
        async with create_database_session() as session:
            query = select(MusicJob).where(
                MusicJob.user_email == user.email,
                MusicJob.id == job_id,
                MusicJob.deleted_at.is_(None),
            )
            results = await session.scalars(query)
            music_job = results.first()
            if music_job:
                await websocket.send_json(jsonable_encoder(message))

    await WebsocketChannel(channel=RedisChannels.MUSIC_JOB_UPDATE).listen(
        websocket=websocket, handler=handler
    )


@jobs_api.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}},
)
async def create_job(
    file: Optional[UploadFile] = File(None),
    video_url: Optional[HttpUrl] = Form(None),
    artwork_url: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: Optional[str] = Form(None),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_database_session),
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
    try:
        audiofile_info = await utils.handle_audio_file(job_id=job_id, file=file)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail=ErrorMessages.FAILED_AUDIO_FILE_UPLOAD,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        artwork_info = await utils.handle_artwork_url(
            job_id=job_id, artwork_url=artwork_url
        )
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail=ErrorMessages.FAILED_IMAGE_UPLOAD,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    session.add(
        MusicJob(
            id=job_id,
            user_email=user.email,
            artwork_url=artwork_info.url,
            artwork_filename=artwork_info.filename,
            original_filename=audiofile_info.filename,
            filename_url=audiofile_info.url,
            video_url=video_url,
            title=title,
            artist=artist,
            album=album,
            grouping=grouping,
            completed=False,
            failed=False,
        )
    )
    await session.commit()
    await asyncio.to_thread(
        rq_client.high_queue.enqueue,
        tasks.run_music_job,
        music_job_id=job_id,
        job_id=job_id,
    )
    return Response(None, status_code=status.HTTP_201_CREATED)


@jobs_api.delete(
    "/delete",
    responses={status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.JOB_NOT_FOUND}},
)
async def delete_job(
    job_id: str = Query(...),
    session: AsyncSession = Depends(create_database_session),
):
    query = select(MusicJob).where(MusicJob.id == job_id)
    results = await session.scalars(query)
    music_job = results.first()
    if not music_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.JOB_NOT_FOUND
        )
    await asyncio.to_thread(rq_client.stop_job, job_id=job_id)
    await utils.cleanup_music_job(music_job=music_job)
    music_job.deleted_at = dripdrop_utils.get_current_time()
    await session.commit()
    return Response(None)
