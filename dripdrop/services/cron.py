import asyncio
from croniter import croniter
from datetime import datetime, timezone, timedelta
from rq.job import Dependency
from typing import Callable

from dripdrop.apps.music import tasks as music_tasks
from dripdrop.apps.youtube import tasks as youtube_tasks
from dripdrop.logger import logger
from dripdrop.services import redis_client, rq_client


CRON_JOBS_KEY_PREFIX = "crons:jobs"
EST = timezone(timedelta(hours=-5))


async def run_cron_jobs():
    update_subscriptions_job = await asyncio.to_thread(
        rq_client.default.enqueue, youtube_tasks.update_subscriptions
    )
    await asyncio.to_thread(
        rq_client.default.enqueue,
        youtube_tasks.update_channel_videos,
        depends_on=update_subscriptions_job,
    )
    await asyncio.to_thread(
        rq_client.default.enqueue, music_tasks.delete_old_music_jobs
    )


@rq_client.worker_task
async def remove_cron_key(key: str):
    async with redis_client.create_client() as redis:
        keys_deleted = await redis.delete(key)
        if keys_deleted == 0:
            raise Exception(f"Could not delete cron key {key}")


@rq_client.worker_task
async def create_cron_job(cron_string: str, function: Callable, args=(), kwargs={}):
    cron = croniter(cron_string, datetime.now(tz=EST))
    next_run_time = cron.get_next(ret_type=datetime)
    job = await asyncio.to_thread(
        rq_client.high.enqueue_at, next_run_time, function, args=args, kwargs=kwargs
    )
    cron_key = f"{CRON_JOBS_KEY_PREFIX}:{job.get_id()}"
    async with redis_client.create_client() as redis:
        await redis.set(cron_key, 1)
    logger.info(f"Scheduling {job.description} to run at {next_run_time}")
    await asyncio.to_thread(
        rq_client.high.enqueue,
        create_cron_job,
        args=(cron_string, function),
        kwargs={"args": args, "kwargs": kwargs},
        depends_on=Dependency(jobs=[job], allow_failure=True, enqueue_at_front=True),
    )
    await asyncio.to_thread(
        rq_client.high.enqueue,
        remove_cron_key,
        args=(cron_key,),
        depends_on=Dependency(jobs=[job], allow_failure=True, enqueue_at_front=True),
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
    async with redis_client.create_client() as redis:
        async for key in redis.scan_iter(f"{CRON_JOBS_KEY_PREFIX}*"):
            key = key.decode()
            job_id = key.split(":")[-1]
            rq_client.stop_job(job_id=job_id)
            await redis.delete(key)
