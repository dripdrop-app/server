import asyncio
import uuid
import traceback
import os
from asyncio.tasks import Task
from typing import Union
from sqlalchemy.sql.expression import desc
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK
from yt_dlp.utils import sanitize_filename
from server.utils.mp3dl import extract_info
from server.utils.imgdl import download_image
from server.db import database, music_jobs, websocket_tokens
from server.redis import RedisChannels, subscribe, redis
from server.tasks import download_task, Job, read_tags
from server.middleware import authenticated_endpoint, endpoint_handler, api_key_protected_endpoint
from server.utils.helpers import convert_db_response
from server.config import API_KEY


@endpoint_handler()
@authenticated_endpoint()
async def get_grouping(request: Request):
    youtube_url = request.query_params.get('youtube_url')
    uploader = await run_in_threadpool(extract_info, youtube_url)
    return JSONResponse({'grouping': uploader})


@endpoint_handler()
@authenticated_endpoint()
async def get_artwork(request: Request):
    artwork_url = request.query_params.get('artwork_url')
    artwork_url = await run_in_threadpool(download_image, artwork_url, False)
    return JSONResponse({'artwork_url': artwork_url})


@endpoint_handler()
@authenticated_endpoint()
async def get_tags(request: Request):
    form = await request.form()
    file: Union[UploadFile, None] = form.get('file')

    if not file:
        return Response(None, 400)

    tags = await run_in_threadpool(read_tags, await file.read(), file.filename)
    return JSONResponse(tags)


async def listen_jobs(websocket: WebSocket):
    tasks: list[Task] = []
    try:
        await websocket.accept()

        token = await websocket.receive_text()
        if token:
            query = websocket_tokens.select().where(websocket_tokens.c.id == token)
            found = await database.fetch_one(query)
            if not found:
                raise WebSocketDisconnect()
        else:
            raise WebSocketDisconnect()

        query = music_jobs.select().order_by(desc(music_jobs.c.started))
        jobs = await database.fetch_all(query)
        await websocket.send_json({
            'type': 'ALL',
            'jobs': [convert_db_response(job) for job in jobs]
        })

        tasks.extend([
            asyncio.create_task(
                subscribe(RedisChannels.STARTED_JOB_CHANNEL, websocket)),
            asyncio.create_task(
                subscribe(RedisChannels.COMPLETED_JOB_CHANNEL, websocket))
        ])

        while True:
            await websocket.send_json({})
            await asyncio.sleep(5)

    except Exception as e:
        if not isinstance(e, WebSocketDisconnect) and not isinstance(e, ConnectionClosedOK):
            print(traceback.format_exc())
        for task in tasks:
            task.cancel()
        await websocket.close()


@endpoint_handler()
@authenticated_endpoint()
async def download(request: Request):
    job_id = str(uuid.uuid4())
    form = await request.form()
    youtube_url = form.get('youtube_url')
    file: Union[UploadFile, None] = form.get('file')
    artwork_url = form.get('artwork_url')
    title = form.get('title')
    artist = form.get('artist')
    album = form.get('album')
    grouping = form.get('grouping')

    if not youtube_url and not file:
        return Response(None, 400)

    job = Job(
        job_id=job_id,
        filename=file.filename if file else None,
        youtube_url=youtube_url,
        artwork_url=artwork_url,
        title=title,
        artist=artist,
        album=album,
        grouping=grouping
    )

    async with database.transaction():
        query = music_jobs.insert().values(
            **job.__dict__,
            completed=False,
            failed=False,
        )
        await database.execute(query)

    task = BackgroundTask(
        download_task,
        job,
        file=await file.read() if file else None,
    )
    await redis.publish(RedisChannels.STARTED_JOB_CHANNEL.value, job.job_id)
    return JSONResponse({'job': job.__dict__}, status_code=202,  background=task)


@endpoint_handler()
@api_key_protected_endpoint()
async def process_job(request: Request):
    job_id = request.query_params.get('job_id')
    completed = request.query_params.get('completed') == 'True'
    failed = request.query_params.get('failed') == 'True'
    async with database.transaction():
        query = music_jobs.update().where(music_jobs.c.job_id ==
                                          job_id).values(completed=completed, failed=failed)
        await database.execute(query)
    await redis.publish(RedisChannels.COMPLETED_JOB_CHANNEL.value, job_id)
    return Response(None)


@endpoint_handler()
@authenticated_endpoint()
@database.transaction()
async def delete_job(request: Request):
    job_id = request.query_params.get('job_id')
    query = music_jobs.delete().where(music_jobs.c.job_id == job_id)
    await database.execute(query)
    try:
        await asyncio.create_subprocess_shell(f'rm -rf jobs/{job_id}')
    except:
        pass
    return Response(None)


@endpoint_handler()
@authenticated_endpoint()
async def download_job(request: Request):
    job_id = request.query_params.get('job_id')
    query = music_jobs.select().order_by(desc(music_jobs.c.started))
    job = await database.fetch_one(query)
    filename = sanitize_filename(f'{job.get("title")} {job.get("artist")}.mp3')
    file_path = os.path.join('jobs', job_id, filename)
    if not os.path.exists(file_path):
        async with database.transaction():
            query = music_jobs.update().where(music_jobs.c.job_id == job_id).values(failed=True)
            await database.execute(query)
        await redis.publish(RedisChannels.COMPLETED_JOB_CHANNEL.value, job_id)
        return Response(None, 404)
    return FileResponse(os.path.join('jobs', job_id, filename), filename=filename)
