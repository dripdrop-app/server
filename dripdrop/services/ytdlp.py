import asyncio
import json


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
    return await _run(*args)


async def extract_videos_info(
    url: str = ...,
    date_after: str | None = None,
):
    args = [
        "--lazy-playlist",
        "--break-on-reject",
        "--dump-json",
    ]
    if date_after:
        args.extend(["--dateafter", date_after])
    args.extend([url])
    output = [json.loads(json_string) for json_string in await _run(*args)]
    return output
