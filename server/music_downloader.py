import asyncio
from asyncio.tasks import Task
import uuid
import traceback
import os
from typing import Union
from sqlalchemy.sql.expression import desc
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool
from starlette.websockets import WebSocket, WebSocketDisconnect
from yt_dlp.utils import sanitize_filename
from server.utils.mp3dl import extractInfo
from server.utils.imgdl import downloadImage
from server.db import database, music_jobs
from server.redis import RedisChannels, subscribe, redis
from server.tasks import downloadTask, Job
from server.utils.helpers import endpointHandler, convertDBJob


@endpointHandler()
async def getGrouping(request: Request):
    youtubeURL = request.query_params.get('youtubeURL')
    uploader = await run_in_threadpool(extractInfo, youtubeURL)
    return JSONResponse({'grouping': uploader})


@endpointHandler()
async def getArtwork(request: Request):
    artworkURL = request.query_params.get('artworkURL')
    artworkURL = await run_in_threadpool(downloadImage, artworkURL, False)
    return JSONResponse({'artworkURL': artworkURL})


async def listenJobs(websocket: WebSocket):
    tasks: list[Task] = []
    try:
        await websocket.accept()
        query = music_jobs.select().order_by(desc(music_jobs.c.started))
        jobs = await database.fetch_all(query)
        await websocket.send_json({
            'type': 'ALL',
            'jobs': [convertDBJob(job) for job in jobs]
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
        if not isinstance(e, WebSocketDisconnect):
            print(traceback.format_exc())
        for task in tasks:
            task.cancel()
        await websocket.close()


@endpointHandler()
async def download(request: Request):
    jobID = str(uuid.uuid4())
    form = await request.form()
    youtubeURL = form.get('youtubeURL')
    file: Union[UploadFile, None] = form.get('file')
    artworkURL = form.get('artworkURL')
    title = form.get('title')
    artist = form.get('artist')
    album = form.get('album')
    grouping = form.get('grouping')

    if not youtubeURL and not file:
        return Response(None, 400)

    job = Job(
        jobID=jobID,
        filename=file.filename if file else None,
        youtubeURL=youtubeURL,
        artworkURL=artworkURL,
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
        downloadTask,
        job,
        file=await file.read() if file else None,
    )
    await redis.publish(RedisChannels.STARTED_JOB_CHANNEL.value, job.jobID)
    return JSONResponse({'job': job.__dict__}, background=task)


@endpointHandler()
async def processJob(request: Request):
    jobID = request.query_params.get('jobID')
    completed = request.query_params.get('completed') == 'True'
    failed = request.query_params.get('failed') == 'True'
    async with database.transaction():
        query = music_jobs.update().where(music_jobs.c.jobID ==
                                          jobID).values(completed=completed, failed=failed)
        await database.execute(query)
    await redis.publish(RedisChannels.COMPLETED_JOB_CHANNEL.value, jobID)
    return Response(None)


@endpointHandler()
@database.transaction()
async def deleteJob(request: Request):
    jobID = request.query_params.get('jobID')
    query = music_jobs.delete().where(music_jobs.c.jobID == jobID)
    await database.execute(query)
    try:
        await asyncio.create_subprocess_shell(f'rm -rf jobs/{jobID}')
    except:
        pass
    return Response(None)


@endpointHandler()
async def downloadJob(request: Request):
    jobID = request.query_params.get('jobID')
    query = music_jobs.select().order_by(desc(music_jobs.c.started))
    job = await database.fetch_one(query)
    filename = sanitize_filename(f'{job.get("title")} {job.get("artist")}.mp3')
    filepath = os.path.join('jobs', jobID, filename)
    if not os.path.exists(filepath):
        async with database.transaction():
            query = music_jobs.update().where(music_jobs.c.jobID == jobID).values(failed=True)
            await database.execute(query)
        await redis.publish(RedisChannels.COMPLETED_JOB_CHANNEL.value, jobID)
        return Response(None, 404)
    return FileResponse(os.path.join('jobs', jobID, filename), filename=filename)
