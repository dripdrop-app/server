import aioredis
from server.config import config
from server.utils.enums import RedisChannels
from typing import Coroutine

redis = aioredis.from_url(config.redis_url)


async def subscribe(channel: RedisChannels, message_handler: Coroutine):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message and message.get('type') == 'message':
            await message_handler(message)
