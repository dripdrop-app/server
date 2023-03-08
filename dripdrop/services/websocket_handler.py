import asyncio
import traceback
from asyncio import Task
from fastapi import WebSocket, WebSocketDisconnect
from typing import Coroutine, Literal
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from dripdrop.logging import logger
from dripdrop.responses import ResponseBaseModel
from dripdrop.services.redis import redis


class PingResponse(ResponseBaseModel):
    status: Literal["PING"]


class RedisChannels:
    MUSIC_JOB_CHANNEL = "MUSIC_JOB_CHANNEL"
    YOUTUBE_SUBSCRIPTION_JOB_CHANNEL = "YOUTUBE_SUBSCRIPTION_JOB_CHANNEL"


close_sockets = False


def close():
    global close_sockets
    close_sockets = True


async def create_websocket_redis_channel_listener(
    websocket: WebSocket = ..., channel: RedisChannels = ..., handler: Coroutine = ...
):
    global close_sockets
    task: Task = None
    try:
        task = asyncio.create_task(
            _subscribe(
                channel=channel,
                message_handler=handler,
            )
        )
        while True:
            await websocket.send_json(PingResponse(status="PING").dict())
            if task.done():
                expection = task.exception()
                if expection:
                    raise expection
                await websocket.close()
            await asyncio.sleep(5)
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


async def _subscribe(channel: str = ..., message_handler: Coroutine = ...):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    while True:
        message = await pubsub.get_message(
            ignore_subscribe_messages=True,
            timeout=1.0,
        )
        if message and message.get("type") == "message":
            await message_handler(message)
