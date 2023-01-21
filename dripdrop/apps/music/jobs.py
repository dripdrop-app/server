import json
import math
import re
import traceback
import uuid
from datetime import datetime, timezone
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
from sqlalchemy import select, func
from typing import Optional

from dripdrop.dependencies import (
    get_authenticated_user,
    create_db_session,
    AsyncSession,
    User,
)
from dripdrop.logging import logger
from dripdrop.redis import redis
from dripdrop.rq import queue
from dripdrop.services.redis import redis_service, RedisChannels

from .models import MusicJob, youtube_regex
from .responses import (
    MusicChannelResponse,
    JobsResponse,
    JobUpdateResponse,
    ErrorMessages,
)
from .tasks import music_tasker
from .utils import handle_artwork_url, cleanup_job, handle_audio_file


jobs_api = APIRouter(
    prefix="/jobs",
    tags=["Music Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@jobs_api.get(
    "/{page}/{per_page}",
    response_model=JobsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.PAGE_NOT_FOUND}
    },
)
async def get_jobs(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = (
        select(MusicJob)
        .where(MusicJob.user_email == user.email, MusicJob.deleted_at.is_(None))
        .order_by(MusicJob.created_at.desc())
    )
    results = await session.scalars(query.offset((page - 1) * per_page))
    jobs = list(map(lambda job: job, results.fetchmany(per_page)))
    count_query = select(func.count(query.subquery().columns.id))
    count = await session.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    if page > total_pages:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return JobsResponse(jobs=jobs, total_pages=total_pages)


@jobs_api.websocket("/listen")
async def listen_jobs(
    websocket: WebSocket,
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    async def handler(msg):
        message = json.loads(msg.get("data").decode())
        message = MusicChannelResponse.parse_obj(message)
        job_id = message.job_id
        query = select(MusicJob).where(
            MusicJob.user_email == user.email,
            MusicJob.id == job_id,
            MusicJob.deleted_at.is_(None),
        )
        results = await session.scalars(query)
        job: MusicJob | None = results.first()
        if job:
            try:
                await websocket.send_json(
                    jsonable_encoder(JobUpdateResponse(job=job).dict(by_alias=True))
                )
            except Exception:
                logger.exception(traceback.format_exc())

    await websocket.accept()
    await redis_service.create_websocket_redis_channel_listener(
        websocket=websocket,
        channel=RedisChannels.MUSIC_JOB_CHANNEL,
        handler=handler,
    )


@jobs_api.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}},
)
async def create_job(
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None, regex=youtube_regex),
    artwork_url: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: Optional[str] = Form(None),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    if file and youtube_url:
        raise HTTPException(
            detail=ErrorMessages.CREATE_JOB_BOTH_DEFINED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    elif file is None and youtube_url is None:
        raise HTTPException(
            detail=ErrorMessages.CREATE_JOB_NOT_DEFINED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if file:
        if not re.match("audio/(wav|mpeg)", file.content_type):
            raise HTTPException(
                detail=ErrorMessages.FILE_INCORRECT_FORMAT,
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    job_id = str(uuid.uuid4())
    try:
        filename_url, filename = await handle_audio_file(job_id=job_id, file=file)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail=ErrorMessages.FAILED_AUDIO_FILE_UPLOAD,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    try:
        artwork_url, artwork_filename = await handle_artwork_url(
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
            artwork_url=artwork_url,
            artwork_filename=artwork_filename,
            original_filename=filename,
            filename_url=filename_url,
            youtube_url=youtube_url,
            title=title,
            artist=artist,
            album=album,
            grouping=grouping,
            completed=False,
            failed=False,
        )
    )
    await session.commit()
    queue.enqueue(music_tasker.run_job, kwargs={"job_id": job_id})
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL,
        json.dumps(MusicChannelResponse(job_id=job_id).dict()),
    )
    return Response(None, status_code=status.HTTP_201_CREATED)


@jobs_api.delete(
    "/delete",
    responses={status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.JOB_NOT_FOUND}},
)
async def delete_job(
    job_id: str = Query(...),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(MusicJob).where(MusicJob.id == job_id)
    results = await session.scalars(query)
    job: MusicJob | None = results.first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.JOB_NOT_FOUND
        )
    await cleanup_job(job=job)
    job.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return Response(None)
