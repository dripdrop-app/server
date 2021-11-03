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
from server.utils.imgdl import downloadImage
from server.utils.mp3dl import ytDownload
from starlette.config import Config

config = Config('.env')
PORT = config.get('PORT')


class Job:
    def __init__(self, jobID='', filename='', youtubeURL='', artworkURL='', title='', artist='', album='', grouping=''):
        self.jobID = jobID
        self.filename = filename
        self.youtubeURL = youtubeURL
        self.artworkURL = artworkURL
        self.title = title
        self.artist = artist
        self.album = album
        self.grouping = grouping
        self.__dict__ = self._convertToDict()

    def _convertToDict(self):
        return {
            'jobID': self.jobID,
            'filename': self.filename,
            'youtubeURL': self.youtubeURL,
            'artworkURL': self.artworkURL,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'grouping': self.grouping
        }

    def __str__(self):
        return str(self.__dict__)


def downloadTask(job: Job, file: Union[str, bytes, None] = None):
    jobPath = os.path.join('jobs', job.jobID)
    try:
        try:
            os.mkdir('jobs')
        except FileExistsError:
            pass
        os.mkdir(jobPath)
        fileName = ''

        if job.youtubeURL:
            def updateProgress(d):
                nonlocal fileName
                if d['status'] == 'finished':
                    fileName = f'{".".join(d["filename"].split(".")[:-1])}.mp3'
            ytDownload(job.youtubeURL, [updateProgress], jobPath)

        elif file:
            filepath = os.path.join(jobPath, job.filename)
            with open(filepath, 'wb') as f:
                f.write(file)
            newFileName = f'{os.path.splitext(filepath)[0]}.mp3'
            AudioSegment.from_file(filepath).export(
                newFileName, format='mp3', bitrate='320k')
            fileName = newFileName

        audioFile = mutagen.File(fileName)

        if job.artworkURL:
            isBase64 = re.search("^data:image/", job.artworkURL)
            if isBase64:
                dataString = ','.join(job.artworkURL.split(',')[1:])
                data = dataString.encode()
                data_bytes = base64.b64decode(data)
                audioFile.tags.add(mutagen.id3.APIC(
                    mimetype='image/png', data=data_bytes)
                )
            else:
                try:
                    imageData = downloadImage(job.artworkURL)
                    audioFile.tags.add(mutagen.id3.APIC(
                        mimetype='image/png', data=imageData)
                    )
                except:
                    print(traceback.format_exc())

        audioFile.tags.add(mutagen.id3.TIT2(text=job.title))
        audioFile.tags.add(mutagen.id3.TPE1(text=job.artist))
        audioFile.tags.add(mutagen.id3.TALB(text=job.album))
        audioFile.tags.add(mutagen.id3.TIT1(text=job.grouping))
        audioFile.save()

        newFileName = os.path.join(
            jobPath, sanitize_filename(f'{job.title} {job.artist}') + '.mp3')
        os.rename(fileName, newFileName)
        response = requests.get(
            f'http://localhost:{PORT}/processJob', params={'jobID': job.jobID, 'completed': True})
        if not response.ok:
            raise RuntimeError('Failed to update job status')

    except:
        subprocess.run(['rm', '-rf', jobPath])
        print(traceback.format_exc())
        response = requests.get(
            f'http://localhost:{PORT}/processJob', params={'jobID': job.jobID, 'failed': True})


def readTags(file: Union[str, bytes, None], filename):
    folderID = str(uuid.uuid4())
    tagPath = os.path.join('tags', folderID)

    try:
        try:
            os.mkdir('tags')
        except FileExistsError:
            pass
        os.mkdir(tagPath)

        filepath = os.path.join(tagPath, filename)
        with open(filepath, 'wb') as f:
            f.write(file)
        audioFile = mutagen.File(filepath)
        title = audioFile.tags['TIT2'].text[0] if audioFile.tags.get(
            'TIT2', None) else ''
        artist = audioFile.tags['TPE1'].text[0] if audioFile.tags.get(
            'TPE1', None) else ''
        album = audioFile.tags['TALB'].text[0] if audioFile.tags.get(
            'TALB', None) else ''
        grouping = audioFile.tags['TIT1'].text[0] if audioFile.tags.get(
            'TIT1', None) else ''
        imageKeys = list(
            filter(lambda key: key.find('APIC') != -1, audioFile.keys()))
        buffer = None
        mimeType = None
        if imageKeys:
            mimeType = audioFile[imageKeys[0]].mime
            buffer = io.BytesIO(audioFile[imageKeys[0]].data)
        subprocess.run(['rm', '-rf', tagPath])
        return {
            'title': title,
            'artist': artist,
            'album': album,
            'grouping': grouping,
            'artworkURL': f'data:{mimeType};base64,{base64.b64encode(buffer.getvalue()).decode()}' if buffer else None
        }
    except:
        subprocess.run(['rm', '-rf', tagPath])
        print(traceback.format_exc())
        return {
            'title': None,
            'artist': None,
            'album': None,
            'grouping': None,
            'artworkURL': None
        }
