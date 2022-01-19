import yt_dlp


class Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        return


def ytdlOptions(progress_hooks, folder=""):
    return {
        "noplaylist": True,
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "logger": Logger(),
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


def extract_info(link: str):
    ytdl_options = ytdlOptions([])
    ydl = yt_dlp.YoutubeDL(ytdl_options)
    info = ydl.extract_info(link, download=False)
    return info.get("uploader", None)


def yt_download(link: str, progress_hooks, folder=""):
    ytdl_options = ytdlOptions(progress_hooks, folder)
    ydl = yt_dlp.YoutubeDL(ytdl_options)
    return ydl.download([link])
