import aioredis
from redis import Redis

from dripdrop.settings import settings

async_redis = aioredis.from_url(settings.redis_url)
redis = Redis.from_url(settings.redis_url)
