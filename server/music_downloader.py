import asyncio
import uuid
import traceback
import datetime
from typing import Union
from sqlalchemy.sql.expression import desc
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool
from starlette.websockets import WebSocket, WebSocketDisconnect
from server.utils.mp3dl import extractInfo
from server.utils.imgdl import downloadImage
from server.db import database, music_jobs
from server.redis import JOB_CHANNEL, subscribe, redis
from server.tasks import downloadTask, Job
from server.utils.helpers import endpointHandler


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


@endpointHandler()
async def processJob(request: Request):
    jobID = request.query_params.get('jobID')
    completed = request.query_params.get('completed') == 'True'
    failed = request.query_params.get('failed') == 'True'
    async with database.transaction():
        query = music_jobs.update().where(music_jobs.c.jobID ==
                                          jobID).values(completed=completed, failed=failed)
        await database.execute(query)
    await redis.publish(JOB_CHANNEL, jobID)
    return Response(None)


@endpointHandler()
async def getJobs(request: Request):
    query = music_jobs.select().order_by(desc(music_jobs.c.started))
    jobs = await database.fetch_all(query)
    return JSONResponse({'jobs': [
        {
            key: value.__str__() if isinstance(
                value, datetime.datetime) else value
            for key, value in job.items()
        }
        for job in jobs
    ]})


async def listenJobs(websocket: WebSocket):
    try:
        await websocket.accept()

        while True:
            json = await websocket.receive_json()
            jobIDs = {
                jobID: True
                for jobID in json.get('jobIDs')
            }

            if jobIDs.keys() is not None and len(jobIDs.keys()) > 0:
                async def onMessage(msg):
                    if msg and msg.get('type') == 'message':
                        completedJobID = msg.get('data').decode()
                        if jobIDs.get(completedJobID, False):
                            del jobIDs[completedJobID]
                            query = music_jobs.select().where(music_jobs.c.jobID == completedJobID)
                            jobs = await database.fetch_all(query)
                            await websocket.send_json({'jobs': [
                                {
                                    key: value.__str__() if isinstance(
                                        value, datetime.datetime) else value
                                    for key, value in job.items()
                                }
                                for job in jobs
                            ]})
                            if len(jobIDs.keys()) == 0:
                                return True
                    return False
                asyncio.create_task(subscribe(JOB_CHANNEL, onMessage))

    except Exception as e:
        if not isinstance(e, WebSocketDisconnect):
            print(traceback.format_exc())
        await websocket.close()


@endpointHandler()
@database.transaction()
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

    return JSONResponse({'job': job.__dict__}, background=task)


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
