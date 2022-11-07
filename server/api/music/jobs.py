import json
import math
import traceback
import uuid
from .utils import handle_artwork_url
from asgiref.sync import sync_to_async
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    Path,
    WebSocket,
    Form,
    File,
    UploadFile,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from server.dependencies import (
    get_authenticated_user,
    create_db_session,
    DBSession,
    User,
)
from server.logging import logger
from server.models.api import MusicResponses, MusicJob, RedisResponses, youtube_regex
from server.models.orm import MusicJobs
from server.services.boto3 import boto3_service, Boto3Service
from server.services.redis import redis_service, RedisChannels, redis
from server.services.rq import queue
from server.tasks.music import music_tasker
from sqlalchemy import select, func
from typing import Optional

music_jobs_api = APIRouter(
    prefix="/jobs",
    tags=["Music Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@music_jobs_api.get("/{page}/{per_page}", response_model=MusicResponses.AllJobs)
async def get_jobs(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    user: User = Depends(get_authenticated_user),
    db: DBSession = Depends(create_db_session),
):
    query = (
        select(MusicJobs)
        .where(MusicJobs.user_email == user.email)
        .order_by(MusicJobs.created_at.desc())
    )
    results = await db.scalars(query.offset((page - 1) * per_page))
    jobs = list(map(lambda job: MusicJob.from_orm(job), results.fetchmany(per_page)))
    count_query = select(func.count(query.c.id))
    count = await db.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    return MusicResponses.AllJobs(jobs=jobs, total_pages=total_pages).dict(
        by_alias=True
    )


@music_jobs_api.websocket("/listen")
async def listen_jobs(
    websocket: WebSocket,
    user: User = Depends(get_authenticated_user),
    db: DBSession = Depends(create_db_session),
):
    async def handler(msg):
        message = json.loads(msg.get("data").decode())
        message = RedisResponses.MusicChannel.parse_obj(message)
        job_id = message.job_id
        type = message.type
        query = select(MusicJobs).where(
            MusicJobs.user_email == user.email,
            MusicJobs.id == job_id,
        )
        results = await db.scalars(query)
        job = results.first()
        if job:
            try:
                job = MusicJob.from_orm(job)
                await websocket.send_json(
                    jsonable_encoder(
                        MusicResponses.JobUpdate(type=type, job=job).dict(by_alias=True)
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


@music_jobs_api.post("/create/youtube", status_code=202)
async def create_job_from_youtube(
    youtubeUrl: str = Form(..., regex=youtube_regex),
    artworkUrl: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
    db: DBSession = Depends(create_db_session),
):
    job_id = str(uuid.uuid4())
    db.add(
        MusicJobs(
            id=job_id,
            youtube_url=youtubeUrl,
            download_url=None,
            artwork_url=await handle_artwork_url(job_id=job_id, artwork_url=artworkUrl),
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
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@music_jobs_api.post("/create/file", status_code=202)
async def create_job_from_file(
    file: UploadFile = File(...),
    artworkUrl: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
    db: DBSession = Depends(create_db_session),
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
        return Response(None, 500)
    db.add(
        MusicJobs(
            id=job_id,
            youtube_url=None,
            download_url=None,
            artwork_url=await handle_artwork_url(job_id=job_id, artwork_url=artworkUrl),
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
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@music_jobs_api.delete("/delete", responses={404: {"description": "Job not found"}})
async def delete_job(
    job_id: str = Query(...),
    db: DBSession = Depends(create_db_session),
):
    query = select(MusicJobs).where(MusicJobs.id == job_id)
    results = await db.scalars(query)
    job = results.first()
    if not job:
        raise HTTPException(404)
    music_job = MusicJob.from_orm(job)
    await db.delete(job)
    await db.commit()
    try:
        delete_file = sync_to_async(boto3_service.delete_file)
        await delete_file(bucket=Boto3Service.S3_ARTWORK_BUCKET, filename=music_job.id)
        await delete_file(bucket=Boto3Service.S3_MUSIC_BUCKET, filename=music_job.id)
    except Exception:
        logger.exception(traceback.format_exc())
    return Response(None)
