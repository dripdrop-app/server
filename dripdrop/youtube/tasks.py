import asyncio
import dateutil.parser
from datetime import datetime, timedelta
from rq.job import Retry
from sqlalchemy import select, delete, false, and_

from dripdrop.authentication.models import User
from dripdrop.services import database, google_api, rq_client
from dripdrop.services.database import AsyncSession
from dripdrop.services.websocket_channel import WebsocketChannel, RedisChannels
from dripdrop.settings import settings
from dripdrop.utils import get_current_time
from dripdrop.youtube.models import (
    YoutubeUserChannel,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeNewSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
)
from dripdrop.youtube.responses import YoutubeChannelUpdateResponse


@rq_client.worker_task
async def delete_subscription(
    channel_id: str = ..., email: str = ..., session: AsyncSession = ...
):
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.channel_id == channel_id,
        YoutubeSubscription.email == email,
    )
    subscription = await session.scalar(query)
    if not subscription:
        raise Exception(f"Subscription ({channel_id}, {email}) not found")
    subscription.deleted_at = get_current_time()
    await session.commit()


@rq_client.worker_task
async def update_user_subscriptions(email: str = ..., session: AsyncSession = ...):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == email)
    user_channel = await session.scalar(query)
    if not user_channel:
        return

    async for subscribed_channels in google_api.get_channel_subscriptions(
        channel_id=user_channel.id
    ):
        for subscribed_channel in subscribed_channels:
            query = select(YoutubeChannel).where(
                YoutubeChannel.id == subscribed_channel.id
            )
            channel = await session.scalar(query)
            if channel:
                channel.title = subscribed_channel.title
                channel.thumbnail = subscribed_channel.thumbnail
            else:
                channel = YoutubeChannel(
                    id=subscribed_channel.id,
                    title=subscribed_channel.title,
                    thumbnail=subscribed_channel.thumbnail,
                    last_videos_updated=get_current_time() - timedelta(days=365),
                )
                session.add(channel)
                await session.commit()
                await asyncio.to_thread(
                    rq_client.default.enqueue,
                    add_channel_videos,
                    channel_id=channel.id,
                )
            query = select(YoutubeSubscription).where(
                YoutubeSubscription.channel_id == channel.id,
                YoutubeSubscription.email == email,
            )
            subscription = await session.scalar(query)
            if not subscription:
                session.add(YoutubeSubscription(email=email, channel_id=channel.id))
            else:
                if not subscription.user_submitted:
                    subscription.deleted_at = None

            query = select(YoutubeNewSubscription).where(
                YoutubeNewSubscription.channel_id == subscribed_channel.id,
                YoutubeNewSubscription.email == email,
            )
            new_subscription = await session.scalar(query)
            if not new_subscription:
                session.add(
                    YoutubeNewSubscription(
                        channel_id=subscribed_channel.id, email=email
                    )
                )
            await session.commit()

    query = (
        select(YoutubeSubscription.channel_id)
        .join(
            YoutubeNewSubscription,
            and_(
                YoutubeNewSubscription.channel_id == YoutubeSubscription.channel_id,
                YoutubeNewSubscription.email == YoutubeSubscription.email,
            ),
            isouter=True,
        )
        .where(
            YoutubeSubscription.email == user_channel.email,
            YoutubeSubscription.deleted_at.is_(None),
            YoutubeSubscription.user_submitted == false(),
            YoutubeNewSubscription.channel_id.is_(None),
        )
    )
    async for rows in database.stream_scalars(
        query=query, yield_per=1, session=session
    ):
        row = rows[0]
        await asyncio.to_thread(
            rq_client.default.enqueue,
            delete_subscription,
            channel_id=row,
            email=email,
        )
    query = delete(YoutubeNewSubscription).where(YoutubeNewSubscription.email == email)
    await session.execute(query)
    await session.commit()


@rq_client.worker_task
async def add_channel_videos(
    channel_id: str = ...,
    date_after: str | None = None,
    session: AsyncSession = ...,
):
    date_limit = (
        datetime.strptime(date_after, "%Y%m%d").replace(tzinfo=settings.timezone)
        if date_after
        else None
    )

    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
    channel = await session.scalar(query)
    if not channel:
        raise Exception(f"Channel ({channel_id}) not found")

    channel.updating = True
    await session.commit()

    websocket_channel = WebsocketChannel(channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE)
    await websocket_channel.publish(
        message=YoutubeChannelUpdateResponse(id=channel.id, updating=True)
    )

    async for videos in google_api.get_channel_latest_videos(channel_id=channel_id):
        end_update = False
        for video in videos:
            video_upload_date = dateutil.parser.parse(video.published)
            if date_limit and video_upload_date < date_limit:
                end_update = True
                break

            query = select(YoutubeVideo).where(YoutubeVideo.id == video.id)
            existing_video = await session.scalar(query)

            if existing_video:
                existing_video.title = video.title
                existing_video.thumbnail = video.thumbnail
                existing_video.description = video.description
                if (
                    existing_video.title != video.title
                    or existing_video.thumbnail != video.thumbnail
                ):
                    existing_video.published_at = video_upload_date
            else:
                session.add(
                    YoutubeVideo(
                        id=video.id,
                        title=video.title,
                        thumbnail=video.thumbnail,
                        channel_id=channel_id,
                        category_id=video.category_id,
                        description=video.description,
                        published_at=video_upload_date,
                    )
                )
        if end_update:
            break

    websocket_channel = WebsocketChannel(channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE)
    await websocket_channel.publish(
        message=YoutubeChannelUpdateResponse(id=channel.id, updating=False)
    )
    channel.updating = False
    channel.last_videos_updated = get_current_time()

    await session.commit()


@rq_client.worker_task
async def update_channel_videos(
    date_after: str | None = None, session: AsyncSession = ...
):
    query = (
        select(YoutubeSubscription.channel_id.label("channel_id"))
        .where(YoutubeSubscription.deleted_at.is_(None))
        .distinct()
    )
    async for subscriptions in database.stream_mappings(
        query=query, yield_per=1, session=session
    ):
        subscription = subscriptions[0]
        query = select(YoutubeChannel).where(
            YoutubeChannel.id == subscription.channel_id
        )
        channel = await session.scalar(query)
        if channel:
            date_after_time = min(
                get_current_time() - timedelta(days=1),
                channel.last_videos_updated,
            )
            if date_after:
                date_after_time = datetime.strptime(date_after, "%Y%m%d")
            await asyncio.to_thread(
                rq_client.default.enqueue,
                add_channel_videos,
                channel_id=subscription.channel_id,
                date_after=date_after_time.strftime("%Y%m%d"),
            )


def update_channel_videos_cron():
    rq_client.high.enqueue(update_channel_videos)


@rq_client.worker_task
async def update_subscriptions(session: AsyncSession = ...):
    query = select(User)
    async for users in database.stream_scalars(
        query=query, yield_per=1, session=session
    ):
        user = users[0]
        await asyncio.to_thread(
            rq_client.default.enqueue,
            update_user_subscriptions,
            email=user.email,
            retry=Retry(2, [10, 30]),
        )


def update_subscriptions_cron():
    rq_client.high.enqueue(update_subscriptions)


@rq_client.worker_task
async def update_video_categories(session: AsyncSession = ...):
    async for video_categories in google_api.get_video_categories():
        for video_category in video_categories:
            query = select(YoutubeVideoCategory).where(
                YoutubeVideoCategory.id == video_category.id
            )
            existing_video_category = await session.scalar(query)
            if existing_video_category:
                existing_video_category.name = video_category.name
            else:
                session.add(
                    YoutubeVideoCategory(
                        id=video_category.id,
                        name=video_category.name,
                    )
                )
        await session.commit()


def update_video_categories_cron():
    rq_client.high.enqueue(update_video_categories)
