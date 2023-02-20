from redis.asyncio import Redis
from dripdrop.settings import settings

redis = Redis.from_url(settings.redis_url)
