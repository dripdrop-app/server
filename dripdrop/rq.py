import asyncio
from redis import Redis
from rq import Queue
from rq.command import send_stop_job_command
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus
from typing import Coroutine

from dripdrop.settings import ENV, settings
from dripdrop.logging import logger

queue = Queue(
    connection=Redis.from_url(settings.redis_url), default_timeout=settings.timeout
)


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


def stop_job(job_id: str = ...):
    try:
        job = Job.fetch(job_id, connection=queue.connection)
        status = job.get_status()
        if status == JobStatus.SCHEDULED:
            job.cancel()
        elif status == JobStatus.STARTED:
            send_stop_job_command(queue.connection, job_id)
        logger.info(f"Stopped job {job.get_call_string()}")
        job.delete(delete_dependents=True)
    except NoSuchJobError:
        pass
