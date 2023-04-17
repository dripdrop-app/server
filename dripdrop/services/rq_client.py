import asyncio
from redis import Redis
from rq import Queue
from rq.command import send_stop_job_command
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus, Dependency
from typing import Coroutine

from dripdrop.settings import settings
from dripdrop.logger import logger

queue = Queue(
    connection=Redis.from_url(settings.redis_url), default_timeout=settings.timeout
)


def report_job_time(job: Job, *args):
    if job.ended_at and job.started_at:
        job_duration = job.ended_at - job.started_at
        logger.info(
            "Job ({id}) {status} in {seconds} seconds".format(
                id=job.id,
                status="failed" if job.is_failed else "completed",
                seconds=job_duration.seconds,
            )
        )


async def enqueue(
    function: Coroutine = ...,
    args: tuple = (),
    kwargs: dict = {},
    job_id: str = None,
    depends_on: list[Job | str] = [],
    run_on_depends_failure=False,
    at_front=False,
):
    dependency = None
    if depends_on:
        dependency = Dependency(jobs=depends_on, allow_failure=run_on_depends_failure)
    return await asyncio.to_thread(
        queue.enqueue,
        function,
        args=args,
        kwargs=kwargs,
        job_id=job_id,
        depends_on=dependency,
        at_front=at_front,
        on_success=report_job_time,
        on_failure=report_job_time,
    )


def stop_job(job_id: str = ...):
    try:
        job = Job.fetch(job_id, connection=queue.connection)
        status = job.get_status()
        if status == JobStatus.SCHEDULED:
            job.cancel()
        elif status == JobStatus.STARTED:
            send_stop_job_command(queue.connection, job_id)
        logger.info(f"Stopped job {job.get_call_string()} ({job.args}, {job.kwargs})")
        job.delete(delete_dependents=True)
    except NoSuchJobError:
        logger.info(f"Job not found ({job_id})")
        pass
