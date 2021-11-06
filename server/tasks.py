import os
import subprocess
import traceback
import mutagen
import requests
import uuid
import io
import base64
import re
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from server.utils.imgdl import download_image
from server.utils.mp3dl import yt_download
from server.config import PORT, API_KEY


class Job:
    def __init__(self, job_id='', filename='', youtube_url='', artwork_url='', title='', artist='', album='', grouping=''):
        self.job_id = job_id
        self.filename = filename
        self.youtube_url = youtube_url
        self.artwork_url = artwork_url
        self.title = title
        self.artist = artist
        self.album = album
        self.grouping = grouping
        self.__dict__ = self._convert_to_dict()

    def _convert_to_dict(self):
        return {
            'job_id': self.job_id,
            'filename': self.filename,
            'youtube_url': self.youtube_url,
            'artwork_url': self.artwork_url,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'grouping': self.grouping
        }

    def __str__(self):
        return str(self.__dict__)


def download_task(job: Job, file: Union[str, bytes, None] = None):
    job_path = os.path.join('jobs', job.job_id)
    try:
        try:
            os.mkdir('jobs')
        except FileExistsError:
            pass
        os.mkdir(job_path)
        filename = ''

        if job.youtube_url:
            def updateProgress(d):
                nonlocal filename
                if d['status'] == 'finished':
                    filename = f'{".".join(d["filename"].split(".")[:-1])}.mp3'
            yt_download(job.youtube_url, [updateProgress], job_path)

        elif file:
            file_path = os.path.join(job_path, job.filename)
            with open(file_path, 'wb') as f:
                f.write(file)
            new_filename = f'{os.path.splitext(file_path)[0]}.mp3'
            AudioSegment.from_file(file_path).export(
                new_filename, format='mp3', bitrate='320k')
            filename = new_filename

        audio_file = mutagen.File(filename)

        if job.artwork_url:
            isBase64 = re.search("^data:image/", job.artwork_url)
            if isBase64:
                dataString = ','.join(job.artwork_url.split(',')[1:])
                data = dataString.encode()
                data_bytes = base64.b64decode(data)
                audio_file.tags.add(mutagen.id3.APIC(
                    mimetype='image/png', data=data_bytes)
                )
            else:
                try:
                    imageData = download_image(job.artwork_url)
                    audio_file.tags.add(mutagen.id3.APIC(
                        mimetype='image/png', data=imageData)
                    )
                except:
                    print(traceback.format_exc())

        audio_file.tags.add(mutagen.id3.TIT2(text=job.title))
        audio_file.tags.add(mutagen.id3.TPE1(text=job.artist))
        audio_file.tags.add(mutagen.id3.TALB(text=job.album))
        audio_file.tags.add(mutagen.id3.TIT1(text=job.grouping))
        audio_file.save()

        new_filename = os.path.join(
            job_path, sanitize_filename(f'{job.title} {job.artist}') + '.mp3')
        os.rename(filename, new_filename)
        response = requests.get(
            f'http://localhost:{PORT}/music/processJob',
            params={'job_id': job.job_id,
                    'completed': True, 'api_key': API_KEY}
        )
        if not response.ok:
            raise RuntimeError('Failed to update job status')

    except:
        subprocess.run(['rm', '-rf', job_path])
        print(traceback.format_exc())
        response = requests.get(
            f'http://localhost:{PORT}/music/processJob',
            params={'job_id': job.job_id, 'failed': True, 'api_key': API_KEY}
        )


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
            'artworkURL': f'data:{mimeType};base64,{base64.b64encode(buffer.getvalue()).decode()}' if buffer else None
        }
    except:
        subprocess.run(['rm', '-rf', tag_path])
        print(traceback.format_exc())
        return {
            'title': None,
            'artist': None,
            'album': None,
            'grouping': None,
            'artworkURL': None
        }
