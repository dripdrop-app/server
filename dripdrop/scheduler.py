import time
from datetime import timedelta, timezone

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from redis.backoff import ExponentialBackoff
from redis.connection import parse_url
from redis.retry import Retry

from dripdrop.logger import logger
from dripdrop.settings import settings
from dripdrop.youtube import tasks as youtube_tasks

EST = timezone(timedelta(hours=-5))

scheduler = BackgroundScheduler(
    jobstores={
        "default": RedisJobStore(
            **parse_url(settings.redis_url),
            retry=Retry(backoff=ExponentialBackoff(cap=10.0, base=1.0), retries=3),
        )
    },
    timezone=EST,
    job_defaults={"misfire_grace_time": None, "coalesce": True},
    logger=logger,
)


if __name__ == "__main__":
    scheduler.start()
    scheduler.add_job(
        youtube_tasks.update_channel_videos_cron,
        trigger=CronTrigger.from_crontab("0 * * * *"),
        id="update_channel_videos",
        replace_existing=True,
    )
    scheduler.add_job(
        youtube_tasks.update_subscriptions_cron,
        trigger=CronTrigger.from_crontab("30 12 * * *"),
        id="update_subscriptions",
        replace_existing=True,
    )
    scheduler.add_job(
        youtube_tasks.update_video_categories_cron,
        trigger=CronTrigger.from_crontab("0 0 * * *"),
        id="update_video_categories",
        replace_existing=True,
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
