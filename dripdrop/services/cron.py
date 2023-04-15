from croniter import croniter
from datetime import datetime, timezone, timedelta
from typing import Callable

from dripdrop.apps.music import tasks as music_tasks
from dripdrop.apps.youtube import tasks as youtube_tasks
from dripdrop.logger import logger
from dripdrop.services import rq_client
from dripdrop.services.redis_client import redis


CRON_JOBS_LIST = "crons:jobs"


async def run_cron_jobs():
    update_subscriptions_job = await rq_client.enqueue(
        function=youtube_tasks.update_subscriptions
    )
    await rq_client.enqueue(
        function=youtube_tasks.update_channel_videos,
        depends_on=update_subscriptions_job,
    )
    await rq_client.enqueue(function=music_tasks.delete_old_music_jobs)


async def create_cron_job(
    cron_string: str = ...,
    function: Callable = ...,
    args: tuple = (),
    kwargs: dict = {},
):
    est = timezone(timedelta(hours=-5))
    cron = croniter(cron_string, datetime.now(est))
    cron.get_next()
    next_run_time = cron.get_current(ret_type=datetime)
    job = rq_client.queue.enqueue_at(
        next_run_time,
        function,
        args=args,
        kwargs=kwargs,
    )
    await redis.rpush(CRON_JOBS_LIST, job.id)
    logger.info(
        f"Scheduling {job.get_call_string()} ({job.args}, {job.kwargs}) to run at {next_run_time}"
    )
    rq_client.queue.enqueue(
        create_cron_job,
        kwargs={
            "cron_string": cron_string,
            "function": function,
            "args": args,
            "kwargs": kwargs,
        },
        depends_on=job,
    )


async def start_cron_jobs():
    await create_cron_job(
        cron_string="0 * * * *",
        function=youtube_tasks.update_channel_videos,
    )
    await create_cron_job(
        cron_string="0 0 * * *", function=music_tasks.delete_old_music_jobs
    )
    await create_cron_job(
        cron_string="30 0 * * *", function=youtube_tasks.update_subscriptions
    )


async def clear_cron_jobs():
    while await redis.llen(CRON_JOBS_LIST) != 0:
        job_id = await redis.rpop(CRON_JOBS_LIST)
        job_id = job_id.decode()
        rq_client.stop_job(job_id=job_id)
