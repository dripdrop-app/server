import aioredis
from starlette.websockets import WebSocket
from server.db import database, music_jobs
from server.utils.helpers import convert_db_response
from server.config import REDIS_URL
from server.utils.enums import RedisChannels

redis = aioredis.from_url(REDIS_URL)


async def on_complete_message(websocket: WebSocket, msg):
    if msg and msg.get('type') == 'message':
        completed_job_id = msg.get('data').decode()
        query = music_jobs.select().where(music_jobs.c.username ==
                                          websocket.user.display_name, music_jobs.c.job_id == completed_job_id)
        job = await database.fetch_one(query)
        if job:
            await websocket.send_json({
                'type': 'COMPLETED',
                'jobs': [convert_db_response(job)]
            })


async def on_started_message(websocket: WebSocket, msg):
    if msg and msg.get('type') == 'message':
        started_job_id = msg.get('data').decode()
        query = music_jobs.select().where(music_jobs.c.username ==
                                          websocket.user.display_name, music_jobs.c.job_id == started_job_id)
        job = await database.fetch_one(query)
        if job:
            await websocket.send_json({
                'type': 'STARTED',
                'jobs': [convert_db_response(job)]
            })


async def subscribe(channel: RedisChannels, websocket: WebSocket):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)

    if channel == RedisChannels.STARTED_JOB_CHANNEL:
        on_message = on_started_message
    elif channel == RedisChannels.COMPLETED_JOB_CHANNEL:
        on_message = on_complete_message

    async for message in pubsub.listen():
        await on_message(websocket, message)
