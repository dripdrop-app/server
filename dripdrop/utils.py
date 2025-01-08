import asyncio
from datetime import datetime
from typing import Any, Coroutine, TypeVar
from urllib.parse import parse_qs, urlparse

from dripdrop.settings import settings

T = TypeVar("T")


async def gather_with_limit(
    *coroutines: Coroutine[Any, Any, T],
    limit: int = -1,
    return_exceptions=False,
) -> list[T]:
    semaphore = asyncio.Semaphore(value=limit if limit != -1 else len(coroutines))

    async def run_coro(coroutine: Coroutine):
        async with semaphore:
            return await coroutine

    tasks = [
        asyncio.create_task(run_coro(coroutine=coroutine)) for coroutine in coroutines
    ]
    return await asyncio.gather(*tasks, return_exceptions=return_exceptions)


def get_current_time():
    return datetime.now(tz=settings.timezone)


def parse_youtube_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    search_params = parse_qs(parsed_url.query)
    video_ids = search_params.get("v")
    if not video_ids:
        raise Exception("No video id found")
    return video_ids[0]
