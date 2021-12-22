import asyncio
import base64
import io
import mutagen
import os
import re
import subprocess
import traceback
import uuid
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from starlette.concurrency import run_in_threadpool
from server.db import database, music_jobs
from server.redis import redis
from server.utils.imgdl import download_image
from server.utils.mp3dl import yt_download
from server.utils.enums import RedisChannels
from server.utils.wrappers import exception_handler, worker_task


JOB_DIR = 'music_jobs'


@exception_handler()
@worker_task()
async def run_job(job_id: str):
    query = music_jobs.select().where(music_jobs.c.id == job_id)
    job = await database.fetch_one(query)

    try:
        if job:
            def download_and_set_tags():
                job_path = os.path.join(JOB_DIR, job_id)
                youtube_url = job.get('youtube_url', None)
                filename = job.get('filename', '')
                artwork_url = job.get('artwork_url', None)
                title = job.get('title')
                artist = job.get('artist')
                album = job.get('album')
                grouping = job.get('grouping', None)

                if youtube_url:
                    def updateProgress(d):
                        nonlocal filename
                        if d['status'] == 'finished':
                            filename = f'{".".join(d["filename"].split(".")[:-1])}.mp3'
                    yt_download(youtube_url, [updateProgress], job_path)
                elif filename:
                    file_path = os.path.join(job_path, filename)
                    new_filename = f'{os.path.splitext(file_path)[0]}.mp3'
                    AudioSegment.from_file(file_path).export(
                        new_filename, format='mp3', bitrate='320k')
                    filename = new_filename

                audio_file = mutagen.File(filename)

                if artwork_url:
                    isBase64 = re.search("^data:image/", artwork_url)
                    if isBase64:
                        dataString = ','.join(artwork_url.split(',')[1:])
                        data = dataString.encode()
                        data_bytes = base64.b64decode(data)
                        audio_file.tags.add(mutagen.id3.APIC(
                            mimetype='image/png', data=data_bytes)
                        )
                    else:
                        try:
                            imageData = download_image(artwork_url)
                            audio_file.tags.add(mutagen.id3.APIC(
                                mimetype='image/png', data=imageData)
                            )
                        except:
                            print(traceback.format_exc())

                audio_file.tags.add(mutagen.id3.TIT2(text=title))
                audio_file.tags.add(mutagen.id3.TPE1(text=artist))
                audio_file.tags.add(mutagen.id3.TALB(text=album))
                audio_file.tags.add(mutagen.id3.TIT1(text=grouping))
                audio_file.save()

                new_filename = os.path.join(
                    job_path, sanitize_filename(f'{title} {artist}') + '.mp3')
                os.rename(filename, new_filename)

            await run_in_threadpool(download_and_set_tags)

            async with database.transaction():
                query = music_jobs.update().where(music_jobs.c.id ==
                                                  job_id).values(completed=True)
                await database.execute(query)
            await redis.publish(RedisChannels.COMPLETED_MUSIC_JOB_CHANNEL.value, job_id)
    except Exception as e:
        if job:
            async with database.transaction():
                query = music_jobs.update().where(music_jobs.c.job_id ==
                                                  job_id).values(failed=True)
                await database.execute(query)
            await asyncio.create_subprocess_shell(f'rm -rf {JOB_DIR}/{job_id}')
            raise e


def read_tags(file: Union[str, bytes, None], filename):
    folder_id = str(uuid.uuid4())
    tag_path = os.path.join('tags', folder_id)

    try:
        try:
            os.mkdir('tags')
        except FileExistsError:
            pass
        os.mkdir(tag_path)

        filepath = os.path.join(tag_path, filename)
        with open(filepath, 'wb') as f:
            f.write(file)
        audio_file = mutagen.File(filepath)
        title = audio_file.tags['TIT2'].text[0] if audio_file.tags.get(
            'TIT2', None) else ''
        artist = audio_file.tags['TPE1'].text[0] if audio_file.tags.get(
            'TPE1', None) else ''
        album = audio_file.tags['TALB'].text[0] if audio_file.tags.get(
            'TALB', None) else ''
        grouping = audio_file.tags['TIT1'].text[0] if audio_file.tags.get(
            'TIT1', None) else ''
        imageKeys = list(
            filter(lambda key: key.find('APIC') != -1, audio_file.keys()))
        buffer = None
        mimeType = None
        if imageKeys:
            mimeType = audio_file[imageKeys[0]].mime
            buffer = io.BytesIO(audio_file[imageKeys[0]].data)
        subprocess.run(['rm', '-rf', tag_path])
        return {
            'title': title,
            'artist': artist,
            'album': album,
            'grouping': grouping,
            'artwork_url': f'data:{mimeType};base64,{base64.b64encode(buffer.getvalue()).decode()}' if buffer else None
        }
    except:
        subprocess.run(['rm', '-rf', tag_path])
        print(traceback.format_exc())
        return {
            'title': None,
            'artist': None,
            'album': None,
            'grouping': None,
            'artwork_url': None
        }
