import aioredis
from starlette.websockets import WebSocket
from server.db import database, music_jobs
from server.utils.helpers import convert_db_response
from server.config import REDIS_URL
from server.utils.enums import RedisChannels
from server.utils.wrappers import exception_handler

redis = aioredis.from_url(REDIS_URL)


@exception_handler()
async def on_started_music_job(websocket: WebSocket, msg):
    if msg and msg.get('type') == 'message':
        started_job_id = msg.get('data').decode()
        query = music_jobs.select().where(music_jobs.c.user_email ==
                                          websocket.user.display_name, music_jobs.c.id == started_job_id)
        job = await database.fetch_one(query)

        if job:
            await websocket.send_json({
                'type': 'STARTED',
                'jobs': [convert_db_response(job)]
            })


@exception_handler()
async def on_completed_music_job(websocket: WebSocket, msg):
    if msg and msg.get('type') == 'message':
        completed_job_id = msg.get('data').decode()
        query = music_jobs.select().where(music_jobs.c.user_email ==
                                          websocket.user.display_name, music_jobs.c.id == completed_job_id)
        job = await database.fetch_one(query)

        if job:
            await websocket.send_json({
                'type': 'COMPLETED',
                'jobs': [convert_db_response(job)]
            })


async def subscribe(channel: RedisChannels, websocket: WebSocket):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)
    on_message = None

    if channel == RedisChannels.STARTED_MUSIC_JOB_CHANNEL:
        on_message = on_started_music_job
    elif channel == RedisChannels.COMPLETED_MUSIC_JOB_CHANNEL:
        on_message = on_completed_music_job

    async for message in pubsub.listen():
        if on_message:
            await on_message(websocket, message)
