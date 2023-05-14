import asyncio
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from sqlalchemy import select, delete, false, and_

from dripdrop.admin import utils as admin_utils
from dripdrop.authentication.models import User
from dripdrop.services import database, rq_client, scraper, ytdlp
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

    proxy_address = await admin_utils.get_proxy_address(session=session)

    for subscribed_channel in await scraper.get_channel_subscriptions(
        channel_id=user_channel.id, proxy=proxy_address
    ):
        query = select(YoutubeChannel).where(YoutubeChannel.id == subscribed_channel.id)
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
                YoutubeNewSubscription(channel_id=subscribed_channel.id, email=email)
            )
        await session.commit()

    query = (
        select(YoutubeSubscription.channel_id.label("channel_id"))
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
    async for rows in database.stream_mappings(
        query=query, yield_per=1, session=session
    ):
        row = rows[0]
        await asyncio.to_thread(
            rq_client.default.enqueue,
            delete_subscription,
            channel_id=row.channel_id,
            email=email,
        )
    query = delete(YoutubeNewSubscription).where(YoutubeNewSubscription.email == email)
    await session.execute(query)
    await session.commit()


@rq_client.worker_task
async def add_channel_videos(
    channel_id: str = ...,
    date_after: str | None = None,
    playlist_chunk: tuple[int, int] = (1, 100),
    session: AsyncSession = ...,
):
    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
    results = await session.scalars(query)
    channel = results.first()
    if not channel:
        raise Exception(f"Channel ({channel_id}) not found")

    playlist_start, playlist_end = playlist_chunk
    playlist_chunk_size = playlist_end - playlist_start + 1  # Inclusive
    num_received_videos = 0

    if playlist_start == 1:
        channel.updating = True
        await session.commit()

        websocket_channel = WebsocketChannel(
            channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE
        )
        await websocket_channel.publish(
            message=YoutubeChannelUpdateResponse(id=channel.id, updating=True)
        )

    videos_info = ytdlp.extract_videos_info(
        url=generate_channel_videos_url(channel_id=channel_id),
        date_after=date_after,
        playlist_items=f"{playlist_start}:{playlist_end}",
    )

    async for video_info in videos_info:
        server_current_time = datetime.now(tz=tzlocal())
        current_time = get_current_time()

        video_id = video_info["id"]
        video_title = video_info["title"]
        video_thumbnail = video_info["thumbnail"]
        video_description = video_info["description"]
        video_category_name = video_info["categories"][0]
        video_upload_date = datetime.strptime(
            video_info["upload_date"], "%Y%m%d"
        ).replace(tzinfo=settings.timezone)

        if current_time.day != video_upload_date.day:
            video_upload_date = video_upload_date.replace(
                hour=server_current_time.hour,
                minute=server_current_time.minute,
                second=server_current_time.second,
            )
        else:
            video_upload_date = video_upload_date.replace(
                hour=current_time.hour,
                minute=current_time.minute,
                second=current_time.second,
            )

        query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
        results = await session.scalars(query)
        video = results.first()
        if video:
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
        await session.commit()
        num_received_videos += 1

    if playlist_chunk_size == num_received_videos:
        next_playlist_chunk = (
            playlist_end + 1,
            playlist_end + playlist_chunk_size,
        )
        await asyncio.to_thread(
            rq_client.default.enqueue,
            add_channel_videos,
            channel_id=channel_id,
            date_after=date_after,
            playlist_chunk=next_playlist_chunk,
        )
    else:
        websocket_channel = WebsocketChannel(
            channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE
        )
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


@rq_client.worker_task
async def update_subscriptions(session: AsyncSession = ...):
    query = select(User)
    async for users in database.stream_scalars(
        query=query, yield_per=1, session=session
    ):
        user = users[0]
        await asyncio.to_thread(
            rq_client.default.enqueue, update_user_subscriptions, email=user.email
        )