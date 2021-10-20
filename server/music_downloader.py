import uuid
import traceback
from typing import Union
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool
from server.utils.mp3dl import extractInfo
from server.utils.imgdl import downloadImage
from server.db import database, music_jobs
from server.tasks import downloadTask


async def getGrouping(request: Request):
    youtubeURL = request.query_params.get('youtubeURL')
    try:
        uploader = await run_in_threadpool(extractInfo, youtubeURL)
        return JSONResponse({'grouping': uploader})
    except Exception as e:
        print(traceback.format_exc())
        return Response(None, 400)


async def completeJob(request: Request):
    transaction = await database.transaction()
    jobID = request.query_params.get('jobID')
    try:
        query = music_jobs.update().where(music_jobs.c.job_id ==
                                          jobID).values(completed=True)
        await database.execute(query)
        await transaction.commit()
        return Response(None)
    except:
        await transaction.rollback()
        return Response(None, 400)


async def getArtwork(request: Request):
    artworkURL = request.query_params.get('artworkURL')
    try:
        artworkURL = await run_in_threadpool(downloadImage, artworkURL, False)
        return JSONResponse({'artworkURL': artworkURL})
    except Exception as e:
        print(traceback.format_exc())
        return Response(None, 400)


async def download(request: Request):
    transaction = await database.transaction()
    try:
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

        try:
            query = music_jobs.insert().values(job_id=jobID, completed=False)
            await database.execute(query)
        except Exception as e:
            await transaction.rollback()
            raise e

        task = BackgroundTask(
            downloadTask,
            jobID,
            youtubeURL=youtubeURL,
            origFileName=file.filename if file else None,
            file=await file.read() if file else None,
            artworkURL=artworkURL,
            title=title,
            artist=artist,
            album=album,
            grouping=grouping
        )

        await transaction.commit()
        return JSONResponse({'jobID': jobID}, background=task)

    except Exception as e:
        print(traceback.format_exc())
        return Response(None, 400)
