from croniter import croniter
from datetime import datetime, timezone, timedelta
from dripdrop.settings import settings
from dripdrop.logging import logger
from dripdrop.services.redis import redis
from dripdrop.services.rq import queue
from dripdrop.music.tasks import music_tasker
from dripdrop.youtube.tasks import youtube_tasker
from rq.registry import ScheduledJobRegistry
from typing import Callable

scheduled_registry = ScheduledJobRegistry(queue=queue)


class CronService:
    def run_cron_jobs(self):
        video_categories_job = queue.enqueue(
            youtube_tasker.update_youtube_video_categories,
            kwargs={"cron": True},
        )
        active_channels_job = queue.enqueue(
            youtube_tasker.update_active_channels,
            depends_on=video_categories_job,
        )
        update_subscriptions_job = queue.enqueue(
            youtube_tasker.update_subscriptions,
            depends_on=active_channels_job,
        )
        queue.enqueue(
            youtube_tasker.channel_cleanup,
            depends_on=update_subscriptions_job,
        )
        queue.enqueue(music_tasker.cleanup_jobs)

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
        logger.info(f"Scheduling {function} to run at {next_run_time}")
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
        if settings.env == "production":
            crons_added = await redis.get("crons_added")
            if not crons_added:
                await redis.set("crons_added", 1)
                for job_id in scheduled_registry.get_job_ids():
                    logger.info(f"Removing Job: {job_id}")
                    scheduled_registry.remove(job_id, delete_job=True)
                self.create_cron_job(
                    "0 0 * * *",
                    youtube_tasker.update_youtube_video_categories,
                    kwargs={"cron": True},
                )
                self.create_cron_job("0 0 * * *", music_tasker.cleanup_jobs)
                self.create_cron_job("0 1 * * *", youtube_tasker.update_active_channels)
                self.create_cron_job("0 3 * * *", youtube_tasker.update_subscriptions)
                self.create_cron_job("0 5 * * sun", youtube_tasker.channel_cleanup)

    async def end_cron_jobs(self):
        if settings.env == "production":
            await redis.delete("crons_added")


cron_service = CronService()
