from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from sqlalchemy import select, delete, false, and_

import dripdrop.tasks as dripdrop_tasks
import dripdrop.utils as dripdrop_utils
from dripdrop.apps.admin import utils as admin_utils
from dripdrop.apps.authentication.models import User
from dripdrop.services import database, rq_client, scraper, ytdlp
from dripdrop.services.database import AsyncSession
from dripdrop.services.websocket_channel import WebsocketChannel, RedisChannels
from dripdrop.settings import settings

from .models import (
    YoutubeUserChannel,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeNewSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
)
from .responses import YoutubeChannelUpdateResponse


@dripdrop_tasks.worker_task()
async def _delete_subscription(
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
    subscription.deleted_at = dripdrop_utils.get_current_time()
    await session.commit()


@dripdrop_tasks.worker_task()
async def update_user_subscriptions(email: str = ..., session: AsyncSession = ...):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == email)
    results = await session.scalars(query)
    user_channel = results.first()
    if not user_channel:
        return

    proxy = await admin_utils.get_proxy(session=session)
    if proxy:
        proxy_address = f"{proxy.ip_address}:{proxy.port}"
        proxy.last_used = dripdrop_utils.get_current_time()
        await session.commit()

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
                    last_videos_updated=dripdrop_utils.get_current_time()
                    - timedelta(days=365),
                )
            )
            await session.commit()
            await rq_client.enqueue(
                add_new_channel_videos, kwargs={"channel_id": subscribed_channel.id}
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
    stream = await session.stream(query)
    async for row in stream.mappings():
        await rq_client.enqueue(
            function=_delete_subscription,
            kwargs={"channel_id": row.channel_id, "email": email},
        )
    query = delete(YoutubeNewSubscription).where(YoutubeNewSubscription.email == email)
    await session.execute(query)
    await session.commit()


@dripdrop_tasks.worker_task()
async def add_new_channel_videos(
    channel_id: str = ..., date_after: str | None = None, session: AsyncSession = ...
):
    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
    results = await session.scalars(query)
    channel = results.first()
    if not channel:
        raise Exception(f"Channel ({channel_id}) not found")

    # if channel.updating:
    #     raise Exception(f"Channel ({channel_id}) already updating")

    channel.updating = True
    await session.commit()

    websocket_channel = WebsocketChannel(channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE)
    await websocket_channel.publish(
        message=YoutubeChannelUpdateResponse(id=channel.id, updating=True)
    )

    day_ago = dripdrop_utils.get_current_time() - timedelta(days=1)
    last_updated = min(day_ago, channel.last_videos_updated)

    date_after = (
        date_after
        if date_after
        else "{year}{month}{day}".format(
            year=last_updated.year,
            month=str(last_updated.month).rjust(2, "0"),
            day=str(last_updated.day).rjust(2, "0"),
        )
    )
    try:
        async for video_info in ytdlp.extract_videos_info(
            url=f"https://youtube.com/channel/{channel_id}/videos",
            date_after=date_after,
        ):
            server_current_time = datetime.now(tz=tzlocal())
            current_time = dripdrop_utils.get_current_time()

            video_id = video_info["id"]
            video_title = video_info["title"]
            video_thumbnail = video_info["thumbnail"]
            video_description = video_info["description"]
            video_category_name = video_info["categories"][0]
            video_upload_date = datetime.strptime(
                video_info["upload_date"], "%Y%m%d"
            ).replace(
                hour=current_time.hour,
                minute=current_time.minute,
                second=current_time.second,
                tzinfo=settings.timezone,
            )

            if current_time.day != video_upload_date.day:
                video_upload_date.replace(
                    hour=server_current_time.hour,
                    minute=server_current_time.minute,
                    second=server_current_time.second,
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
        channel.last_videos_updated = dripdrop_utils.get_current_time()
    except Exception as e:
        raise e
    finally:
        channel.updating = False
        await session.commit()
        await websocket_channel.publish(
            message=YoutubeChannelUpdateResponse(id=channel.id, updating=False)
        )


@dripdrop_tasks.worker_task()
async def update_channel_videos(
    date_after: str | None = None, session: AsyncSession = ...
):
    current_time = dripdrop_utils.get_current_time()
    query = (
        select(YoutubeSubscription.channel_id.label("channel_id"))
        .where(YoutubeSubscription.deleted_at.is_(None))
        .distinct()
    )
    if current_time.hour % 2 == 0:
        query = query.order_by(YoutubeSubscription.channel_id.desc())
    else:
        query = query.order_by(YoutubeSubscription.channel_id.asc())
    async for subscriptions in database.stream_mappings(
        query=query, yield_per=1, session=session
    ):
        subscription = subscriptions[0]
        await rq_client.enqueue(
            function=add_new_channel_videos,
            kwargs={"channel_id": subscription.channel_id, "date_after": date_after},
            retry=rq_client.Retry(max=2, interval=settings.timeout),
        )


@dripdrop_tasks.worker_task()
async def update_subscriptions(session: AsyncSession = ...):
    query = select(User)
    async for users in database.stream_scalars(
        query=query, yield_per=1, session=session
    ):
        user = users[0]
        await rq_client.enqueue(
            function=update_user_subscriptions,
            kwargs={"email": user.email},
        )
