import os
import traceback
import mutagen
import subprocess
import requests
from pydub import AudioSegment
from typing import Union
from yt_dlp.utils import sanitize_filename
from server.utils.imgdl import downloadImage
from server.utils.mp3dl import ytDownload


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
        response = requests.get(
            f'http://localhost:{os.getenv("PORT")}/completeJob', params={'jobID': jobID})
        if not response.ok:
            raise RuntimeError('Failed to update job status')

    except Exception as e:
        subprocess.run(['rm', '-rf', jobPath])
        print(traceback.format_exc())
