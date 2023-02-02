import asyncio
import traceback
from asyncio import Task
from fastapi import WebSocket, WebSocketDisconnect
from typing import Coroutine
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from dripdrop.logging import logger
from dripdrop.redis import async_redis


class RedisChannels:
    MUSIC_JOB_CHANNEL = "MUSIC_JOB_CHANNEL"
    YOUTUBE_SUBSCRIPTION_JOB_CHANNEL = "YOUTUBE_SUBSCRIPTION_JOB_CHANNEL"


class RedisService:
    async def create_websocket_redis_channel_listener(
        self,
        websocket: WebSocket = ...,
        channel: RedisChannels = ...,
        handler: Coroutine = ...,
    ):
        task: Task = None
        try:
            task = asyncio.create_task(
                self.subscribe(
                    channel=channel,
                    message_handler=handler,
                )
            )
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

    async def subscribe(
        self,
        channel: str = ...,
        message_handler: Coroutine = ...,
    ):
        pubsub = async_redis.pubsub()
        await pubsub.subscribe(channel)
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message and message.get("type") == "message":
                await message_handler(message)


redis_service = RedisService()
