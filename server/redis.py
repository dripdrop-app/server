import aioredis
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from server.config import config
from server.database import GoogleAccount, MusicJob, db, music_jobs, google_accounts
from server.models import SessionUser
from server.utils.enums import RedisChannels

redis = aioredis.from_url(config.redis_url)


def on_youtube_subscription_job(user: SessionUser):
    async def handler(websocket: WebSocket, msg):
        if msg and msg.get('type') == 'message':
            user_email = msg.get('data').decode()
            if user.email == user_email:
                query = google_accounts.select().where(
                    google_accounts.c.user_email == user_email)
                google_account = await db.fetch_one(query)
                if google_account:
                    google_account = GoogleAccount.parse_obj(google_account)
                    await websocket.send_json({
                        'type': 'SUBSCRIPTIONS_UPDATE',
                        'finished': not google_account.subscriptions_loading
                    })
    return handler


def on_music_job(user: SessionUser, type: str):
    async def handler(websocket: WebSocket, msg):
        if msg and msg.get('type') == 'message':
            started_job_id = msg.get('data').decode()
            query = music_jobs.select().where(music_jobs.c.user_email ==
                                              user.email, music_jobs.c.id == started_job_id)
            job = await db.fetch_one(query)
            if job:
                job = MusicJob.parse_obj(job)
                await websocket.send_json({
                    'type': type,
                    'jobs': [jsonable_encoder(job)]
                })
    return handler


async def subscribe(channel: RedisChannels, websocket: WebSocket, user: SessionUser):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel.value)
    on_message = None

    if channel == RedisChannels.STARTED_MUSIC_JOB_CHANNEL:
        on_message = on_music_job(user, 'STARTED')
    elif channel == RedisChannels.COMPLETED_MUSIC_JOB_CHANNEL:
        on_message = on_music_job(user, 'COMPLETED')
    elif channel == RedisChannels.COMPLETED_YOUTUBE_SUBSCRIPTION_JOB_CHANNEL:
        on_message = on_youtube_subscription_job(user)

    async for message in pubsub.listen():
        if on_message:
            await on_message(websocket, message)
