import asyncio
import os


async def convert_audio_to_mp3(audio_file: str):
    root, ext = os.path.splitext(audio_file)
    if ext == ".mp3":
        return audio_file
    output_filename = f"{root}.mp3"
    process = await asyncio.subprocess.create_subprocess_exec(
        "ffmpeg",
        "-i",
        audio_file,
        "-b:a",
        "320k",
        output_filename,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    error = await process.stderr.read()
    await process.wait()
    if process.returncode != 0:
        raise Exception(error.decode())
    return output_filename
