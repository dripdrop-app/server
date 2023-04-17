import asyncio
import orjson
from contextlib import asynccontextmanager


@asynccontextmanager
async def _run(*args):
    process = None
    try:
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


async def download_audio_from_video(download_path: str = ..., url: str = ...):
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


async def extract_video_info(url: str = ...):
    async with _run("--no-playlist", "--dump-json", "--skip-download", url) as process:
        output = await process.stdout.read()
        if not output:
            return None
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


async def get_videos_playlist_length(url: str = ...):
    args = [*["--print", "n_entries"], "--skip-download", url]
    async with _run(*args) as process:
        async for line in _read_lines(process.stdout):
            return int(line)


async def extract_videos_info(
    url: str = ..., date_after: str | None = None, playlist_items: str | None = None
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
