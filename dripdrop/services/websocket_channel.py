import asyncio
import orjson
import traceback
from asyncio import Task
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
from typing import Coroutine, Literal
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from dripdrop.logger import logger
from dripdrop.responses import ResponseBaseModel
from dripdrop.services.redis_client import redis


class PingResponse(ResponseBaseModel):
    status: Literal["PING"]


class RedisChannels(Enum):
    MUSIC_JOB_UPDATE = "MUSIC_JOB_UPDATE"
    YOUTUBE_CHANNEL_UPDATE = "YOUTUBE_CHANNEL_UPDATE"


class WebsocketChannel:
    close_sockets = False

    def __init__(self, channel: RedisChannels = ...):
        self.channel = channel

    @classmethod
    def close(cls):
        WebsocketChannel.close_sockets = True

    async def publish(self, message: ResponseBaseModel = ...):
        await redis.publish(self.channel.value, orjson.dumps(message.dict()))

    async def listen(self, websocket: WebSocket = ..., handler: Coroutine = ...):
        task: Task = None
        try:
            await websocket.accept()
            task = asyncio.create_task(self._subscribe(handler=handler))
            while not WebsocketChannel.close_sockets:
                await websocket.send_json(PingResponse(status="PING").dict())
                if task.done():
                    exception = task.exception()
                    if exception:
                        raise exception
                    break
                await asyncio.sleep(5)
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

    async def _subscribe(self, handler: Coroutine = ...):
        pubsub = redis.pubsub()
        await pubsub.subscribe(self.channel.value)
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message and message.get("type") == "message":
                await handler(orjson.loads(message.get("data").decode()))
