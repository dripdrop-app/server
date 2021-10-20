import subprocess
import mutagen
import os
import uuid
import traceback
import requests
from typing import Union
from starlette.background import BackgroundTask
from starlette.datastructures import UploadFile
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool
from pydub import AudioSegment
from yt_dlp.utils import sanitize_filename
from server.utils.mp3dl import ytDownload, extractInfo
from server.utils.imgdl import downloadImage
from server.db import database, music_jobs


async def getGrouping(request: Request):
    form = await request.form()
    youtubeURL = form.get('youtubeURL')
    try:
        uploader = await run_in_threadpool(extractInfo, youtubeURL)
        return JSONResponse({'grouping': uploader})
    except Exception as e:
        print(traceback.format_exc())
        return Response(None, 400)


async def completeJob(request: Request):
    transaction = await database.transaction()
    form = await request.form()
    jobID = form.get('jobID')
    try:
        query = music_jobs.update().where(music_jobs.c.job_id ==
                                          jobID).values(completed=True)
        await database.execute(query)
        await transaction.commit()
        return Response(None, 200)
    except:
        await transaction.rollback()
        return Response(None, 400)


def downloadTask(jobID: str, youtubeURL='', origFileName='', file: Union[str, bytes, None] = None, artworkURL='', title='', artist='', album='', grouping=''):
    jobPath = os.path.join('jobs', jobID)
    try:
        subprocess.run(['mkdir', 'jobs'])
        subprocess.run(['mkdir', jobPath])
        fileName = ''

        if youtubeURL:
            def updateProgress(d):
                nonlocal fileName
                if d['status'] == 'finished':
                    fileName = f'{".".join(d["filename"].split(".")[:-1])}.mp3'
            ytDownload(youtubeURL, [updateProgress], jobPath)

        elif file:
            filepath = os.path.join(jobPath, origFileName)
            with open(filepath) as f:
                f.write(file)
            newFileName = f'{os.path.splitext(filepath)[:-1]}.mp3'
            AudioSegment.from_file(filepath).export(
                newFileName, format='mp3', bitrate='320k')
            fileName = newFileName

        audioFile = mutagen.File(fileName)

        if artworkURL:
            imageData = downloadImage(artworkURL)
            audioFile.tags.add(mutagen.id3.APIC(
                mimetype='image/png', data=imageData))

        audioFile.tags.add(mutagen.id3.TIT2(text=title))
        audioFile.tags.add(mutagen.id3.TPE1(text=artist))
        audioFile.tags.add(mutagen.id3.TALB(text=album))
        audioFile.tags.add(mutagen.id3.TIT1(text=grouping))
        audioFile.save()

        newFileName = os.path.join(
            jobPath, sanitize_filename(f'{title} {artist}') + '.mp3')
        subprocess.run(['mv', '-f', fileName, newFileName])
        response = requests.post(
            f'http://localhost:{os.getenv("PORT")}/completeJob', data={'jobID': jobID})
        if not response.ok:
            raise RuntimeError('Failed to update job status')

    except Exception as e:
        subprocess.run(['rm', '-rf', jobPath])
        print(traceback.format_exc())


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
