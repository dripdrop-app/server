import asyncio
import uuid
import os
import json
from fastapi import (
    FastAPI,
    Query,
    Response,
    UploadFile,
    WebSocket,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
)
from fastapi.responses import FileResponse
from server.utils.imgdl import download_image
from server.utils.mp3dl import extract_info
from server.dependencies import get_authenticated_user
from server.models.main import db, MusicJobs, AuthenticatedUser, MusicJob
from server.models.api import (
    youtube_regex,
    JobInfo,
    JobInfoResponse,
    MusicResponses,
    RedisResponses,
)
from server.redis import (
    redis,
    RedisChannels,
    create_websocket_redis_channel_listener,
)
from server.rq import queue
from server.tasks.music import run_job, read_tags, JOB_DIR
from sqlalchemy import desc, select, insert, delete, update
from typing import Optional
from yt_dlp.utils import sanitize_filename


app = FastAPI(dependencies=[Depends(get_authenticated_user)], responses={401: {}})


@app.get("/grouping", response_model=MusicResponses.Grouping)
async def get_grouping(youtube_url: str = Query(None, regex=youtube_regex)):
    try:
        loop = asyncio.get_event_loop()
        uploader = await loop.run_in_executor(None, extract_info, youtube_url)
        return MusicResponses.Grouping(grouping=uploader).dict()
    except Exception:
        raise HTTPException(400)


@app.get("/artwork", response_model=MusicResponses.ArtworkURL)
async def get_artwork(artwork_url: str = Query(None)):
    try:
        loop = asyncio.get_event_loop()
        artwork_url = await loop.run_in_executor(
            None, download_image, artwork_url, False
        )
        return MusicResponses.ArtworkURL(artwork_url=artwork_url).dict()
    except Exception:
        raise HTTPException(400)


@app.post("/tags", response_model=MusicResponses.Tags)
async def get_tags(file: UploadFile = File(None)):
    if not file:
        raise HTTPException(400)
    loop = asyncio.get_event_loop()
    tags = await loop.run_in_executor(None, read_tags, await file.read(), file.filename)
    return tags.dict()


@app.get("/jobs", response_model=MusicResponses.AllJobs)
async def get_jobs(user: AuthenticatedUser = Depends(get_authenticated_user)):
    query = (
        select(MusicJobs)
        .where(MusicJobs.user_email == user.email)
        .order_by(desc(MusicJobs.created_at))
    )
    jobs = []
    for row in await db.fetch_all(query):
        job = JobInfo.parse_obj(row)
        jobs.append(
            JobInfoResponse(
                id=job.id,
                filename=job.filename,
                youtube_url=job.youtube_url,
                artwork_url=job.artwork_url,
                title=job.title,
                artist=job.artist,
                album=job.album,
                grouping=job.grouping,
                completed=job.completed,
                failed=job.failed,
            )
        )
    return MusicResponses.AllJobs(jobs=jobs).dict()


@app.websocket("/jobs/listen")
async def listen_jobs(
    websocket: WebSocket, user: AuthenticatedUser = Depends(get_authenticated_user)
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
                    MusicResponses.JobUpdate(
                        type=type,
                        job=JobInfoResponse(
                            id=job.id,
                            filename=job.filename,
                            youtube_url=job.youtube_url,
                            artwork_url=job.artwork_url,
                            title=job.title,
                            artist=job.artist,
                            album=job.album,
                            grouping=job.grouping,
                            completed=job.completed,
                            failed=job.failed,
                        ),
                    ).dict(by_alias=True)
                )
            except Exception:
                pass
        return

    await websocket.accept()
    await create_websocket_redis_channel_listener(
        websocket=websocket, channel=RedisChannels.MUSIC_JOB_CHANNEL, handler=handler
    )


@app.post("/jobs/create/youtube", status_code=202)
async def create_job__from_youtube(
    youtubeUrl: str = Form(None, regex=youtube_regex),
    artworkUrl: Optional[str] = Form(None),
    title: str = Form(None),
    artist: str = Form(None),
    album: str = Form(None),
    grouping: Optional[str] = Form(""),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    job_id = str(uuid.uuid4())
    job_info = JobInfo(
        id=job_id,
        youtube_url=youtubeUrl,
        artwork_url=artworkUrl,
        title=title,
        artist=artist,
        album=album,
        grouping=grouping,
        filename=None,
        completed=False,
        failed=False,
    )
    query = insert(MusicJobs).values(
        **job_info.dict(),
        user_email=user.email,
    )
    await db.execute(query)
    queue.enqueue(run_job, job_id, None)
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@app.post("/jobs/create/file", status_code=202)
async def create_job_from_file(
    file: UploadFile = File(None),
    artworkUrl: Optional[str] = Form(None),
    title: str = Form(None),
    artist: str = Form(None),
    album: str = Form(None),
    grouping: Optional[str] = Form(""),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    job_id = str(uuid.uuid4())
    filename = file.filename
    job_info = JobInfo(
        id=job_id,
        youtube_url=None,
        artwork_url=artworkUrl,
        title=title,
        artist=artist,
        album=album,
        grouping=grouping,
        filename=filename,
        completed=False,
        failed=False,
    )
    query = insert(MusicJobs).values(
        **job_info.dict(),
        user_email=user.email,
    )
    await db.execute(query)
    file = await file.read()
    queue.enqueue(run_job, job_id, file)
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps(RedisResponses.MusicChannel(job_id=job_id, type="STARTED").dict()),
    )
    return Response(None, 202)


@app.delete("/jobs/delete/{job_id}")
async def delete_job(
    job_id: str = Path(None), user: AuthenticatedUser = Depends(get_authenticated_user)
):
    query = delete(MusicJobs).where(
        MusicJobs.user_email == user.email, MusicJobs.id == job_id
    )
    await db.execute(query)
    try:
        await asyncio.create_subprocess_shell(f"rm -rf {JOB_DIR}/{job_id}")
    except Exception:
        raise HTTPException(404)
    return Response(None)


@app.get("/jobs/download/{job_id}", status_code=200)
async def download_job(
    job_id: str = Path(None), user: AuthenticatedUser = Depends(get_authenticated_user)
):
    query = select(MusicJobs).where(MusicJobs.id == job_id)
    job = await db.fetch_one(query)
    filename = sanitize_filename(f'{job.get("title")} {job.get("artist")}.mp3')
    file_path = os.path.join(JOB_DIR, job_id, filename)

    if not os.path.exists(file_path):
        query = (
            update(MusicJobs)
            .where(MusicJobs.user_email == user.email, MusicJobs.id == job_id)
            .values(failed=True)
        )
        await db.execute(query)
        await redis.publish(RedisChannels.COMPLETED_MUSIC_JOB_CHANNEL.value, job_id)
        raise HTTPException(404)

    return FileResponse(os.path.join(JOB_DIR, job_id, filename), filename=filename)
