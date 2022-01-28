import asyncio
import uuid
import traceback
import os
import json
from asyncio.tasks import Task
from fastapi import (
    FastAPI,
    Query,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    File,
    Form,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from server.api.music.imgdl import download_image
from server.api.music.mp3dl import extract_info
from server.api.music.tasks import read_tags, JOB_DIR
from server.dependencies import get_authenticated_user
from server.models import db, MusicJobs, AuthenticatedUser, MusicJob
from server.models.api import JobInfo, MusicResponses, youtube_regex
from server.redis import RedisChannels, subscribe, redis
from server.queue import q
from sqlalchemy import desc, select, insert, delete, update
from typing import Optional
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from yt_dlp.utils import sanitize_filename


app = FastAPI(dependencies=[Depends(get_authenticated_user)], responses={401: {}})


@app.get("/grouping", response_model=MusicResponses.Grouping)
async def get_grouping(youtube_url: str = Query(None, regex=youtube_regex)):
    try:
        loop = asyncio.get_event_loop()
        uploader = await loop.run_in_executor(None, extract_info, youtube_url)
        return JSONResponse({"grouping": uploader})
    except Exception:
        raise HTTPException(400)


@app.get("/get_artwork", response_model=MusicResponses.ArtworkURL)
async def get_artwork(artwork_url: str = Query(None)):
    try:
        loop = asyncio.get_event_loop()
        artwork_url = await loop.run_in_executor(
            None, download_image, artwork_url, False
        )
        return JSONResponse({"artwork_url": artwork_url})
    except Exception:
        raise HTTPException(400)


@app.post("/get_tags", response_model=MusicResponses.Tags)
async def get_tags(file: UploadFile = File(None)):
    if not file:
        raise HTTPException(400)
    loop = asyncio.get_event_loop()
    tags = await loop.run_in_executor(None, read_tags, await file.read(), file.filename)
    return JSONResponse(tags.dict())


@app.websocket("/listen_jobs")
async def listen_jobs(
    websocket: WebSocket, user: AuthenticatedUser = Depends(get_authenticated_user)
):
    async def handler(msg):
        message = json.loads(msg.get("data").decode())
        job_id = message.get("job_id")
        type = message.get("type")
        query = select(MusicJobs).where(
            MusicJobs.user_email == user.email, MusicJobs.id == job_id
        )
        job = await db.fetch_one(query)
        if job:
            job = MusicJob.parse_obj(job)
            await websocket.send_json({"type": type, "jobs": [jsonable_encoder(job)]})
        return

    task: Task = None
    try:
        await websocket.accept()
        query = (
            select(MusicJobs)
            .where(MusicJobs.user_email == user.email)
            .order_by(desc(MusicJobs.created_at))
        )
        jobs = await db.fetch_all(query)
        await websocket.send_json({"type": "ALL", "jobs": jsonable_encoder(jobs)})
        task = asyncio.create_task(subscribe(RedisChannels.MUSIC_JOB_CHANNEL, handler))
        while True:
            await websocket.send_json({})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await websocket.close()
    except ConnectionClosedError:
        pass
    except ConnectionClosedOK:
        pass
    except Exception:
        print(traceback.format_exc())
    finally:
        task.cancel()


@app.post("/download", status_code=202, response_model=MusicResponses.Download)
async def download(
    youtube_url: Optional[str] = Form(None, regex=youtube_regex),
    artwork_url: Optional[str] = Form(None),
    title: str = Form(None),
    artist: str = Form(None),
    album: str = Form(None),
    grouping: Optional[str] = Form(""),
    file: UploadFile = File(None),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    job_id = str(uuid.uuid4())
    if not youtube_url and not file:
        return Response(None, 400)

    filename = file.filename if file else None

    job_info = JobInfo(
        id=job_id,
        youtube_url=youtube_url,
        artwork_url=artwork_url,
        title=title,
        artist=artist,
        album=album,
        grouping=grouping,
        filename=filename,
    )

    query = insert(MusicJobs).values(
        **job_info.dict(),
        user_email=user.email,
        completed=False,
        failed=False,
    )
    await db.execute(query)

    if file:
        file = await file.read()

    q.enqueue("server.api.music.tasks.run_job", job_id, file)
    await redis.publish(
        RedisChannels.MUSIC_JOB_CHANNEL.value,
        json.dumps({"job_id": job_id, "type": "STARTED"}),
    )
    return JSONResponse({"job": jsonable_encoder(job_info)})


@app.delete("/delete_job")
async def delete_job(
    id: str = Query(None), user: AuthenticatedUser = Depends(get_authenticated_user)
):
    job_id = id
    query = delete(MusicJobs).where(
        MusicJobs.user_email == user.email, MusicJobs.id == job_id
    )
    await db.execute(query)
    try:
        await asyncio.create_subprocess_shell(f"rm -rf {JOB_DIR}/{job_id}")
    except Exception:
        pass
    return Response(None)


@app.get("/download_job", status_code=200)
async def download_job(
    id: str = Query(None), user: AuthenticatedUser = Depends(get_authenticated_user)
):
    job_id = id
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
