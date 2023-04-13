import asyncio
import os
import orjson
import shutil
from contextlib import asynccontextmanager
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
    return_code = await process.wait()
    if return_code in [1, 2, 100]:
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


async def _stream_files(path: str = ...):
    with os.scandir(path=path) as it:
        for file in it:
            if file.is_file() and file.name.endswith(".json"):
                text = None
                with open(file.path, "r") as f:
                    text = await asyncio.to_thread(f.read)
                yield await asyncio.to_thread(orjson.loads, text)
                await asyncio.to_thread(os.remove, file.path)


@asynccontextmanager
async def extract_videos_info(url: str = ..., date_after: str | None = None):
    VIDEOS_INFO_DIRECTORY = "videos_info"

    videos_info_path = await temp_files.create_new_directory(
        directory=VIDEOS_INFO_DIRECTORY, raise_on_exists=False
    )
    url_info_path = os.path.join(videos_info_path, sanitize_filename(url))
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
        yield _stream_files(path=url_info_path)
    except Exception as e:
        raise e
    finally:
        await asyncio.to_thread(shutil.rmtree, url_info_path)
