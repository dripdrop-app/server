import dateutil.parser
import traceback
from datetime import datetime, timedelta
from sqlalchemy import select, func

from dripdrop.database import AsyncSession
from dripdrop.logging import logger
from dripdrop.services.google_api import google_api_service
from dripdrop.settings import settings
from dripdrop.rq import enqueue
from dripdrop.utils import worker_task

from .models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
    create_temp_subscriptions_table,
)
from .utils import update_google_access_token


class YoutubeTasker:
    async def _add_update_subscription(
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
        subscription = results.first()
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
        return bool(subscription)

    async def _add_update_channel(
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
        channel = results.first()
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
        return bool(channel)

    async def _add_update_video(self, video: dict = ..., session: AsyncSession = ...):
        video_id = video["id"]
        video_title = video["snippet"]["title"]
        video_thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_channel_id = video["snippet"]["channelId"]
        video_published_at = dateutil.parser.parse(video["snippet"]["publishedAt"])
        video_category_id = int(video["snippet"]["categoryId"])
        query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
        results = await session.scalars(query)
        video = results.first()
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
        return bool(video)

    @worker_task
    async def _update_channels(
        self, channel_ids: list[int] = ..., session: AsyncSession = ...
    ):
        channels_info = google_api_service.get_channels_info(channel_ids=channel_ids)
        for channel_info in channels_info:
            try:
                await self._add_update_channel(channel=channel_info, session=session)
            except Exception:
                logger.exception(traceback.format_exc())

    async def _add_update_video_category(
        self, category: dict = ..., session: AsyncSession = ...
    ):
        category_id = int(category["id"])
        category_title = category["snippet"]["title"]
        query = select(YoutubeVideoCategory).where(
            YoutubeVideoCategory.id == category_id
        )
        results = await session.scalars(query)
        category = results.first()
        if category:
            category.name = category_title
        else:
            session.add(YoutubeVideoCategory(id=category_id, name=category_title))
        await session.commit()
        return bool(category)

    @worker_task
    async def update_video_categories(
        self, cron: bool = ..., session: AsyncSession = ...
    ):
        if not cron:
            query = select(func.count(YoutubeVideoCategory.id))
            count = await session.scalar(query)
            if count > 0:
                return
        video_categories = google_api_service.get_video_categories()
        for category in video_categories:
            try:
                await self._add_update_video_category(
                    category=category, session=session
                )
            except Exception:
                logger.exception(traceback.format_exc())

    @worker_task
    async def _delete_subscription(
        self, subscription_id: str = ..., email: str = ..., session: AsyncSession = ...
    ):
        query = select(YoutubeSubscription).where(
            YoutubeSubscription.id == subscription_id,
            YoutubeSubscription.email == email,
        )
        results = await session.scalars(query)
        subscription = results.first()
        if not subscription:
            raise Exception(f"Subscription ({subscription_id}) not found")
        await session.delete(subscription)
        await session.commit()

    @worker_task
    async def update_user_subscriptions(
        self, user_email: str = ..., session: AsyncSession = ...
    ):
        query = select(GoogleAccount).where(GoogleAccount.user_email == user_email)
        results = await session.scalars(query)
        account = results.first()
        if not account:
            return
        await session.commit()
        await update_google_access_token(google_email=account.email, session=session)
        await session.refresh(account)
        if not account.access_token:
            return

        async with create_temp_subscriptions_table(
            email=account.email
        ) as TempSubscription:
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
                channels = results.all()
                channel_ids = [channel.id for channel in channels]
                new_channel_ids = list(
                    filter(
                        lambda channel_id: channel_id not in channel_ids,
                        subscription_channel_ids,
                    )
                )
                if len(new_channel_ids) > 0:
                    channels_info = google_api_service.get_channels_info(
                        channel_ids=new_channel_ids
                    )
                    for channel_info in channels_info:
                        await self._add_update_channel(
                            channel=channel_info, session=session
                        )
                for subscription in subscriptions:
                    try:
                        await self._add_update_subscription(
                            google_email=account.email,
                            subscription=subscription,
                            session=session,
                        )
                        session.add(TempSubscription(id=subscription["id"]))
                        await session.commit()
                    except Exception:
                        logger.exception(traceback.format_exc())
            subscription_query = (
                select(YoutubeSubscription)
                .where(YoutubeSubscription.email == account.email)
                .subquery()
            )
            temp_subscription_query = select(TempSubscription).subquery()
            query = subscription_query.join(
                temp_subscription_query,
                subscription_query.columns.id == temp_subscription_query.columns.id,
                isouter=True,
            )
            stream = await session.stream(
                select(subscription_query.columns.id.label("subscription_id"))
                .select_from(query)
                .where(temp_subscription_query.columns.id.is_(None))
            )
            async for row in stream:
                row = row._mapping
                await enqueue(
                    function=self._delete_subscription,
                    kwargs={
                        "subscription_id": row.subscription_id,
                        "email": account.email,
                    },
                    at_front=True,
                )

    @worker_task
    async def _add_new_channel_videos_job(
        self, channel_id: str = ..., session: AsyncSession = ...
    ):
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await session.scalars(query)
        channel = results.first()
        for uploaded_playlist_videos in google_api_service.get_playlist_videos(
            playlist_id=channel.upload_playlist_id
        ):
            new_videos = []
            video_ids = []
            videos_info = google_api_service.get_videos_info(video_ids=video_ids)
            for video_info in videos_info:
                try:
                    new_video = await self._add_update_video(
                        video=video_info, session=session
                    )
                    if new_video:
                        new_videos.append(video_info["id"])
                except Exception:
                    logger.exception(traceback.format_exc())
            if len(new_videos) < len(uploaded_playlist_videos):
                break
        channel.last_videos_updated = datetime.now(tz=settings.timezone)
        await session.commit()

    @worker_task
    async def update_channels_videos(self, session: AsyncSession = ...):
        query = select(YoutubeChannel)
        stream = await session.stream_scalars(query)
        async for channel in stream:
            await enqueue(
                function=self._add_new_channel_videos_job,
                kwargs={"channel_id": channel.id},
                at_front=True,
            )

    @worker_task
    async def update_channels_meta(self, session: AsyncSession = ...):
        CHANNEL_NUM = 50
        page = 0
        while True:
            query = select(YoutubeChannel).offset(page * CHANNEL_NUM)
            results = await session.scalars(query)
            channels = results.fetchmany(CHANNEL_NUM)
            if len(channels) == 0:
                break
            channel_ids = [channel.id for channel in channels]
            await enqueue(
                function=self._update_channels,
                kwargs={"channel_ids": channel_ids},
                at_front=True,
            )
            page += 1

    @worker_task
    async def update_subscriptions(self, session: AsyncSession = ...):
        query = select(GoogleAccount)
        stream = await session.stream_scalars(query)
        async for account in stream:
            await enqueue(
                function=self.update_user_subscriptions,
                kwargs={"user_email": account.user_email},
                at_front=True,
            )

    @worker_task
    async def _delete_channel(self, channel_id: str = ..., session: AsyncSession = ...):
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await session.scalars(query)
        channel = results.first()
        if not channel:
            raise Exception(f"Channel ({channel_id}) not found")
        await session.delete(channel)
        await session.commit()

    @worker_task
    async def delete_old_channels(self, session: AsyncSession = ...):
        query = (
            select(YoutubeChannel)
            .join(
                YoutubeSubscription,
                YoutubeChannel.id == YoutubeSubscription.channel_id,
                isouter=True,
            )
            .where(YoutubeSubscription.id.is_(None))
        )
        stream = await session.stream_scalars(query)
        async for channel in stream:
            await enqueue(
                function=self._delete_channel,
                kwargs={"channel_id": channel.id},
                at_front=True,
            )


youtube_tasker = YoutubeTasker()
