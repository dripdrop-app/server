import asyncio
import os

TEMP_DIRECTORY = "temp"


async def _create_temp_directory():
    try:
        await asyncio.to_thread(os.mkdir, TEMP_DIRECTORY)
    except FileExistsError:
        pass


async def create_new_directory(directory: str = ..., raise_on_exists=True):
    directory_path = os.path.join(TEMP_DIRECTORY, os.path.normpath(directory))
    await _create_temp_directory()
    if not raise_on_exists:
        try:
            await asyncio.to_thread(os.mkdir, directory_path)
        except FileExistsError:
            pass
    else:
        await asyncio.to_thread(os.mkdir, directory_path)
    return directory_path
