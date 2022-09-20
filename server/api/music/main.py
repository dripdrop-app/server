import base64
import json
import logging
import re
import requests
import traceback
import server.tasks.music as music_tasks
import server.utils.boto3 as boto3
import server.utils.imgdl as imgdl
import server.utils.mp3dl as mp3dl
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
from server.models.main import db, MusicJobs, User, MusicJob
from server.models.api import MusicResponses, RedisResponses, youtube_regex
from server.redis import (
    redis,
    RedisChannels,
    create_websocket_redis_channel_listener,
)
from server.rq import queue
from sqlalchemy import select, insert, delete, update


app = FastAPI(dependencies=[Depends(get_authenticated_user)], responses={401: {}})


@app.get("/grouping", response_model=MusicResponses.Grouping)
async def get_grouping(youtube_url: str = Query(..., regex=youtube_regex)):
    try:
        extract_info = sync_to_async(mp3dl.extract_info)
        uploader = await extract_info(youtube_url)
        return MusicResponses.Grouping(grouping=uploader).dict(by_alias=True)
    except Exception:
        raise HTTPException(400)


@app.get("/artwork", response_model=MusicResponses.ArtworkURL)
async def get_artwork(artwork_url: str = Query(...)):
    try:
        download_image = sync_to_async(imgdl.download_image)
        artwork_url = await download_image(artwork_url, False)
        return MusicResponses.ArtworkURL(artwork_url=artwork_url).dict(by_alias=True)
    except Exception:
        raise HTTPException(400)


@app.post("/tags", response_model=MusicResponses.Tags)
async def get_tags(file: UploadFile = File(...)):
    read_tags = sync_to_async(music_tasks.read_tags)
    tags = await read_tags(await file.read(), file.filename)
    return tags.dict(by_alias=True)


@app.get("/jobs/{page}/{per_page}", response_model=MusicResponses.AllJobs)
async def get_jobs(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    user: User = Depends(get_authenticated_user),
):
    query = (
        select(MusicJobs)
        .where(MusicJobs.user_email == user.email)
        .order_by(MusicJobs.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    jobs = [MusicJob.parse_obj(row) for row in await db.fetch_all(query)]
    return MusicResponses.AllJobs(jobs=jobs).dict(by_alias=True)


@app.websocket("/jobs/listen")
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
                logging.exception(traceback.format_exc())
        return

    await websocket.accept()
    await create_websocket_redis_channel_listener(
        websocket=websocket, channel=RedisChannels.MUSIC_JOB_CHANNEL, handler=handler
    )


async def handle_artwork_url(job_id: str, artwork_url: str):
    is_base64 = re.search("^data:image/", artwork_url)
    if is_base64:
        extension = artwork_url.split(";")[0].split("/")[1]
        dataString = ",".join(artwork_url.split(",")[1:])
        data = dataString.encode()
        data_bytes = base64.b64decode(data)
        artwork_filename = f"{job_id}_artwork.{extension}"
        upload_file = sync_to_async(boto3.upload_file)
        await upload_file(
            bucket=boto3.S3_ARTWORK_BUCKET,
            filename=artwork_filename,
            body=data_bytes,
            content_type=f"image/{extension}",
        )
        artwork_url = artwork_filename
    return artwork_url


@app.post("/jobs/create/youtube", status_code=202)
async def create_job_from_youtube(
    youtubeUrl: str = Form(..., regex=youtube_regex),
    artworkUrl: str = Form(None),
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
        artwork_url=await handle_artwork_url(job_id, artworkUrl),
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
    queue.enqueue(music_tasks.run_job, job_id)
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@app.post("/jobs/create/file", status_code=202)
async def create_job_from_file(
    file: UploadFile = File(...),
    artworkUrl: str = Form(None),
    title: str = Form(...),
    artist: str = Form(...),
    album: str = Form(...),
    grouping: str = Form(""),
    user: User = Depends(get_authenticated_user),
):
    job_id = str(uuid.uuid4())
    filename = f"{job_id}/{file.filename}"
    try:
        upload_file = sync_to_async(boto3.upload_file)
        await upload_file(
            bucket=boto3.S3_MUSIC_BUCKET,
            filename=filename,
            body=await file.read(),
            content_type=file.content_type,
        )
    except Exception:
        logging.exception(traceback.format_exc())
        return Response(None, 500)
    query = insert(MusicJobs).values(
        id=job_id,
        youtube_url=None,
        download_url=None,
        artwork_url=await handle_artwork_url(job_id, artworkUrl),
        title=title,
        artist=artist,
        album=album,
        grouping=grouping,
        filename=filename,
        completed=False,
        failed=False,
        user_email=user.email,
    )
    await db.execute(query)
    queue.enqueue(music_tasks.run_job, job_id)
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@app.delete("/jobs/delete/{job_id}")
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
        delete_file = sync_to_async(boto3.delete_file)
        await delete_file(bucket=boto3.S3_ARTWORK_BUCKET, filename=job.artwork_url)
        await delete_file(bucket=boto3.S3_MUSIC_BUCKET, filename=job.filename)
    except Exception:
        logging.exception(traceback.format_exc())
    return Response(None)


@app.get("/jobs/download/{job_id}", response_model=MusicResponses.Download)
async def download_job(job_id: str, user: User = Depends(get_authenticated_user)):
    query = select(MusicJobs).where(MusicJobs.id == job_id)
    job = await db.fetch_one(query)
    if not job:
        raise HTTPException(404)
    job = MusicJob.parse_obj(job)
    res = await sync_to_async(requests.get)(job.download_url)
    if res.status_code != 200:
        query = (
            update(MusicJobs)
            .where(MusicJobs.user_email == user.email, MusicJobs.id == job_id)
            .values(failed=True)
        )
        await db.execute(query)
        await redis.publish(RedisChannels.MUSIC_JOB_CHANNEL.value, job_id)
        raise HTTPException(404)
    return MusicResponses.Download(url=job.download_url)
