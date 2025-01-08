import asyncio
import traceback
from asyncio import Task
from enum import Enum
from typing import Coroutine, Literal

import orjson
from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from dripdrop.base.responses import ResponseBaseModel
from dripdrop.logger import logger
from dripdrop.services import redis_client


class PingResponse(ResponseBaseModel):
    status: Literal["PING"]


class RedisChannels(Enum):
    MUSIC_JOB_UPDATE = "MUSIC_JOB_UPDATE"
    YOUTUBE_CHANNEL_UPDATE = "YOUTUBE_CHANNEL_UPDATE"


WEBSOCKET_LISTEN = "websocket:listen"


class WebsocketChannel:
    def __init__(self, channel: RedisChannels):
        self.channel = channel

    @classmethod
    async def start(cls):
        async with redis_client.create_client() as client:
            await client.set(WEBSOCKET_LISTEN, "1")

    @classmethod
    async def close(cls):
        async with redis_client.create_client() as client:
            await client.delete(WEBSOCKET_LISTEN)

    async def publish(self, message: ResponseBaseModel):
        async with redis_client.create_client() as redis:
            await redis.publish(self.channel.value, orjson.dumps(message.model_dump()))

    async def listen(self, websocket: WebSocket, handler: Coroutine):
        task: Task = None
        try:
            await websocket.accept()
            task = asyncio.create_task(self._subscribe(handler=handler))
            async with redis_client.create_client() as client:
                while await client.get(WEBSOCKET_LISTEN):
                    await websocket.send_json(PingResponse(status="PING").model_dump())
                    if task.done():
                        exception = task.exception()
                        if exception:
                            raise exception
                        break
                    await asyncio.sleep(1)
            await websocket.close()
        except WebSocketDisconnect:
            await websocket.close()
        except ConnectionClosedError:
            pass
        except ConnectionClosedOK:
            await websocket.close()
        except Exception:
            logger.exception(traceback.format_exc())
        finally:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def _subscribe(self, handler: Coroutine):
        async with redis_client.create_client() as redis:
            pubsub = redis.pubsub()
            await pubsub.subscribe(self.channel.value)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message.get("type") == "message":
                    await handler(orjson.loads(message.get("data").decode()))
                await asyncio.sleep(1)
