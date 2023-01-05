import aioredis

from dripdrop.settings import settings

redis = aioredis.from_url(settings.redis_url)
