import aioredis
from enum import Enum
from typing import Coroutine
from server.config import config

redis = aioredis.from_url(config.redis_url)


class RedisChannels(Enum):
    MUSIC_JOB_CHANNEL = "MUSIC_JOB_CHANNEL"
    YOUTUBE_SUBSCRIPTION_JOB_CHANNEL = "YOUTUBE_SUBSCRIPTION_JOB_CHANNEL"


async def subscribe(channel: RedisChannels, message_handler: Coroutine):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message and message.get("type") == "message":
            await message_handler(message)
