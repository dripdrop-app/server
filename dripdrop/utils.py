import asyncio
from typing import Coroutine, TypeVar, Any

T = TypeVar("T")


async def gather_with_limit(
    *coroutines: Coroutine[Any, Any, T], limit: int = -1
) -> list[T]:
    semaphore = asyncio.Semaphore(value=limit if limit != -1 else len(coroutines))

    async def run_coro(coroutine: Coroutine = ...):
        async with semaphore:
            return await coroutine

    tasks = [run_coro(coroutine=coroutine) for coroutine in coroutines]
    return await asyncio.gather(*tasks)
