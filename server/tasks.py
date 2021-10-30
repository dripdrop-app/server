import os
import subprocess
import traceback
import mutagen
import requests
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
            imageData = downloadImage(job.artworkURL)
            audioFile.tags.add(mutagen.id3.APIC(
                mimetype='image/png', data=imageData))

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
