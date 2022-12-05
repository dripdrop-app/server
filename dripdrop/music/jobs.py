import json
import math
import traceback
import uuid
from .models import MusicJob, MusicJobs, youtube_regex
from .responses import (
    MusicChannelResponse,
    JobsResponse,
    JobUpdateResponse,
    JobNotFoundResponse,
)
from .tasks import music_tasker
from .utils import handle_artwork_url
from asgiref.sync import sync_to_async
from datetime import datetime, timezone
from dripdrop.dependencies import (
    get_authenticated_user,
    create_db_session,
    AsyncSession,
    User,
)
from dripdrop.logging import logger
from dripdrop.services.boto3 import boto3_service, Boto3Service
from dripdrop.services.redis import redis_service, RedisChannels, redis
from dripdrop.services.rq import queue
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    Path,
    WebSocket,
    File,
    UploadFile,
    HTTPException,
    status,
    Form,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func
from typing import Optional

jobs_api = APIRouter(
    prefix="/jobs",
    tags=["Music Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@jobs_api.get("/{page}/{per_page}", response_model=JobsResponse)
async def get_jobs(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = (
        select(MusicJobs)
        .where(MusicJobs.user_email == user.email, MusicJobs.deleted_at.is_(None))
        .order_by(MusicJobs.created_at.desc())
    )
    results = await db.scalars(query.offset((page - 1) * per_page))
    jobs = list(map(lambda job: MusicJob.from_orm(job), results.fetchmany(per_page)))
    count_query = select(func.count(query.c.id))
    count = await db.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    return JobsResponse(jobs=jobs, total_pages=total_pages)


@jobs_api.websocket("/listen")
async def listen_jobs(
    websocket: WebSocket,
    user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(create_db_session),
):
    async def handler(msg):
        message = json.loads(msg.get("data").decode())
        message = MusicChannelResponse.parse_obj(message)
        job_id = message.job_id
        type = message.type
        query = select(MusicJobs).where(
            MusicJobs.user_email == user.email,
            MusicJobs.id == job_id,
            MusicJobs.deleted_at.is_(None),
        )
        results = await db.scalars(query)
        job = results.first()
        if job:
            try:
                await websocket.send_json(
                    jsonable_encoder(
                        JobUpdateResponse(type=type, job=MusicJob.from_orm(job)).dict(
                            by_alias=True
                        )
                    )
                )
            except Exception:
                logger.exception(traceback.format_exc())
        return

    await websocket.accept()
    await redis_service.create_websocket_redis_channel_listener(
        websocket=websocket,
        channel=RedisChannels.MUSIC_JOB_CHANNEL,
        handler=handler,
    )


@jobs_api.post("/create/youtube", status_code=status.HTTP_201_CREATED)
async def create_job_from_youtube(
    youtube_url: str = Form(..., regex=youtube_regex),
    artwork_url: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(create_db_session),
):
    job_id = str(uuid.uuid4())
    db.add(
        MusicJobs(
            id=job_id,
            youtube_url=youtube_url,
            download_url=None,
            artwork_url=await handle_artwork_url(
                job_id=job_id, artwork_url=artwork_url
            ),
            title=title,
            artist=artist,
            album=album,
            grouping=grouping,
            filename=None,
            completed=False,
            failed=False,
            user_email=user.email,
        )
    )
    await db.commit()
    queue.enqueue(music_tasker.run_job, kwargs={"job_id": job_id})
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(MusicChannelResponse(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, status_code=status.HTTP_201_CREATED)


@jobs_api.post("/create/file", status_code=status.HTTP_201_CREATED)
async def create_job_from_file(
    file: UploadFile = File(...),
    artwork_url: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(create_db_session),
):
    job_id = str(uuid.uuid4())
    try:
        upload_file = sync_to_async(boto3_service.upload_file)
        await upload_file(
            bucket=Boto3Service.S3_MUSIC_BUCKET,
            filename=f"{job_id}/{file.filename}",
            body=await file.read(),
            content_type=file.content_type,
        )
    except Exception:
        logger.exception(traceback.format_exc())
        return Response(None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    db.add(
        MusicJobs(
            id=job_id,
            youtube_url=None,
            download_url=None,
            artwork_url=await handle_artwork_url(
                job_id=job_id, artwork_url=artwork_url
            ),
            title=title,
            artist=artist,
            album=album,
            grouping=grouping,
            filename=file.filename,
            completed=False,
            failed=False,
            user_email=user.email,
        )
    )
    await db.commit()
    queue.enqueue(music_tasker.run_job, kwargs={"job_id": job_id})
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(MusicChannelResponse(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, status_code=status.HTTP_201_CREATED)


@jobs_api.delete(
    "/delete",
    responses={status.HTTP_404_NOT_FOUND: {"description": JobNotFoundResponse}},
)
async def delete_job(
    job_id: str = Query(...),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(MusicJobs).where(MusicJobs.id == job_id)
    results = await db.scalars(query)
    job = results.first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=JobNotFoundResponse
        )
    music_job = MusicJob.from_orm(job)
    delete_file = sync_to_async(boto3_service.delete_file)
    if music_job.artwork_url:
        await delete_file(
            bucket=Boto3Service.S3_ARTWORK_BUCKET, filename=music_job.artwork_url
        )
    if music_job.download_url:
        await delete_file(
            bucket=Boto3Service.S3_MUSIC_BUCKET, filename=music_job.download_url
        )
    job.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return Response(None)
