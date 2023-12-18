import asyncio
import orjson
from contextlib import asynccontextmanager

from dripdrop.services import redis_client

UPDATING_YTDLP = "UPDATING_YTDLP"


async def check_and_update_ytdlp():
    async with redis_client.create_client() as redis:
        if await redis.get(UPDATING_YTDLP):
            return
        await redis.set(UPDATING_YTDLP, "1", ex=60 * 60 * 24)
        process = await asyncio.subprocess.create_subprocess_exec(
            "pip",
            "install",
            "-U",
            "yt-dlp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(process.wait(), timeout=60 * 5)
        finally:
            pass


@asynccontextmanager
async def _run(*args):
    process = None
    try:
        await check_and_update_ytdlp()
        process = await asyncio.subprocess.create_subprocess_exec(
            "yt-dlp",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        yield process
    finally:
        if process:
            if process.returncode is None:
                process.kill()
            await process.wait()


async def download_audio_from_video(download_path: str, url: str):
    args = [
        "--no-playlist",
        "--extract-audio",
        *["--audio-format", "mp3"],
        *["--audio-quality", "0"],
        *["--output", download_path],
        url,
    ]
    async with _run(*args) as process:
        await process.wait()


async def extract_video_info(url: str):
    async with _run("--no-playlist", "--dump-json", "--skip-download", url) as process:
        output = await process.stdout.read()
        error = await process.stderr.read()
        if process.returncode != 0:
            raise Exception(error.decode())
        return await asyncio.to_thread(orjson.loads, output)


async def _read_lines(stream):
    while not stream.at_eof():
        line = ""
        while True:
            output = await stream.read(1)
            output = output.decode()
            if not output or output == "\n":
                yield line
                break
            line += output


async def get_videos_playlist_length(url: str):
    args = [*["--print", "n_entries"], "--skip-download", url]
    async with _run(*args) as process:
        async for line in _read_lines(process.stdout):
            try:
                return int(line)
            except ValueError:
                error = await process.stderr.read()
                raise Exception(error.decode())


async def extract_videos_info(
    url: str, date_after: str | None = None, playlist_items: str | None = None
):
    args = [
        "--lazy-playlist",
        "--break-on-reject",
        "--dump-json",
        "--skip-download",
    ]
    if date_after:
        args.extend(["--dateafter", date_after])
    if playlist_items:
        args.extend(["--playlist-items", playlist_items])
    args.extend([url])
    async with _run(*args) as process:
        async for line in _read_lines(process.stdout):
            try:
                yield await asyncio.to_thread(orjson.loads, line)
            except orjson.JSONDecodeError:
                pass
