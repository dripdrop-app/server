import base64
import json
import math
import re
import traceback
import uuid
from asgiref.sync import sync_to_async
from fastapi import (
    FastAPI,
    Query,
    Path,
    Response,
    UploadFile,
    WebSocket,
    Depends,
    File,
    Form,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from server.dependencies import get_authenticated_user
from server.logging import logger
from server.models.api import MusicResponses, RedisResponses, youtube_regex
from server.models.main import db, MusicJobs, User, MusicJob
from server.services.boto3 import boto3_service, Boto3Service
from server.services.image_downloader import image_downloader_service
from server.services.redis import (
    redis,
    RedisChannels,
    redis_service,
)
from server.services.rq import queue
from server.services.tag_extractor import tag_extractor_service
from server.services.youtube_downloader import youtuber_downloader_service
from server.tasks.music import music_tasker
from sqlalchemy import select, insert, delete, func
from typing import Optional


music_app = FastAPI(dependencies=[Depends(get_authenticated_user)], responses={401: {}})


@music_app.get("/grouping", response_model=MusicResponses.Grouping)
async def get_grouping(youtube_url: str = Query(..., regex=youtube_regex)):
    try:
        extract_info = sync_to_async(youtuber_downloader_service.extract_info)
        uploader = await extract_info(link=youtube_url)
        return MusicResponses.Grouping(grouping=uploader).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(400)


@music_app.get("/artwork", response_model=MusicResponses.ArtworkURL)
async def get_artwork(artwork_url: str = Query(...)):
    try:
        resolve_artwork = sync_to_async(image_downloader_service.resolve_artwork)
        artwork_url = await resolve_artwork(artwork=artwork_url)
        return MusicResponses.ArtworkURL(artwork_url=artwork_url).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(400)


@music_app.post("/tags", response_model=MusicResponses.Tags)
async def get_tags(file: UploadFile = File(...)):
    read_tags = sync_to_async(tag_extractor_service.read_tags)
    tags = await read_tags(file=await file.read(), filename=file.filename)
    return tags.dict(by_alias=True)


@music_app.get("/jobs/{page}/{per_page}", response_model=MusicResponses.AllJobs)
async def get_jobs(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    user: User = Depends(get_authenticated_user),
):
    jobs_query = (
        select(MusicJobs)
        .where(MusicJobs.user_email == user.email)
        .alias(name="music_jobs")
    )
    query = (
        select(jobs_query)
        .order_by(jobs_query.c.created_at.desc())
        .select_from(jobs_query)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    count_query = select(func.count(jobs_query.c.id)).select_from(jobs_query)
    count = await db.fetch_val(count_query)
    total_pages = math.ceil(count / per_page)
    jobs = list(map(lambda row: MusicJob.parse_obj(row), await db.fetch_all(query)))
    return MusicResponses.AllJobs(jobs=jobs, total_pages=total_pages).dict(
        by_alias=True
    )


@music_app.websocket("/jobs/listen")
async def listen_jobs(
    websocket: WebSocket, user: User = Depends(get_authenticated_user)
):
    async def handler(msg):
        message = json.loads(msg.get("data").decode())
        message = RedisResponses.MusicChannel.parse_obj(message)
        job_id = message.job_id
        type = message.type
        query = select(MusicJobs).where(
            MusicJobs.user_email == user.email, MusicJobs.id == job_id
        )
        job = await db.fetch_one(query)
        if job:
            try:
                job = MusicJob.parse_obj(job)
                await websocket.send_json(
                    jsonable_encoder(
                        MusicResponses.JobUpdate(
                            type=type,
                            job=job,
                        ).dict(by_alias=True)
                    )
                )
            except Exception:
                logger.exception(traceback.format_exc())
        return

    await websocket.accept()
    await redis_service.create_websocket_redis_channel_listener(
        websocket=websocket, channel=RedisChannels.MUSIC_JOB_CHANNEL, handler=handler
    )


async def handle_artwork_url(job_id: str = ..., artwork_url: Optional[str] = ...):
    if artwork_url:
        is_base64 = re.search("^data:image/", artwork_url)
        if is_base64:
            extension = artwork_url.split(";")[0].split("/")[1]
            dataString = ",".join(artwork_url.split(",")[1:])
            data = dataString.encode()
            data_bytes = base64.b64decode(data)
            artwork_filename = f"{job_id}/artwork.{extension}"
            upload_file = sync_to_async(boto3_service.upload_file)
            await upload_file(
                bucket=Boto3Service.S3_ARTWORK_BUCKET,
                filename=artwork_filename,
                body=data_bytes,
                content_type=f"image/{extension}",
            )
            artwork_url = f"artwork.{extension}"
    return artwork_url


@music_app.post("/jobs/create/youtube", status_code=202)
async def create_job_from_youtube(
    youtubeUrl: str = Form(..., regex=youtube_regex),
    artworkUrl: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
):
    job_id = str(uuid.uuid4())
    query = insert(MusicJobs).values(
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
    await db.execute(query)
    queue.enqueue(music_tasker.run_job, kwargs={"job_id": job_id})
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@music_app.post("/jobs/create/file", status_code=202)
async def create_job_from_file(
    file: UploadFile = File(...),
    artworkUrl: Optional[str] = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
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
    query = insert(MusicJobs).values(
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
    await db.execute(query)
    queue.enqueue(music_tasker.run_job, kwargs={"job_id": job_id})
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@music_app.delete("/jobs/delete/{job_id}")
async def delete_job(job_id: str, user: User = Depends(get_authenticated_user)):
    query = select(MusicJobs).where(MusicJobs.id == job_id)
    job = await db.fetch_one(query)
    if not job:
        raise HTTPException(404)
    job = MusicJob.parse_obj(job)
    query = delete(MusicJobs).where(
        MusicJobs.user_email == user.email, MusicJobs.id == job_id
    )
    await db.execute(query)
    try:
        delete_file = sync_to_async(boto3_service.delete_file)
        await delete_file(bucket=Boto3Service.S3_ARTWORK_BUCKET, filename=job.id)
        await delete_file(bucket=Boto3Service.S3_MUSIC_BUCKET, filename=job.id)
    except Exception:
        logger.exception(traceback.format_exc())
    return Response(None)
