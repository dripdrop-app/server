import asyncio
from redis import Redis
from rq import Queue
from rq.job import Job
from typing import Coroutine

from dripdrop.settings import ENV, settings

connection = Redis.from_url(settings.redis_url)

queue = Queue(connection=connection, default_timeout=settings.timeout)

scheduled_registry = queue.scheduled_job_registry


async def enqueue(
    function: Coroutine = ...,
    args: tuple = (),
    kwargs: dict = {},
    job_id: str = None,
    depends_on: Job = None,
    at_front=False,
):
    if settings.env == ENV.TESTING:
        await asyncio.wait_for(function(*args, **kwargs), timeout=settings.timeout)
        return None
    return queue.enqueue(
        function,
        args=args,
        kwargs=kwargs,
        job_id=job_id,
        depends_on=depends_on,
        at_front=at_front,
    )
