import asyncio
from datetime import datetime
from typing import Coroutine, TypeVar, Any

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
