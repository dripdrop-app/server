import aioredis
import asyncio
import traceback
from asyncio import Task
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
from typing import Coroutine
from server.config import config
from server.logging import logger
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

redis = aioredis.from_url(config.redis_url)


class RedisChannels(Enum):
    MUSIC_JOB_CHANNEL = "MUSIC_JOB_CHANNEL"
    YOUTUBE_SUBSCRIPTION_JOB_CHANNEL = "YOUTUBE_SUBSCRIPTION_JOB_CHANNEL"


async def create_websocket_redis_channel_listener(
    websocket: WebSocket, channel: RedisChannels, handler: Coroutine
):
    task: Task = None
    try:
        task = asyncio.create_task(subscribe(channel=channel, message_handler=handler))
        while True:
            await websocket.send_json({})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await websocket.close()
    except ConnectionClosedError:
        pass
    except ConnectionClosedOK:
        await websocket.close()
    except Exception:
        logger.exception(traceback.format_exc())
    finally:
        if task:
            task.cancel()


async def subscribe(channel: RedisChannels, message_handler: Coroutine):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message and message.get("type") == "message":
            await message_handler(message)
