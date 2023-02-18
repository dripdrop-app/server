import os
import yt_dlp
from asgiref.sync import sync_to_async
from pydub import AudioSegment

from dripdrop.logging import logger


class AudioService:
    def _create_options(self, progress_hooks=[], folder: str = ..., playlist=False):
        return {
            "noplaylist": not playlist,
            "format": "bestaudio/best",
            "logging": logger,
            "progress_hooks": progress_hooks,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "paths": {"home": folder},
        }

    def extract_info(self, link: str = ...):
        ytdl_options = self._create_options()
        ydl = yt_dlp.YoutubeDL(ytdl_options)
        info = ydl.sanitize_info(ydl.extract_info(link, download=False))
        return info

    async def async_extract_info(self, link: str = ...):
        extract_info = sync_to_async(self.extract_info)
        return await extract_info(link=link)

    def download(
        self,
        link: str = ...,
        folder: str = ...,
    ):
        filename = None

        def updateProgress(d):
            nonlocal filename
            if d["status"] == "finished":
                filename = f'{os.path.splitext(d["filename"])[0]}.mp3'

        options = self._create_options(progress_hooks=[updateProgress], folder=folder)
        ydl = yt_dlp.YoutubeDL(params=options)
        error_code = ydl.download([link])
        if error_code != 0:
            raise Exception("Failed to download audio")
        return filename

    def convert_to_mp3(self, file_path: str = ..., new_file_path: str = ...):
        AudioSegment.from_file(file=file_path).export(
            new_file_path, format="mp3", bitrate="320k"
        )


audio_service = AudioService()
