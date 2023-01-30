import dateutil.parser
import traceback
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta
from sqlalchemy import select, func, delete
from typing import AsyncGenerator

from dripdrop.database import AsyncSession
from dripdrop.logging import logger
from dripdrop.services.google_api import google_api_service
from dripdrop.settings import settings
from dripdrop.rq import queue
from dripdrop.utils import worker_task, exception_handler

from .models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
)
from .utils import update_google_access_token


class YoutubeTasker:
    def enqueue(self, *args, **kwargs):
        queue.enqueue(*args, **kwargs, at_front=True)

    @exception_handler
    async def add_update_youtube_subscription(
        self,
        google_email: str = ...,
        subscription: dict = ...,
        session: AsyncSession = ...,
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
        results = await session.scalars(query)
        subscription: YoutubeSubscription | None = results.first()
        if subscription:
            subscription.published_at = subscription_published_at
        else:
            session.add(
                YoutubeSubscription(
                    id=subscription_id,
                    channel_id=subscription_channel_id,
                    email=google_email,
                    published_at=subscription_published_at,
                )
            )
        await session.commit()

    @exception_handler
    async def add_update_youtube_channel(
        self, channel: dict = ..., session: AsyncSession = ...
    ):
        channel_id = channel["id"]
        channel_title = channel["snippet"]["title"]
        channel_upload_playlist_id = channel["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        channel_thumbnail = channel["snippet"]["thumbnails"]["high"]["url"]
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await session.scalars(query)
        channel: YoutubeChannel | None = results.first()
        if channel:
            channel.title = channel_title
            channel.thumbnail = channel_thumbnail
            channel.upload_playlist_id = channel_upload_playlist_id
        else:
            session.add(
                YoutubeChannel(
                    id=channel_id,
                    title=channel_title,
                    thumbnail=channel_thumbnail,
                    upload_playlist_id=channel_upload_playlist_id,
                    last_videos_updated=datetime.now(tz=settings.timezone)
                    - timedelta(days=32),
                )
            )
        await session.commit()

    @exception_handler
    async def add_update_youtube_video(
        self, video: dict = ..., session: AsyncSession = ...
    ):
        video_id = video["id"]
        video_title = video["snippet"]["title"]
        video_thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_channel_id = video["snippet"]["channelId"]
        video_published_at = dateutil.parser.parse(video["snippet"]["publishedAt"])
        video_category_id = int(video["snippet"]["categoryId"])
        query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
        results = await session.scalars(query)
        video: YoutubeVideo = results.first()
        if video:
            video.title = video_title
            video.thumbnail = video_thumbnail
            video.published_at = video_published_at
            video.category_id = video_category_id
        else:
            session.add(
                YoutubeVideo(
                    id=video_id,
                    title=video_title,
                    thumbnail=video_thumbnail,
                    channel_id=video_channel_id,
                    published_at=video_published_at,
                    category_id=video_category_id,
                )
            )
        await session.commit()

    @worker_task
    async def update_channels(
        self, channel_ids: list[int] = ..., session: AsyncSession = ...
    ):
        get_channels_info = sync_to_async(google_api_service.get_channels_info)
        channels_info = await get_channels_info(channel_ids=channel_ids)
        for channel_info in channels_info:
            await self.add_update_youtube_channel(channel=channel_info, session=session)

    @exception_handler
    async def add_update_youtube_video_category(
        self, category: dict = ..., session: AsyncSession = ...
    ):
        category_id = int(category["id"])
        category_title = category["snippet"]["title"]
        logger.exception(traceback.format_exc())
        query = select(YoutubeVideoCategory).where(
            YoutubeVideoCategory.id == category_id
        )
        results = await session.scalars(query)
        category: YoutubeVideoCategory | None = results.first()
        if category:
            category.name = category_title
        else:
            session.add(YoutubeVideoCategory(id=category_id, name=category_title))
        await session.commit()

    @worker_task
    async def update_youtube_video_categories(
        self, cron: bool = ..., session: AsyncSession = ...
    ):
        if not cron:
            query = select(func.count(YoutubeVideoCategory.id))
            count = await session.scalar(query)
            if count > 0:
                return
        get_video_categories = sync_to_async(google_api_service.get_video_categories)
        video_categories = await get_video_categories()
        for category in video_categories:
            await self.add_update_youtube_video_category(
                category=category, session=session
            )

    @worker_task
    async def update_user_youtube_subscriptions_job(
        self, user_email: str = ..., session: AsyncSession = ...
    ):
        get_channels_info = sync_to_async(google_api_service.get_channels_info)
        query = select(GoogleAccount).where(GoogleAccount.user_email == user_email)
        results = await session.scalars(query)
        account: GoogleAccount | None = results.first()
        if not account:
            return
        await session.commit()
        await update_google_access_token(google_email=account.email, session=session)
        await session.refresh(account)
        if not account.access_token:
            return

        for subscriptions in google_api_service.get_user_subscriptions(
            access_token=account.access_token
        ):
            subscription_channel_ids = [
                subscription["snippet"]["resourceId"]["channelId"]
                for subscription in subscriptions
            ]
            query = select(YoutubeChannel).where(
                YoutubeChannel.id.in_(subscription_channel_ids)
            )
            results = await session.scalars(query)
            channels: list[YoutubeChannel] = results.all()
            channel_ids = [channel.id for channel in channels]
            new_channel_ids = list(
                filter(
                    lambda channel_id: channel_id not in channel_ids,
                    subscription_channel_ids,
                )
            )
            if len(new_channel_ids) > 0:
                channels_info = await get_channels_info(channel_ids=new_channel_ids)
                for channel_info in channels_info:
                    self.add_update_youtube_channel(
                        channel=channel_info, session=session
                    )
            for subscription in subscriptions:
                await self.add_update_youtube_subscription(
                    google_email=account.email,
                    subscription=subscription,
                    session=session,
                )

    @worker_task
    async def add_new_channel_videos_job(
        self, channel_id: str = ..., session: AsyncSession = ...
    ):
        get_videos_info = sync_to_async(google_api_service.get_videos_info)
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await session.scalars(query)
        channel: YoutubeChannel | None = results.first()
        for uploaded_playlist_videos in google_api_service.get_playlist_videos(
            playlist_id=channel.upload_playlist_id
        ):
            new_videos = []
            video_ids = []
            for uploaded_video in uploaded_playlist_videos:
                video_published_at = dateutil.parser.parse(
                    uploaded_video["contentDetails"]["videoPublishedAt"]
                )
                uploaded_video["contentDetails"][
                    "videoPublishedAt"
                ] = video_published_at
                video_ids.append(uploaded_video["contentDetails"]["videoId"])
                if video_published_at > channel.last_videos_updated:
                    new_videos.append(uploaded_video)
            videos_info = await get_videos_info(video_ids=video_ids)
            for video_info in videos_info:
                await self.add_update_youtube_video(video=video_info, session=session)
            if len(new_videos) < len(uploaded_playlist_videos):
                break
        channel.last_videos_updated = datetime.now(tz=settings.timezone)
        await session.commit()

    @worker_task
    async def update_subscribed_channels_videos(self, session: AsyncSession = ...):
        query = select(YoutubeSubscription).distinct(YoutubeSubscription.channel_id)
        stream: AsyncGenerator[YoutubeSubscription] = await session.stream_scalars(
            query
        )
        async for subscription in stream:
            self.enqueue(
                self.add_new_channel_videos_job,
                kwargs={"channel_id": subscription.channel_id},
            )

    @worker_task
    async def update_subscribed_channels_meta(self, session: AsyncSession = ...):
        CHANNEL_NUM = 50
        page = 0
        while True:
            query = (
                select(YoutubeSubscription)
                .distinct(YoutubeSubscription.channel_id)
                .offset(page * CHANNEL_NUM)
            )
            results = await session.scalars(query)
            subscriptions: list[YoutubeSubscription] = results.fetchmany(CHANNEL_NUM)
            if len(subscriptions) == 0:
                break
            channel_ids = [subscription.channel_id for subscription in subscriptions]
            self.enqueue(self.update_channels, kwargs={"channel_ids": channel_ids})
            page += 1

    @worker_task
    async def update_subscriptions(self, session: AsyncSession = ...):
        query = select(GoogleAccount)
        stream: AsyncGenerator[GoogleAccount] = await session.stream_scalars(query)
        async for account in stream:
            self.enqueue(
                self.update_user_youtube_subscriptions_job,
                kwargs={"user_email": account.user_email},
            )

    @worker_task
    async def delete_channel(self, channel_id: str = ..., session: AsyncSession = ...):
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await session.scalars(query)
        channel: YoutubeChannel | None = results.first()
        if not channel:
            raise Exception(f"Channel ({channel_id}) not found")
        query = delete(YoutubeSubscription).where(
            YoutubeSubscription.channel_id == channel.id
        )
        await session.execute(query)
        await session.commit()
        await session.delete(channel)
        await session.commit()

    @worker_task
    async def delete_old_channels(self, session: AsyncSession = ...):
        limit = datetime.now(tz=settings.timezone) - timedelta(days=7)
        query = select(YoutubeChannel).where(YoutubeChannel.last_videos_updated < limit)
        stream: AsyncGenerator[YoutubeChannel] = await session.stream_scalars(query)
        async for channel in stream:
            self.enqueue(self.delete_channel, kwargs={"channel_id": channel.id})


youtube_tasker = YoutubeTasker()
