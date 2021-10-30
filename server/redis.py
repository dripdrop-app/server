import aioredis
from starlette.config import Config

config = Config('.env')

REDIS_URL = config.get('REDIS_URL')
redis = aioredis.from_url(REDIS_URL)

JOB_CHANNEL = 'music_jobs'


async def subscribe(channel: str, onMessage):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    async for message in pubsub.listen():
        end = await onMessage(message)
        if end:
            break
