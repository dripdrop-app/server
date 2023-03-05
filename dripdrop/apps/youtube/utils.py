import math
from sqlalchemy import select, func, or_

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
    query = (
        select(
            YoutubeVideo.id,
            YoutubeVideo.title,
            YoutubeVideo.thumbnail,
            YoutubeVideo.category_id,
            YoutubeVideo.published_at,
            YoutubeVideo.channel_id,
            YoutubeChannel.title.label("channel_title"),
            YoutubeChannel.thumbnail.label("channel_thumbnail"),
            YoutubeVideoLike.created_at.label("liked"),
            YoutubeVideoWatch.created_at.label("watched"),
            YoutubeVideoQueue.created_at.label("queued"),
        )
        .join(YoutubeChannel, YoutubeVideo.channel_id == YoutubeChannel.id)
        .join(
            YoutubeSubscription,
            YoutubeChannel.id == YoutubeSubscription.channel_id,
            isouter=True,
        )
        .join(
            YoutubeVideoQueue,
            YoutubeVideo.id == YoutubeVideoQueue.video_id,
            isouter=not queued_only,
        )
        .join(
            YoutubeVideoLike,
            YoutubeVideo.id == YoutubeVideoLike.video_id,
            isouter=not liked_only,
        )
        .join(
            YoutubeVideoWatch,
            YoutubeVideo.id == YoutubeVideoWatch.video_id,
            isouter=True,
        )
    ).where(
        or_(YoutubeVideoLike.email.is_(None), YoutubeVideoLike.email == user.email),
        or_(YoutubeVideoWatch.email.is_(None), YoutubeVideoWatch.email == user.email),
        or_(YoutubeVideoQueue.email.is_(None), YoutubeVideoQueue.email == user.email),
    )
    if channel_id:
        query = query.where(YoutubeChannel.id == channel_id)
    if subscribed_only:
        query = query.where(YoutubeSubscription.email == user.email)
    if video_categories:
        query = query.where(YoutubeVideo.category_id.in_(video_categories))
    if video_ids:
        query = query.where(YoutubeVideo.id.in_(video_ids))
    if exclude_video_ids:
        query = query.where(YoutubeVideo.id.not_in(exclude_video_ids))

    if liked_only:
        query = query.order_by(YoutubeVideoLike.created_at.desc())
    elif queued_only:
        query = query.order_by(YoutubeVideoQueue.created_at.asc())
    else:
        query = query.order_by(YoutubeVideo.published_at.desc())

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
