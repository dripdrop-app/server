from redis import Redis
from rq import Queue
from rq.command import send_stop_job_command
from rq.exceptions import NoSuchJobError
from rq.job import Job, JobStatus

from dripdrop.settings import settings, ENV
from dripdrop.logger import logger

connection = Redis.from_url(settings.redis_url)


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


class CustomJob(Job):
    @classmethod
    def create(
        cls,
        *args,
        on_success=None,
        on_failure=None,
        **kwargs,
    ):
        return super().create(
            *args,
            **kwargs,
            on_success=report_job_time,
            on_failure=report_job_time,
        )


queue = Queue(
    connection=connection, default_timeout=settings.timeout, job_class=CustomJob
)
high_queue = Queue(
    name="high",
    connection=connection,
    is_async=settings.env != ENV.TESTING,
    job_class=CustomJob,
)


def stop_job(job_id: str):
    try:
        job = Job.fetch(job_id, connection=connection)
        status = job.get_status()
        if status == JobStatus.SCHEDULED:
            job.cancel()
        elif status == JobStatus.STARTED:
            send_stop_job_command(connection, job_id)
        logger.info(f"Stopped job {job.get_call_string()} ({job.args}, {job.kwargs})")
        job.delete(delete_dependents=True)
    except NoSuchJobError:
        logger.info(f"Job not found ({job_id})")
        pass
