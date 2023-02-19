from rq import Queue
from rq.job import Job
from typing import Coroutine

from dripdrop.redis import redis
from dripdrop.settings import ENV, settings

queue = Queue(connection=redis, default_timeout=-1, is_async=False)


# Mock rq's behavior when running with is_async=True to handle async code
async def enqueue(
    function: Coroutine = ...,
    args: tuple = (),
    kwargs: dict = {},
    depends_on: Job = None,
    at_front=False,
):
    if settings.env == ENV.TESTING:
        await function(*args, **kwargs)
        return None
    return queue.enqueue(
        f=function, args=args, kwargs=kwargs, depends_on=depends_on, at_front=at_front
    )
