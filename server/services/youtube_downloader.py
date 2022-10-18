import yt_dlp
from server.logging import logger


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        logger.warn(msg)

    def error(self, msg):
        logger.error(msg)


class YoutubeDownloaderService:
    def ytdlOptions(self, progress_hooks=[], folder: str = ...):
        return {
            "noplaylist": True,
            "format": "bestaudio/best",
            "outtmpl": "%(title)s.%(ext)s",
            "logging": Logger(),
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
        ytdl_options = self.ytdlOptions()
        ydl = yt_dlp.YoutubeDL(ytdl_options)
        info = ydl.extract_info(link, download=False)
        return info.get("uploader", None)

    def yt_download(
        self, link: str = ..., progress_hooks: list = [], folder: str = ...
    ):
        ytdl_options = self.ytdlOptions(progress_hooks, folder)
        ydl = yt_dlp.YoutubeDL(ytdl_options)
        return ydl.download([link])


youtuber_downloader_service = YoutubeDownloaderService()
