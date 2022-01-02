import asyncio
import uuid
from asyncpg.exceptions import UniqueViolationError
from datetime import datetime, timezone
from server.api.youtube import google_api
from server.database import (
    GoogleAccountDB,
    YoutubeChannelDB,
    db,
    google_accounts,
    youtube_subscriptions,
    youtube_channels,
    youtube_video_categories,
    youtube_jobs,
    youtube_videos
)
from server.queue import q
from server.decorators import exception_handler, worker_task


async def update_google_access_token(google_email: str):
    query = google_accounts.select().where(google_accounts.c.email == google_email)
    google_account = GoogleAccountDB.parse_obj(await db.fetch_one(query))
    access_token = google_account.access_token

    if (datetime.now(timezone.utc) - google_account.last_updated).seconds >= google_account.expires:
        new_access_token = await google_api.refresh_access_token(google_account.refresh_token)
        if new_access_token:
            query = google_accounts.update().values(
                access_token=new_access_token['access_token'],
                expires=new_access_token['expires_in']
            ).where(google_accounts.c.email == google_email)
            await db.execute(query)
            return new_access_token['access_token']
        else:
            query = google_accounts.delete().where(google_accounts.c.email == google_email)
            await db.execute(query)
            return None
    return access_token


@worker_task
@exception_handler
async def update_youtube_video_categories():
    async def update_youtube_video_category(category):
        category_id = category['id']
        category_title = category['snippet']['title']
        try:
            query = youtube_video_categories.insert().values(
                id=category_id, name=category_title)
            await db.execute(query)
        except UniqueViolationError:
            query = youtube_video_categories.update().where(
                youtube_video_categories.c.name == category_title)

    video_categories = await google_api.get_video_categories()
    await asyncio.gather(*[update_youtube_video_category(category) for category in video_categories])


async def add_youtube_subscription(google_email: str, subscription):
    subscription_id = subscription['id']
    subscription_channel_id = subscription['snippet']['resourceId']['channelId']
    try:
        query = youtube_subscriptions.insert().values(
            id=subscription_id,
            channel_id=subscription_channel_id,
            email=google_email
        )
        await db.execute(query)
    except UniqueViolationError:
        pass


async def add_youtube_channel(channel):
    channel_id = channel['id']
    channel_title = channel['snippet']['title']
    channel_upload_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
    channel_thumbnail = channel['snippet']['thumbnails']['default']['url']
    try:
        query = youtube_channels.insert().values(
            id=channel_id,
            title=channel_title,
            thumbnail=channel_thumbnail,
            upload_playlist_id=channel_upload_playlist_id
        )
        await db.execute(query)
        q.enqueue(
            'server.api.youtube.tasks.add_new_channel_videos_job', channel_id, 30)
    except UniqueViolationError:
        pass


async def add_youtube_video(video):
    video_id = video['id']
    video_title = video['snippet']['title']
    video_thumbnail = video['snippet']['thumbnails']['default']['url']
    video_channel_id = video['snippet']['channelId']
    video_published_at = datetime.strptime(
        video['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%S%z')
    video_category_id = video['snippet']['categoryId']
    try:
        query = youtube_videos.insert().values(
            id=video_id,
            title=video_title,
            thumbnail=video_thumbnail,
            channel_id=video_channel_id,
            published_at=video_published_at,
            category_id=video_category_id
        )
        await db.execute(query)
    except UniqueViolationError:
        pass


@worker_task
@exception_handler
async def update_user_youtube_subscriptions_job(user_email: str):
    query = google_accounts.select().where(
        google_accounts.c.user_email == user_email)
    google_account = GoogleAccountDB.parse_obj(await db.fetch_one(query))
    if not google_account:
        return

    youtube_job_id = str(uuid.uuid4())
    google_email = google_account.get('email')
    query = youtube_jobs.select().where(youtube_jobs.c.email == google_email)
    job = await db.fetch_one(query)
    if job:
        return

    query = youtube_jobs.insert().values(job_id=youtube_job_id,
                                         email=google_email, completed=False, failed=False)
    await db.execute(query)
    access_token = await update_google_access_token(google_email)
    if not access_token:
        return

    current_subscriptions = []
    for subscriptions in google_api.get_user_subscriptions(access_token):
        youtube_subscription_channels = [
            subscription['snippet']['resourceId']['channelId'] for subscription in subscriptions]
        query = youtube_channels.select().where(
            youtube_channels.c.id.in_(youtube_subscription_channels))
        existing_channels = await db.fetch_all(query)

        if len(existing_channels) != len(youtube_subscription_channels):
            channels_info = await google_api.get_channels_info(youtube_subscription_channels)
            await asyncio.gather(*[add_youtube_channel(channel) for channel in channels_info])

        await asyncio.gather(*[add_youtube_subscription(google_email, subscription) for subscription in subscriptions])
        current_subscriptions.extend(
            [subscription['id'] for subscription in subscriptions])

    query = youtube_subscriptions.delete().where(
        youtube_subscriptions.c.id.notin_(current_subscriptions))
    await db.execute(query)
    query = youtube_jobs.delete().where(youtube_jobs.c.email == google_email)
    await db.execute(query)


@worker_task
@exception_handler
async def add_new_channel_videos_job(channel_id: str, days_limit: int):
    query = youtube_channels.select().where(youtube_channels.c.id == channel_id)
    youtube_channel = YoutubeChannelDB.parse_obj(await db.fetch_one(query))
    channel_upload_playist = youtube_channel.upload_playlist_id
    for uploaded_playlist_videos in google_api.get_playlist_videos(channel_upload_playist):
        recent_uploaded_playlist_videos = []
        for uploaded_playlist_video in uploaded_playlist_videos:
            video_published_at = datetime.strptime(
                uploaded_playlist_video['contentDetails']['videoPublishedAt'], '%Y-%m-%dT%H:%M:%S%z')
            uploaded_playlist_video['contentDetails']['videoPublishedAt'] = video_published_at
            if (datetime.now(timezone.utc) - video_published_at).days < days_limit:
                recent_uploaded_playlist_videos.append(uploaded_playlist_video)

        recent_uploaded_playlist_video_ids = [recent_uploaded_video['contentDetails']
                                              ['videoId'] for recent_uploaded_video in recent_uploaded_playlist_videos]
        query = youtube_videos.select().where(
            youtube_videos.c.id.in_(recent_uploaded_playlist_video_ids))
        existing_videos = await db.fetch_all(query)

        if len(existing_videos) < len(recent_uploaded_playlist_videos):
            videos_info = await google_api.get_videos_info(recent_uploaded_playlist_video_ids)
            await asyncio.gather(*[add_youtube_video(video) for video in videos_info])

        if len(recent_uploaded_playlist_videos) < len(uploaded_playlist_videos):
            break
