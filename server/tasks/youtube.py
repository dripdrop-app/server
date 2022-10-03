import asyncio
import dateutil.parser
import logging
import server.utils.decorators as decorators
import server.utils.google_api as google_api
import traceback
from asgiref.sync import sync_to_async
from asyncpg.exceptions import UniqueViolationError
from databases import Database
from datetime import datetime, timedelta, timezone
from server.models.main import (
    GoogleAccount,
    YoutubeChannel,
    GoogleAccounts,
    YoutubeSubscription,
    YoutubeSubscriptions,
    YoutubeChannels,
    YoutubeVideoCategories,
    YoutubeVideos,
)
from server.rq import queue
from server.redis import redis, RedisChannels
from sqlalchemy import delete, select, func, update, insert


async def update_google_access_token(google_email: str, db: Database):
    query = select(GoogleAccounts).where(GoogleAccounts.email == google_email)
    google_account = GoogleAccount.parse_obj(await db.fetch_one(query))
    access_token = google_account.access_token
    if (
        datetime.now(timezone.utc) - google_account.last_updated
    ).seconds >= google_account.expires:
        refresh_access_token = sync_to_async(google_api.refresh_access_token)
        new_access_token = await refresh_access_token(google_account.refresh_token)
        if new_access_token:
            query = (
                update(GoogleAccounts)
                .values(
                    access_token=new_access_token["access_token"],
                    expires=new_access_token["expires_in"],
                )
                .where(GoogleAccounts.email == google_email)
            )
            await db.execute(query)
            return new_access_token["access_token"]
        return ""
    return access_token


async def add_youtube_subscription(google_email: str, subscription, db: Database):
    subscription_id = subscription["id"]
    subscription_channel_id = subscription["snippet"]["resourceId"]["channelId"]
    subscription_published_at = dateutil.parser.parse(
        subscription["snippet"]["publishedAt"]
    )
    try:
        query = insert(YoutubeSubscriptions).values(
            id=subscription_id,
            channel_id=subscription_channel_id,
            email=google_email,
            published_at=subscription_published_at,
        )
        await db.execute(query)
    except UniqueViolationError:
        logging.exception(traceback.format_exc())


async def add_youtube_channel(channel, db: Database):
    channel_id = channel["id"]
    channel_title = channel["snippet"]["title"]
    channel_upload_playlist_id = channel["contentDetails"]["relatedPlaylists"][
        "uploads"
    ]
    channel_thumbnail = channel["snippet"]["thumbnails"]["high"]["url"]
    try:
        query = insert(YoutubeChannels).values(
            id=channel_id,
            title=channel_title,
            thumbnail=channel_thumbnail,
            upload_playlist_id=channel_upload_playlist_id,
            last_updated=datetime.now(timezone.utc) - timedelta(days=32),
        )
        await db.execute(query)
        queue.enqueue(
            add_new_channel_videos_job,
            channel_id,
        )
    except UniqueViolationError:
        logging.exception(traceback.format_exc())


async def add_youtube_video(video, db: Database):
    video_id = video["id"]
    video_title = video["snippet"]["title"]
    video_thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
    video_channel_id = video["snippet"]["channelId"]
    video_published_at = dateutil.parser.parse(video["snippet"]["publishedAt"])
    video_category_id = int(video["snippet"]["categoryId"])
    try:
        query = insert(YoutubeVideos).values(
            id=video_id,
            title=video_title,
            thumbnail=video_thumbnail,
            channel_id=video_channel_id,
            published_at=video_published_at,
            category_id=video_category_id,
            created_at=datetime.now(timezone.utc),
        )
        await db.execute(query)
    except UniqueViolationError:
        logging.exception(traceback.format_exc())


@decorators.worker_task
@decorators.exception_handler
async def update_channels(channels: list, db: Database):
    async def update_channel(channel_info: dict):
        try:
            channel_id = channel_info["id"]
            channel_thumbnail = channel_info["snippet"]["thumbnails"]["high"]["url"]
            query = (
                update(YoutubeChannels)
                .values(thumbnail=channel_thumbnail)
                .where(YoutubeChannels.id == channel_id)
            )
            await db.execute(query)
        except Exception:
            logging.exception(traceback.format_exc())

    get_channels_info = sync_to_async(google_api.get_channels_info)
    channels_info = await get_channels_info(channels)
    await asyncio.gather(
        *[update_channel(channel_info) for channel_info in channels_info]
    )


@decorators.worker_task
@decorators.exception_handler
async def update_youtube_video_categories(cron: bool, db: Database = None):
    async def update_youtube_video_category(category):
        category_id = int(category["id"])
        category_title = category["snippet"]["title"]
        try:
            query = insert(YoutubeVideoCategories).values(
                id=category_id,
                name=category_title,
            )
            await db.execute(query)
        except UniqueViolationError:
            query = update(YoutubeVideoCategories).where(
                YoutubeVideoCategories.name == category_title
            )

    if not cron:
        query = select([func.count(YoutubeVideoCategories.id)]).select_from(
            select(YoutubeVideoCategories)
        )
        count = await db.fetch_val(query)
        if count > 0:
            return
    get_video_categories = sync_to_async(google_api.get_video_categories)
    video_categories = await get_video_categories()
    await asyncio.gather(
        *[update_youtube_video_category(category) for category in video_categories]
    )


@decorators.worker_task
@decorators.exception_handler
async def update_user_youtube_subscriptions_job(user_email: str, db: Database = None):
    get_channels_info = sync_to_async(google_api.get_channels_info)
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == user_email)
    google_account = await db.fetch_one(query)
    if not google_account:
        return
    google_account = GoogleAccount.parse_obj(google_account)
    google_email = google_account.email
    query = (
        update(GoogleAccounts)
        .values(subscriptions_loading=True)
        .where(GoogleAccounts.user_email == user_email)
    )
    await db.execute(query)
    await redis.publish(
        RedisChannels.YOUTUBE_SUBSCRIPTION_JOB_CHANNEL.value, user_email
    )
    access_token = await update_google_access_token(google_email, db)
    if not access_token:
        return
    for subscriptions in google_api.get_user_subscriptions(access_token):
        youtube_subscription_channels = [
            subscription["snippet"]["resourceId"]["channelId"]
            for subscription in subscriptions
        ]
        query = select(YoutubeChannels).where(
            YoutubeChannels.id.in_(youtube_subscription_channels)
        )
        existing_channels = await db.fetch_all(query)
        if len(existing_channels) != len(youtube_subscription_channels):
            channels_info = await get_channels_info(youtube_subscription_channels)
            await asyncio.gather(
                *[add_youtube_channel(channel, db) for channel in channels_info]
            )
        await asyncio.gather(
            *[
                add_youtube_subscription(google_email, subscription, db)
                for subscription in subscriptions
            ]
        )
    query = (
        update(GoogleAccounts)
        .values(subscriptions_loading=False)
        .where(GoogleAccounts.user_email == user_email)
    )
    await db.execute(query)
    await redis.publish(
        RedisChannels.YOUTUBE_SUBSCRIPTION_JOB_CHANNEL.value, user_email
    )


@decorators.worker_task
@decorators.exception_handler
async def add_new_channel_videos_job(channel_id: str, db: Database = None):
    get_videos_info = sync_to_async(google_api.get_videos_info)
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    youtube_channel = YoutubeChannel.parse_obj(await db.fetch_one(query))
    last_updated = youtube_channel.last_updated
    channel_upload_playist = youtube_channel.upload_playlist_id
    for uploaded_playlist_videos in google_api.get_playlist_videos(
        channel_upload_playist
    ):
        recent_uploaded_playlist_videos = []
        for uploaded_playlist_video in uploaded_playlist_videos:
            video_published_at = dateutil.parser.parse(
                uploaded_playlist_video["contentDetails"]["videoPublishedAt"]
            )
            uploaded_playlist_video["contentDetails"][
                "videoPublishedAt"
            ] = video_published_at
            if video_published_at > last_updated:
                recent_uploaded_playlist_videos.append(uploaded_playlist_video)

        recent_uploaded_playlist_video_ids = [
            recent_uploaded_video["contentDetails"]["videoId"]
            for recent_uploaded_video in recent_uploaded_playlist_videos
        ]
        query = select(YoutubeVideos).where(
            YoutubeVideos.id.in_(recent_uploaded_playlist_video_ids)
        )
        existing_videos = await db.fetch_all(query)
        if len(existing_videos) < len(recent_uploaded_playlist_videos):
            videos_info = await get_videos_info(recent_uploaded_playlist_video_ids)
            await asyncio.gather(
                *[add_youtube_video(video, db) for video in videos_info]
            )
        if len(recent_uploaded_playlist_videos) < len(uploaded_playlist_videos):
            break
    query = (
        update(YoutubeChannels)
        .values(last_updated=datetime.now(timezone.utc))
        .where(YoutubeChannels.id == channel_id)
    )
    await db.execute(query)


@decorators.worker_task
@decorators.exception_handler
async def update_active_channels(db: Database = None):
    query = select(YoutubeSubscriptions).distinct(YoutubeSubscriptions.channel_id)
    channels = []
    async for row in db.iterate(query):
        subscription = YoutubeSubscription.parse_obj(row)
        queue.enqueue(
            add_new_channel_videos_job,
            subscription.channel_id,
        )
        channels.append(subscription.channel_id)
        if len(channels) == 50:
            queue.enqueue(update_channels, channels)
            channels = []
    if len(channels) > 0:
        queue.enqueue(update_channels, channels)


@decorators.worker_task
@decorators.exception_handler
async def update_subscriptions(db: Database = None):
    query = select(GoogleAccounts)
    async for row in db.iterate(query):
        google_account = GoogleAccount.parse_obj(row)
        queue.enqueue(
            update_user_youtube_subscriptions_job,
            google_account.user_email,
        )


@decorators.worker_task
@decorators.exception_handler
async def delete_channel(channel_id: str, db: Database = None):
    query = delete(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    await db.execute(query)


@decorators.worker_task
@decorators.exception_handler
async def channel_cleanup(db: Database = None):
    limit = datetime.now(timezone.utc) - timedelta(days=7)
    query = select(YoutubeChannels).where(
        YoutubeChannels.last_updated < limit.timestamp()
    )
    async for row in db.iterate(query):
        channel = YoutubeChannel.parse_obj(row)
        queue.enqueue(delete_channel, channel.id)
