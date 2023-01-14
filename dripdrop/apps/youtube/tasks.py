import asyncio
import dateutil.parser
import traceback
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, delete
from typing import AsyncGenerator

from dripdrop.database import AsyncSession
from dripdrop.logging import logger
from dripdrop.services.google_api import google_api_service
from dripdrop.utils import worker_task

from .models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
)


class YoutubeTasker:
    @worker_task
    async def update_google_access_token(
        self, google_email: str = ..., db: AsyncSession = ...
    ):
        query = select(GoogleAccount).where(GoogleAccount.email == google_email)
        results = await db.scalars(query)
        account: GoogleAccount | None = results.first()
        if account:
            difference = datetime.now(timezone.utc) - account.last_updated
            if difference.seconds >= account.expires:
                try:
                    refresh_access_token = sync_to_async(
                        google_api_service.refresh_access_token
                    )
                    new_access_token = await refresh_access_token(
                        refresh_token=account.refresh_token
                    )
                    if new_access_token:
                        account.access_token = new_access_token["access_token"]
                        account.expires = new_access_token["expires_in"]
                        await db.commit()
                except Exception:
                    account.access_token = ""
                    account.expires = 0
                    await db.commit()

    @worker_task
    async def add_update_youtube_subscription(
        self, google_email: str = ..., subscription: dict = ..., db: AsyncSession = ...
    ):
        subscription_id = subscription["id"]
        subscription_channel_id = subscription["snippet"]["resourceId"]["channelId"]
        subscription_published_at = dateutil.parser.parse(
            subscription["snippet"]["publishedAt"]
        )
        query = select(YoutubeSubscription).where(
            YoutubeSubscription.id == subscription_id,
            YoutubeSubscription.email == google_email,
        )
        results = await db.scalars(query)
        subscription: YoutubeSubscription | None = results.first()
        if subscription:
            subscription.published_at = subscription_published_at
        else:
            db.add(
                YoutubeSubscription(
                    id=subscription_id,
                    channel_id=subscription_channel_id,
                    email=google_email,
                    published_at=subscription_published_at,
                )
            )
        await db.commit()

    @worker_task
    async def add_update_youtube_channel(
        self, channel: dict = ..., db: AsyncSession = ...
    ):
        channel_id = channel["id"]
        channel_title = channel["snippet"]["title"]
        channel_upload_playlist_id = channel["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        channel_thumbnail = channel["snippet"]["thumbnails"]["high"]["url"]
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await db.scalars(query)
        channel: YoutubeChannel | None = results.first()
        if channel:
            channel.title = channel_title
            channel.thumbnail = channel_thumbnail
            channel.upload_playlist_id = channel_upload_playlist_id
        else:
            db.add(
                YoutubeChannel(
                    id=channel_id,
                    title=channel_title,
                    thumbnail=channel_thumbnail,
                    upload_playlist_id=channel_upload_playlist_id,
                    last_updated=datetime.now(timezone.utc) - timedelta(days=32),
                )
            )
        await db.commit()

    @worker_task
    async def add_update_youtube_video(self, video: dict = ..., db: AsyncSession = ...):
        video_id = video["id"]
        video_title = video["snippet"]["title"]
        video_thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_channel_id = video["snippet"]["channelId"]
        video_published_at = dateutil.parser.parse(video["snippet"]["publishedAt"])
        video_category_id = int(video["snippet"]["categoryId"])
        query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
        results = await db.scalars(query)
        video: YoutubeVideo = results.first()
        if video:
            video.title = video_title
            video.thumbnail = video_thumbnail
            video.published_at = video_published_at
            video.category_id = video_category_id
        else:
            db.add(
                YoutubeVideo(
                    id=video_id,
                    title=video_title,
                    thumbnail=video_thumbnail,
                    channel_id=video_channel_id,
                    published_at=video_published_at,
                    category_id=video_category_id,
                )
            )
        await db.commit()

    @worker_task
    async def update_channels(self, channels: list = ...):
        get_channels_info = sync_to_async(google_api_service.get_channels_info)
        channels_info = await get_channels_info(channel_ids=channels)
        await asyncio.gather(
            *list(
                map(
                    lambda channel_info: self.add_update_youtube_channel(
                        channel=channel_info
                    ),
                    channels_info,
                )
            )
        )

    @worker_task
    async def add_update_youtube_video_category(
        self, category: dict = ..., db: AsyncSession = ...
    ):
        category_id = int(category["id"])
        category_title = category["snippet"]["title"]
        logger.exception(traceback.format_exc())
        query = select(YoutubeVideoCategory).where(
            YoutubeVideoCategory.id == category_id
        )
        results = await db.scalars(query)
        category: YoutubeVideoCategory | None = results.first()
        if category:
            category.name = category_title
        else:
            db.add(YoutubeVideoCategory(id=category_id, name=category_title))
        await db.commit()

    @worker_task
    async def update_youtube_video_categories(
        self, cron: bool = ..., db: AsyncSession = ...
    ):
        if not cron:
            query = select(func.count(YoutubeVideoCategory.id))
            count = await db.scalar(query)
            if count > 0:
                return
        get_video_categories = sync_to_async(google_api_service.get_video_categories)
        video_categories = await get_video_categories()
        await asyncio.gather(
            *list(
                map(
                    lambda category: self.add_update_youtube_video_category(
                        category=category
                    ),
                    video_categories,
                )
            )
        )

    @worker_task
    async def update_user_youtube_subscriptions_job(
        self, user_email: str = ..., db: AsyncSession = ...
    ):
        get_channels_info = sync_to_async(google_api_service.get_channels_info)
        query = select(GoogleAccount).where(GoogleAccount.user_email == user_email)
        results = await db.scalars(query)
        account: GoogleAccount | None = results.first()
        if not account:
            return
        account.subscriptions_loading = True
        await db.commit()
        await self.update_google_access_token(google_email=account.email)
        await db.refresh(account)
        if not account.access_token:
            return
        for subscriptions in google_api_service.get_user_subscriptions(
            access_token=account.access_token
        ):
            youtube_subscription_channels = list(
                map(
                    lambda subscription: subscription["snippet"]["resourceId"][
                        "channelId"
                    ],
                    subscriptions,
                )
            )
            channels_info = await get_channels_info(
                channel_ids=youtube_subscription_channels
            )
            await asyncio.gather(
                *list(
                    map(
                        lambda channel: self.add_update_youtube_channel(
                            channel=channel
                        ),
                        channels_info,
                    )
                )
            )
            await asyncio.gather(
                *list(
                    map(
                        lambda subscription: self.add_update_youtube_subscription(
                            google_email=account.email,
                            subscription=subscription,
                        ),
                        subscriptions,
                    )
                )
            )
        account.subscriptions_loading = False
        await db.commit()

    @worker_task
    async def add_new_channel_videos_job(
        self, channel_id: str = ..., db: AsyncSession = ...
    ):
        get_videos_info = sync_to_async(google_api_service.get_videos_info)
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await db.scalars(query)
        channel: YoutubeChannel | None = results.first()
        for uploaded_playlist_videos in google_api_service.get_playlist_videos(
            playlist_id=channel.upload_playlist_id
        ):
            recent_uploaded_playlist_videos = []
            for uploaded_playlist_video in uploaded_playlist_videos:
                video_published_at = dateutil.parser.parse(
                    uploaded_playlist_video["contentDetails"]["videoPublishedAt"]
                )
                uploaded_playlist_video["contentDetails"][
                    "videoPublishedAt"
                ] = video_published_at
                if video_published_at > channel.last_updated:
                    recent_uploaded_playlist_videos.append(uploaded_playlist_video)

            recent_uploaded_playlist_video_ids = list(
                map(
                    lambda recent_uploaded_video: recent_uploaded_video[
                        "contentDetails"
                    ]["videoId"],
                    recent_uploaded_playlist_videos,
                )
            )
            videos_info = await get_videos_info(
                video_ids=recent_uploaded_playlist_video_ids
            )
            await asyncio.gather(
                *list(
                    map(
                        lambda video: self.add_update_youtube_video(video=video),
                        videos_info,
                    )
                )
            )
            if len(recent_uploaded_playlist_videos) < len(uploaded_playlist_videos):
                break
        channel.last_updated = datetime.now(timezone.utc)
        await db.commit()

    @worker_task
    async def update_active_channels(self, db: AsyncSession = ...):
        query = select(YoutubeSubscription).distinct(YoutubeSubscription.channel_id)
        channels = []
        stream: AsyncGenerator[YoutubeSubscription] = await db.stream_scalars(query)
        async for subscription in stream:
            await self.add_new_channel_videos_job(subscription.channel_id)
            channels.append(subscription.channel_id)
            if len(channels) == 50:
                await self.update_channels(channels=channels)
                channels = []
        if len(channels) > 0:
            await self.update_channels(channels=channels)

    @worker_task
    async def update_subscriptions(self, db: AsyncSession = ...):
        query = select(GoogleAccount)
        stream: AsyncGenerator[GoogleAccount] = await db.stream_scalars(query)
        async for account in stream:
            await self.update_user_youtube_subscriptions_job(
                user_email=account.user_email
            )

    @worker_task
    async def channel_cleanup(self, db: AsyncSession = ...):
        limit = datetime.now(timezone.utc) - timedelta(days=7)
        query = select(YoutubeChannel).where(YoutubeChannel.last_updated < limit)
        stream: AsyncGenerator[YoutubeChannel] = await db.stream_scalars(query)
        async for channel in stream:
            query = delete(YoutubeSubscription).where(
                YoutubeSubscription.channel_id == channel.id
            )
            await db.execute(query)
            await db.commit()
            await db.delete(channel)
            await db.commit()


youtube_tasker = YoutubeTasker()
