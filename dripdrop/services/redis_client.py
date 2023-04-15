import redis.asyncio as Redis
from dripdrop.settings import settings

redis = Redis.from_url(settings.redis_url)
