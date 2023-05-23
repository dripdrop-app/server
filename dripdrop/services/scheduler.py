from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta, timezone
from redis.connection import parse_url

from dripdrop.settings import settings

EST = timezone(timedelta(hours=-5))

scheduler = AsyncIOScheduler(
    jobstores={"default": RedisJobStore(**parse_url(settings.redis_url))},
    timezone=EST,
    job_defaults={"misfire_grace_time": None, "coalesce": True},
)
