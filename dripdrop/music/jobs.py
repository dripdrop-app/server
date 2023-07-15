import asyncio
import math
import re
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
    BackgroundTasks,
)
from pydantic import HttpUrl
from sqlalchemy import select, func
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
    MusicJobsResponse,
    ErrorMessages,
)
from dripdrop.services import database, rq_client
from dripdrop.services.websocket_channel import (
    RedisChannels,
    WebsocketChannel,
)
from dripdrop.utils import get_current_time


api = APIRouter(
    prefix="/jobs",
    tags=["Music Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.get(
    "/{page}/{per_page}",
    response_model=MusicJobsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.PAGE_NOT_FOUND}
    },
)
async def get_jobs(
    user: AuthenticatedUser,
    session: DatabaseSession,
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
):
    query = (
        select(MusicJob)
        .where(MusicJob.user_email == user.email, MusicJob.deleted_at.is_(None))
        .order_by(MusicJob.created_at.desc())
    )
    results = await session.scalars(query.offset((page - 1) * per_page).limit(per_page))
    music_jobs = list(map(lambda job: job, results.all()))
    count_query = select(func.count(query.subquery().columns.id))
    count = await session.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    if page > total_pages and page != 1:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return MusicJobsResponse(music_jobs=music_jobs, total_pages=total_pages)


@api.websocket("/listen")
async def listen_jobs(user: AuthenticatedUser, websocket: WebSocket):
    async def handler(msg):
        message = MusicJobUpdateResponse.model_validate(msg)
        job_id = message.id
        async with database.create_session() as session:
            query = select(MusicJob).where(
                MusicJob.user_email == user.email,
                MusicJob.id == job_id,
                MusicJob.deleted_at.is_(None),
            )
            results = await session.scalars(query)
            music_job = results.first()
            if music_job:
                await websocket.send_json(message.model_dump())

    await WebsocketChannel(channel=RedisChannels.MUSIC_JOB_UPDATE).listen(
        websocket=websocket, handler=handler
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
    "/delete",
    responses={status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.JOB_NOT_FOUND}},
)
async def delete_job(session: DatabaseSession, job_id: str = Query(...)):
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
