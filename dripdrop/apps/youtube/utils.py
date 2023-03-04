import math
from sqlalchemy import select, func

from dripdrop.apps.authentication.models import User
from dripdrop.database import AsyncSession

from .models import (
    YoutubeSubscription,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)


async def execute_videos_query(
    session: AsyncSession = ...,
    user: User = ...,
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
    subscription_query = (
        select(YoutubeSubscription)
        .where(YoutubeSubscription.email == user.email)
        .subquery()
    )
    channel_query = (
        select(YoutubeChannel)
        .where(
            YoutubeChannel.id == channel_id
            if channel_id
            else YoutubeChannel.id.is_not(None)
        )
        .subquery()
    )
    videos_query = (
        select(YoutubeVideo)
        .where(
            YoutubeVideo.category_id.in_(video_categories)
            if video_categories and len(video_categories) != 0
            else YoutubeVideo.category_id.is_not(None),
            YoutubeVideo.id.in_(video_ids)
            if video_ids
            else YoutubeVideo.id.is_not(None),
            YoutubeVideo.id.not_in(exclude_video_ids)
            if exclude_video_ids
            else YoutubeVideo.id.is_not(None),
        )
        .subquery()
    )
    video_likes_query = (
        select(YoutubeVideoLike).where(YoutubeVideoLike.email == user.email).subquery()
    )
    video_queues_query = (
        select(YoutubeVideoQueue)
        .where(YoutubeVideoQueue.email == user.email)
        .subquery()
    )
    video_watches_query = (
        select(YoutubeVideoWatch)
        .where(YoutubeVideoWatch.email == user.email)
        .subquery()
    )
    subquery = None
    if subscribed_only:
        subquery = subscription_query.join(
            channel_query,
            channel_query.columns.id == subscription_query.columns.channel_id,
        )
    else:
        subquery = channel_query
    query = select(
        videos_query.columns.id,
        videos_query.columns.title,
        videos_query.columns.thumbnail,
        videos_query.columns.category_id,
        videos_query.columns.published_at,
        videos_query.columns.channel_id,
        channel_query.columns.title.label("channel_title"),
        channel_query.columns.thumbnail.label("channel_thumbnail"),
        video_likes_query.columns.created_at.label("liked"),
        video_watches_query.columns.created_at.label("watched"),
        video_queues_query.columns.created_at.label("queued"),
    ).select_from(
        subquery.join(
            videos_query,
            videos_query.columns.channel_id == channel_query.columns.id,
        )
        .join(
            video_likes_query,
            video_likes_query.columns.video_id == videos_query.columns.id,
            isouter=not liked_only,
        )
        .join(
            video_queues_query,
            video_queues_query.columns.video_id == videos_query.columns.id,
            isouter=not queued_only,
        )
        .join(
            video_watches_query,
            video_watches_query.columns.video_id == videos_query.columns.id,
            isouter=True,
        )
    )
    if liked_only:
        query = query.order_by(video_likes_query.columns.created_at.desc())
    elif queued_only:
        query = query.order_by(video_queues_query.columns.created_at.asc())
    else:
        query = query.order_by(videos_query.columns.published_at.desc())
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
