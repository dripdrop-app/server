import asyncio
import traceback
from datetime import datetime, timedelta
from rq.job import Retry
from sqlalchemy import select, delete, false, and_

from dripdrop.authentication.models import User
from dripdrop.logger import logger
from dripdrop.services import database, google_api, invidious, rq_client
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


def generate_channel_videos_url(channel_id: str = ...):
    return f"https://youtube.com/channel/{channel_id}/videos"


@rq_client.worker_task
async def delete_subscription(
    channel_id: str = ..., email: str = ..., session: AsyncSession = ...
):
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.channel_id == channel_id,
        YoutubeSubscription.email == email,
    )
    results = await session.scalars(query)
    subscription = results.first()
    if not subscription:
        raise Exception(f"Subscription ({channel_id}, {email}) not found")
    subscription.deleted_at = get_current_time()
    await session.commit()


@rq_client.worker_task
async def update_user_subscriptions(email: str = ..., session: AsyncSession = ...):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == email)
    results = await session.scalars(query)
    user_channel = results.first()
    if not user_channel:
        return

    async for subscribed_channels in google_api.get_channel_subscriptions(
        channel_id=user_channel.id
    ):
        for subscribed_channel in subscribed_channels:
            query = select(YoutubeChannel).where(
                YoutubeChannel.id == subscribed_channel.id
            )
            results = await session.scalars(query)
            channel = results.first()
            if channel:
                channel.title = subscribed_channel.title
                channel.thumbnail = subscribed_channel.thumbnail
            else:
                session.add(
                    YoutubeChannel(
                        id=subscribed_channel.id,
                        title=subscribed_channel.title,
                        thumbnail=subscribed_channel.thumbnail,
                        last_videos_updated=get_current_time() - timedelta(days=365),
                    )
                )
                await session.commit()
                await asyncio.to_thread(
                    rq_client.default.enqueue,
                    add_channel_videos,
                    channel_id=subscribed_channel.id,
                )
            query = select(YoutubeSubscription).where(
                YoutubeSubscription.channel_id == subscribed_channel.id,
                YoutubeSubscription.email == email,
            )
            results = await session.scalars(query)
            subscription = results.first()
            if not subscription:
                session.add(
                    YoutubeSubscription(
                        email=email,
                        channel_id=subscribed_channel.id,
                    )
                )
            else:
                if not subscription.user_submitted:
                    subscription.deleted_at = None

            query = select(YoutubeNewSubscription).where(
                YoutubeNewSubscription.channel_id == subscribed_channel.id,
                YoutubeNewSubscription.email == email,
            )
            results = await session.scalars(query)
            if not results.first():
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
    continuation_token: str | None = None,
    session: AsyncSession = ...,
):
    date_limit = (
        datetime.strptime(date_after, "%Y%m%d").replace(tzinfo=settings.timezone)
        if date_after
        else None
    )

    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
    results = await session.scalars(query)
    channel = results.first()
    if not channel:
        raise Exception(f"Channel ({channel_id}) not found")

    if not continuation_token:
        channel.updating = True
        await session.commit()

        websocket_channel = WebsocketChannel(
            channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE
        )
        await websocket_channel.publish(
            message=YoutubeChannelUpdateResponse(id=channel.id, updating=True)
        )

    response = await invidious.get_youtube_channel_videos(
        channel_id=channel_id, continuation_token=continuation_token
    )
    retrieve_fails = 0
    end_update = False

    for video_info in response.videos:
        video_id = video_info["videoId"]
        video_title = video_info["title"]
        video_published = video_info["published"]

        try:
            detailed_video_info = await invidious.get_youtube_video_info(
                video_id=video_id
            )
            video_thumbnail = detailed_video_info["videoThumbnails"][0]["url"]
            video_description = detailed_video_info["description"]
            video_category_name = detailed_video_info["genre"]

            query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
            results = await session.scalars(query)
            video = results.first()

            video_upload_date = datetime.fromtimestamp(video_published)

            if video:
                if date_limit and video.published_at < date_limit:
                    end_update = True
                    break
                video.title = video_title
                video.thumbnail = video_thumbnail
                video.description = video_description
                if video.title != video_title or video.thumbnail != video_thumbnail:
                    video.published_at = video_upload_date
            else:
                query = select(YoutubeVideoCategory).where(
                    YoutubeVideoCategory.name == video_category_name
                )
                results = await session.scalars(query)
                video_category = results.first()
                if not video_category:
                    video_category = YoutubeVideoCategory(name=video_category_name)
                    session.add(video_category)
                    await session.commit()
                session.add(
                    YoutubeVideo(
                        id=video_id,
                        title=video_title,
                        thumbnail=video_thumbnail,
                        channel_id=channel_id,
                        category_id=video_category.id,
                        description=video_description,
                        published_at=video_upload_date,
                    )
                )
        except Exception:
            retrieve_fails += 1
            logger.exception(traceback.format_exc())
        await session.commit()

    if (
        not response.continuation
        or end_update
        or retrieve_fails == len(response.videos)
    ):
        websocket_channel = WebsocketChannel(
            channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE
        )
        await websocket_channel.publish(
            message=YoutubeChannelUpdateResponse(id=channel.id, updating=False)
        )
        channel.updating = False
        channel.last_videos_updated = get_current_time()
    else:
        await asyncio.to_thread(
            rq_client.default.enqueue,
            add_channel_videos,
            channel_id=channel_id,
            date_after=date_after,
            continuation_token=response.continuation,
        )

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
        results = await session.scalars(query)
        channel = results.first()
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
