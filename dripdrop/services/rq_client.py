import asyncio
from inspect import signature
from redis import Redis
from rq import Queue, get_current_job
from rq.command import send_stop_job_command
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus

from dripdrop.services import database
from dripdrop.settings import settings, ENV
from dripdrop.logger import logger

connection = Redis.from_url(settings.redis_url)


def report_job_time(job: Job, *_):
    if job.ended_at and job.started_at:
        job_duration = job.ended_at - job.started_at
        logger.info(
            "Job ({description}) {status} in {seconds} seconds".format(
                description=job.description,
                status="failed" if job.is_failed else "completed",
                seconds=job_duration.seconds,
            )
        )


class CustomJob(Job):
    @classmethod
    def create(cls, *args, on_success=None, on_failure=None, **kwargs):
        return super().create(
            *args,
            **kwargs,
            on_success=on_success if on_success else report_job_time,
            on_failure=on_failure if on_failure else report_job_time,
        )

    async def _async_execute(self):
        func_signature = signature(self.func)
        parameters = func_signature.parameters
        if "session" in parameters:
            async with database.create_session() as session:
                return await self.func(*self.args, session=session, **self.kwargs)

    def _execute(self):
        func_signature = signature(self.func)
        parameters = func_signature.parameters
        if "job" in parameters:
            self.kwargs["job"] = get_current_job()
        if asyncio.iscoroutinefunction(self.func):
            return asyncio.run(self._async_execute())
        return self.func(*self.args, **self.kwargs)


queue_settings = {
    "connection": connection,
    "default_timeout": settings.timeout,
    "is_async": settings.env != ENV.TESTING,
    "job_class": CustomJob,
}
default = Queue(**queue_settings)
high = Queue(name="high", **queue_settings)


def stop_job(job_id: str):
    try:
        job = Job.fetch(job_id, connection=connection)
        status = job.get_status()
        if status == JobStatus.STARTED:
            send_stop_job_command(connection, job_id)
        else:
            job.cancel()
        logger.info(f"Stopped job {job.description}")
        job.delete(delete_dependents=True)
    except NoSuchJobError:
        logger.info(f"Job not found ({job_id})")
        pass
