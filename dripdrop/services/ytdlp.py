import asyncio
import os
import orjson
import shutil
from yt_dlp.utils import sanitize_filename

from dripdrop.services import temp_files

EXECUTABLE = "yt-dlp"


async def _run(*args):
    process = await asyncio.subprocess.create_subprocess_exec(
        EXECUTABLE,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    output = await process.stdout.read()
    error = await process.stderr.read()
    await process.wait()
    if error:
        raise Exception(error.decode())
    return output.decode().splitlines()


async def download_audio_from_video(download_path: str = ..., url: str = ...):
    args = [
        "--no-playlist",
        "--extract-audio",
        *["--audio-format", "mp3"],
        *["--audio-quality", "0"],
        *["--output", download_path],
        url,
    ]
    await _run(*args)


async def extract_video_info(url: str = ...):
    jsons = await _run("--lazy-playlist", "--break-on-reject", "--dump-json", url)
    if not jsons:
        return None
    return await asyncio.to_thread(orjson.loads, jsons[0])


async def extract_videos_info(url: str = ..., date_after: str | None = None):
    VIDEOS_INFO_DIRECTORY = "videos_info"

    videos_info_path = await temp_files.create_new_directory(
        directory=VIDEOS_INFO_DIRECTORY, raise_on_exists=False
    )
    url_info_path = os.path.join(videos_info_path, sanitize_filename(url))
    if os.path.exists(url_info_path):
        await asyncio.to_thread(shutil.rmtree, url_info_path)
    await asyncio.to_thread(os.mkdir, url_info_path)
    try:
        args = [
            "--lazy-playlist",
            "--break-on-reject",
            "--write-info-json",
            "--no-write-playlist-metafiles",
            "--skip-download",
            "-o",
            os.path.join(url_info_path, "%(title)s.%(ext)s"),
        ]
        if date_after:
            args.extend(["--dateafter", date_after])
        args.extend([url])
        await _run(*args)
        with os.scandir(path=url_info_path) as it:
            for file in it:
                if file.is_file() and file.name.endswith(".json"):
                    with open(file.path, "r") as f:
                        text = await asyncio.to_thread(f.read)
                        yield await asyncio.to_thread(orjson.loads, text)
    except Exception as e:
        raise e
    finally:
        await asyncio.to_thread(shutil.rmtree, url_info_path)
