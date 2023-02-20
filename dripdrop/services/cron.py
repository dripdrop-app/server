from croniter import croniter
from datetime import datetime, timezone, timedelta
from rq.registry import ScheduledJobRegistry
from typing import Callable

from dripdrop.apps.music.tasks import music_tasker
from dripdrop.apps.youtube.tasks import youtube_tasker
from dripdrop.logging import logger
from dripdrop.redis import redis
from dripdrop.rq import queue, enqueue
from dripdrop.settings import settings, ENV

scheduled_registry = ScheduledJobRegistry(queue=queue)


class Cron:
    def __init__(self):
        self.CRONS_ADDED = "crons_added"

    async def run_cron_jobs(self):
        video_categories_job = await enqueue(
            function=youtube_tasker.update_video_categories,
            kwargs={"cron": True},
        )
        update_subscriptions_job = await enqueue(
            function=youtube_tasker.update_subscriptions,
            depends_on=video_categories_job,
        )
        subscribed_channels_videos_job = await enqueue(
            function=youtube_tasker.update_channel_videos,
            depends_on=update_subscriptions_job,
        )
        await enqueue(
            function=youtube_tasker.delete_old_channels,
            depends_on=subscribed_channels_videos_job,
        )
        await enqueue(function=music_tasker.delete_old_jobs)

    def create_cron_job(
        self,
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
        job = queue.enqueue_at(
            next_run_time,
            function,
            args=args,
            kwargs=kwargs,
        )
        queue.enqueue(
            self.create_cron_job,
            kwargs={
                "cron_string": cron_string,
                "function": function,
                "args": args,
                "kwargs": kwargs,
            },
            depends_on=job,
        )

    async def start_cron_jobs(self):
        if settings.env == ENV.PRODUCTION:
            crons_added = await redis.get(self.CRONS_ADDED)
            if not crons_added:
                await redis.set(self.CRONS_ADDED, 1)
                for job_id in scheduled_registry.get_job_ids():
                    logger.info(f"Removing Job: {job_id}")
                    scheduled_registry.remove(job_id, delete_job=True)
                self.create_cron_job(
                    "0 0 * * *",
                    youtube_tasker.update_video_categories,
                    kwargs={"cron": True},
                )
                self.create_cron_job("0 * * * *", youtube_tasker.update_channel_videos)
                self.create_cron_job("0 0 * * *", music_tasker.delete_old_jobs)
                self.create_cron_job("0 0 * * *", youtube_tasker.update_subscriptions)
                self.create_cron_job("0 5 * * sun", youtube_tasker.delete_old_channels)

    async def end_cron_jobs(self):
        if settings.env == ENV.PRODUCTION:
            await redis.delete(self.CRONS_ADDED)


cron = Cron()
