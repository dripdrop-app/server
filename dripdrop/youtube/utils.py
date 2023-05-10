import math
from sqlalchemy import select, func

from dripdrop.authentication.models import User
from dripdrop.services.database import AsyncSession
from dripdrop.youtube.models import (
    YoutubeSubscription,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)


async def execute_videos_query(
    session: AsyncSession,
    user: User,
    channel_id: str | None = None,
    video_ids: list[str] | None = None,
    exclude_video_ids: list[str] | None = None,
    video_categories: list[int] | None = None,
    liked_only=False,
    queued_only=False,
    subscribed_only=True,
    offset: int | None = None,
    limit: int | None = None,
):
    subscriptions_query = (
        select(YoutubeSubscription)
        .where(
            YoutubeSubscription.email == user.email,
            YoutubeSubscription.deleted_at.is_(None),
        )
        .alias()
    )

    channels_query = select(YoutubeChannel)
    if channel_id:
        channels_query = channels_query.where(YoutubeChannel.id == channel_id)
    channels_query = channels_query.alias()

    videos_query = select(YoutubeVideo)
    if video_ids:
        videos_query = videos_query.where(YoutubeVideo.id.in_(video_ids))
    if exclude_video_ids:
        videos_query = videos_query.where(YoutubeVideo.id.not_in(exclude_video_ids))
    videos_query = videos_query.alias()

    video_categories_query = select(YoutubeVideoCategory)
    if video_categories:
        video_categories_query = video_categories_query.where(
            YoutubeVideoCategory.id.in_(video_categories)
        )
    video_categories_query = video_categories_query.alias()

    videos_queue_query = (
        select(YoutubeVideoQueue).where(YoutubeVideoQueue.email == user.email).alias()
    )
    videos_like_query = (
        select(YoutubeVideoLike).where(YoutubeVideoLike.email == user.email).alias()
    )
    videos_watch_query = (
        select(YoutubeVideoWatch).where(YoutubeVideoWatch.email == user.email).alias()
    )

    query = None
    if subscribed_only:
        query = subscriptions_query.join(
            channels_query, subscriptions_query.c.channel_id == channels_query.c.id
        )
    else:
        query = channels_query

    query = (
        query.join(videos_query, videos_query.c.channel_id == channels_query.c.id)
        .join(
            video_categories_query,
            video_categories_query.c.id == videos_query.c.category_id,
        )
        .join(
            videos_queue_query,
            videos_queue_query.c.video_id == videos_query.c.id,
            isouter=not queued_only,
        )
        .join(
            videos_like_query,
            videos_like_query.c.video_id == videos_query.c.id,
            isouter=not liked_only,
        )
        .join(
            videos_watch_query,
            videos_watch_query.c.video_id == videos_query.c.id,
            isouter=True,
        )
    )

    query = select(
        videos_query.c.id,
        videos_query.c.title,
        videos_query.c.thumbnail,
        videos_query.c.category_id,
        videos_query.c.published_at,
        videos_query.c.channel_id,
        videos_query.c.description,
        video_categories_query.c.name.label("category_name"),
        channels_query.c.title.label("channel_title"),
        channels_query.c.thumbnail.label("channel_thumbnail"),
        videos_like_query.c.created_at.label("liked"),
        videos_watch_query.c.created_at.label("watched"),
        videos_queue_query.c.created_at.label("queued"),
    ).select_from(query)

    if liked_only:
        query = query.order_by(videos_like_query.c.created_at.desc())
    elif queued_only:
        query = query.order_by(videos_queue_query.c.created_at.asc())
    else:
        query = query.order_by(videos_query.c.published_at.desc())
    query = query.order_by(videos_query.c.title.desc())

    results = await session.execute(query.offset(offset))
    videos = results.mappings()
    if limit:
        videos = videos.fetchmany(limit)
    else:
        videos = videos.all()
    count = await session.scalar(select(func.count(query.subquery().columns.id)))
    total_pages = 1
    if count is not None and limit is not None:
        total_pages = math.ceil(count / limit)
    return (videos, total_pages)
