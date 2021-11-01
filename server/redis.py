import aioredis
from enum import Enum
from starlette.config import Config
from starlette.websockets import WebSocket
from server.db import database, music_jobs
from server.utils.helpers import convertDBJob

config = Config('.env')

REDIS_URL = config.get('REDIS_URL')
redis = aioredis.from_url(REDIS_URL)


class RedisChannels(Enum):
    COMPLETED_JOB_CHANNEL = 'completed_jobs'
    STARTED_JOB_CHANNEL = 'started_jobs'


async def onCompleteMessage(websocket: WebSocket, msg):
    if msg and msg.get('type') == 'message':
        completedJobID = msg.get('data').decode()
        query = music_jobs.select().where(music_jobs.c.jobID == completedJobID)
        job = await database.fetch_one(query)
        if job:
            await websocket.send_json({
                'type': 'COMPLETED',
                'jobs': [convertDBJob(job)]
            })


async def onStartedMessage(websocket: WebSocket, msg):
    if msg and msg.get('type') == 'message':
        startedJobID = msg.get('data').decode()
        query = music_jobs.select().where(music_jobs.c.jobID == startedJobID)
        job = await database.fetch_one(query)
        if job:
            await websocket.send_json({
                'type': 'STARTED',
                'jobs': [convertDBJob(job)]
            })


async def subscribe(channel: RedisChannels, websocket: WebSocket):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)

    if channel == RedisChannels.STARTED_JOB_CHANNEL:
        onMessage = onStartedMessage
    elif channel == RedisChannels.COMPLETED_JOB_CHANNEL:
        onMessage = onCompleteMessage

    async for message in pubsub.listen():
        await onMessage(websocket, message)
