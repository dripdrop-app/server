from croniter import croniter
from datetime import datetime, timezone, timedelta
from typing import Callable

from dripdrop.apps.music import tasks as music_tasks
from dripdrop.apps.youtube import tasks as youtube_tasks
from dripdrop.logging import logger
from dripdrop.services import rq
from dripdrop.services.redis import redis
from dripdrop.settings import settings, ENV


CRONS_ADDED = "crons:added"
CRON_JOBS_LIST = "crons:jobs"


async def run_cron_jobs():
    update_subscriptions_job = await rq.enqueue(
        function=youtube_tasks.update_subscriptions
    )
    await rq.enqueue(
        function=youtube_tasks.update_channel_videos,
        depends_on=update_subscriptions_job,
    )
    await rq.enqueue(function=music_tasks.delete_old_jobs)


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
    logger.info(f"Scheduling {function.__name__} to run at {next_run_time}")
    job = rq.queue.enqueue_at(
        next_run_time,
        function,
        args=args,
        kwargs=kwargs,
    )
    await redis.rpush(CRON_JOBS_LIST, job.id)
    rq.queue.enqueue(
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
    if settings.env == ENV.PRODUCTION:
        crons_added = await redis.get(CRONS_ADDED)
        if not crons_added:
            await redis.set(CRONS_ADDED, 1, ex=timedelta(seconds=10))
            while await redis.llen(CRON_JOBS_LIST) != 0:
                job_id = await redis.rpop(CRON_JOBS_LIST)
                job_id = job_id.decode()
                rq.stop_job(job_id=job_id)
            await create_cron_job("0 * * * *", youtube_tasks.update_channel_videos)
            await create_cron_job("0 0 * * *", music_tasks.delete_old_jobs)
            await create_cron_job("30 0 * * *", youtube_tasks.update_subscriptions)
