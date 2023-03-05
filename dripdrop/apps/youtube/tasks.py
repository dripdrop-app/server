import dateutil.parser
import traceback
from datetime import datetime, timedelta
from sqlalchemy import select, func, delete

from dripdrop.apps.authentication.models import User
from dripdrop.database import AsyncSession
from dripdrop.logging import logger
from dripdrop.services.google_api import google_api
from dripdrop.services.ytdlp import ytdlp
from dripdrop.settings import settings
from dripdrop.rq import enqueue
from dripdrop.utils import worker_task

from .models import (
    YoutubeUserChannel,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeNewSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
)


class YoutubeTasker:
    @worker_task
    async def update_video_categories(
        self, cron: bool = ..., session: AsyncSession = ...
    ):
        if not cron:
            query = select(func.count(YoutubeVideoCategory.id))
            count = await session.scalar(query)
            if count > 0:
                return
        video_categories = await google_api.get_video_categories()
        for category in video_categories:
            try:
                id = int(category["id"])
                name = category["snippet"]["title"]
                query = select(YoutubeVideoCategory).where(
                    YoutubeVideoCategory.id == id
                )
                results = await session.scalars(query)
                category = results.first()
                if category:
                    category.name = name
                else:
                    session.add(YoutubeVideoCategory(id=id, name=name))
                await session.commit()
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
        self, email: str = ..., session: AsyncSession = ...
    ):
        query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == email)
        results = await session.scalars(query)
        user_channel = results.first()
        if not user_channel:
            return

        async for subscriptions in google_api.get_channel_subscriptions(
            channel_id=user_channel.channel_id
        ):
            for subscription in subscriptions:
                subscription_id = subscription["id"]
                subscription_snippet = subscription["snippet"]
                channel_id = subscription_snippet["resourceId"]["channelId"]
                channel_title = subscription_snippet["title"]
                channel_thumbnail = subscription_snippet["thumbnails"]["high"]["url"]
                published_at = dateutil.parser.parse(
                    subscription_snippet["publishedAt"]
                )
                try:
                    query = select(YoutubeChannel).where(
                        YoutubeChannel.id == channel_id
                    )
                    results = await session.scalars(query)
                    channel = results.first()
                    if channel:
                        channel.title = channel_title
                        channel.thumbnail = channel_thumbnail
                    else:
                        session.add(
                            YoutubeChannel(
                                id=channel_id,
                                title=channel_title,
                                thumbnail=channel_thumbnail,
                                last_videos_updated=datetime.now(tz=settings.timezone)
                                - timedelta(days=30),
                            )
                        )
                        await session.commit()
                        await enqueue(
                            self.add_new_channel_videos_job,
                            kwargs={"channel_id": channel_id},
                            at_front=True,
                        )
                    query = select(YoutubeSubscription).where(
                        YoutubeSubscription.id == subscription_id
                    )
                    results = await session.scalars(query)
                    if not results.first():
                        session.add(
                            YoutubeSubscription(
                                id=subscription_id,
                                email=user_channel.email,
                                channel_id=channel_id,
                                published_at=published_at,
                            )
                        )
                    query = select(YoutubeNewSubscription).where(
                        YoutubeNewSubscription.id == subscription_id
                    )
                    results = await session.scalars(query)
                    if not results.first():
                        session.add(
                            YoutubeNewSubscription(
                                id=subscription_id, email=user_channel.email
                            )
                        )
                    await session.commit()
                except Exception:
                    logger.exception(traceback.format_exc())
        query = (
            select(YoutubeSubscription.id.label("subscription_id"))
            .join(
                YoutubeNewSubscription,
                YoutubeNewSubscription.id == YoutubeSubscription.id,
                isouter=True,
            )
            .where(
                YoutubeSubscription.email == user_channel.email,
                YoutubeNewSubscription.id.is_(None),
            )
        )
        stream = await session.stream(query)
        async for row in stream:
            row = row._mapping
            await enqueue(
                function=self._delete_subscription,
                kwargs={
                    "subscription_id": row.subscription_id,
                    "email": user_channel.email,
                },
                at_front=True,
            )
        query = delete(YoutubeNewSubscription).where(
            YoutubeNewSubscription.email == user_channel.email
        )
        await session.execute(query)

    @worker_task
    async def add_new_channel_videos_job(
        self,
        channel_id: str = ...,
        date_after: str | None = None,
        session: AsyncSession = ...,
    ):
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = await session.scalars(query)
        channel = results.first()
        if not channel:
            raise Exception("Channel not found")
        date_after = (
            date_after
            if date_after
            else "{year}{month}{day}".format(
                year=channel.last_videos_updated.year,
                month=str(channel.last_videos_updated.month).rjust(2, "0"),
                day=str(channel.last_videos_updated.day).rjust(2, "0"),
            )
        )
        videos_info = await ytdlp.extract_videos_info(
            url=f"https://youtube.com/channel/{channel_id}/videos",
            date_after=date_after,
        )
        for video_info in videos_info:
            current_time = datetime.now(tz=settings.timezone)
            video_id = video_info["id"]
            video_title = video_info["title"]
            video_thumbnail = video_info["thumbnail"]
            video_category_name = video_info["categories"][0]
            video_upload_date = datetime.strptime(
                video_info["upload_date"], "%Y%m%d"
            ).replace(
                hour=current_time.hour,
                minute=current_time.minute,
                second=current_time.second,
                tzinfo=settings.timezone,
            )
            query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
            results = await session.scalars(query)
            video = results.first()
            if video:
                video.title = video_title
                video.thumbnail = video_thumbnail
                if video.title != video_title or video.thumbnail != video_thumbnail:
                    video.published_at = video_upload_date
            else:
                query = select(YoutubeVideoCategory).where(
                    YoutubeVideoCategory.name == video_category_name
                )
                results = await session.scalars(query)
                video_category = results.first()
                if not video_category:
                    raise Exception(f"video category not found {video_category_name}")
                session.add(
                    YoutubeVideo(
                        id=video_id,
                        title=video_title,
                        thumbnail=video_thumbnail,
                        channel_id=channel_id,
                        category_id=video_category.id,
                        published_at=video_upload_date,
                    )
                )
            await session.commit()
        channel.last_videos_updated = datetime.now(tz=settings.timezone)
        await session.commit()

    @worker_task
    async def update_channel_videos(
        self, date_after: str | None = None, session: AsyncSession = ...
    ):
        query = select(YoutubeChannel)
        stream = await session.stream_scalars(query)
        async for channel in stream:
            await enqueue(
                function=self.add_new_channel_videos_job,
                kwargs={"channel_id": channel.id, "date_after": date_after},
                at_front=True,
            )

    @worker_task
    async def update_subscriptions(self, session: AsyncSession = ...):
        query = select(User)
        stream = await session.stream_scalars(query)
        async for user in stream:
            await enqueue(
                function=self.update_user_subscriptions,
                kwargs={"email": user.email},
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
