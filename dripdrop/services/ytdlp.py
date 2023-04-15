import asyncio
import os
import orjson
from io import TextIOWrapper
from yt_dlp.utils import sanitize_filename

from dripdrop.services import temp_files


async def _run(*args, stdout: TextIOWrapper | int = asyncio.subprocess.PIPE):
    process = await asyncio.subprocess.create_subprocess_exec(
        "yt-dlp",
        *args,
        stdout=stdout,
        stderr=asyncio.subprocess.PIPE,
    )
    output = None
    if process.stdout:
        output = await process.stdout.read()
        output = output.decode().splitlines()
    return_code = await process.wait()
    if return_code in [1, 2, 100]:
        error = await process.stderr.read()
        raise Exception(error.decode())
    return output


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
    url_info_path = os.path.join(videos_info_path, f"{sanitize_filename(url)}.json")
    try:
        args = [
            "--lazy-playlist",
            "--break-on-reject",
            "--dump-json",
            "--skip-download",
        ]
        if date_after:
            args.extend(["--dateafter", date_after])
        args.extend([url])
        with open(file=url_info_path, mode="w") as f:
            await _run(*args, stdout=f)
        with open(file=url_info_path, mode="r") as f:
            json = await asyncio.to_thread(f.readline)
            yield await asyncio.to_thread(orjson.loads, json)
    except Exception as e:
        raise e
    finally:
        if os.stat(path=url_info_path):
            await asyncio.to_thread(os.remove, url_info_path)
