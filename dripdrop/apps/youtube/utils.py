import math
from bs4 import BeautifulSoup
from sqlalchemy import select, func, and_

from dripdrop.apps.authentication.models import User
from dripdrop.services.database import AsyncSession
from dripdrop.services.http_client import http_client

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
            YoutubeVideo.description,
            YoutubeChannel.title.label("channel_title"),
            YoutubeChannel.thumbnail.label("channel_thumbnail"),
            YoutubeVideoLike.email,
            YoutubeVideoLike.created_at.label("liked"),
            YoutubeVideoWatch.email,
            YoutubeVideoWatch.created_at.label("watched"),
            YoutubeVideoQueue.email,
            YoutubeVideoQueue.created_at.label("queued"),
        )
        .join(YoutubeChannel, YoutubeVideo.channel_id == YoutubeChannel.id)
        .join(
            YoutubeSubscription,
            and_(
                YoutubeChannel.id == YoutubeSubscription.channel_id,
                YoutubeSubscription.email == user.email,
                YoutubeSubscription.deleted_at.is_(None),
            ),
            isouter=not subscribed_only,
        )
        .join(
            YoutubeVideoQueue,
            and_(
                YoutubeVideo.id == YoutubeVideoQueue.video_id,
                YoutubeVideoQueue.email == user.email,
            ),
            isouter=not queued_only,
        )
        .join(
            YoutubeVideoLike,
            and_(
                YoutubeVideo.id == YoutubeVideoLike.video_id,
                YoutubeVideoLike.email == user.email,
            ),
            isouter=not liked_only,
        )
        .join(
            YoutubeVideoWatch,
            and_(
                YoutubeVideo.id == YoutubeVideoWatch.video_id,
                YoutubeVideoWatch.email == user.email,
            ),
            isouter=True,
        )
    )
    if channel_id:
        query = query.where(YoutubeChannel.id == channel_id)
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


async def get_channel_id_from_handle(handle: str = ...):
    response = await http_client.get(f"https://youtube.com/{handle}")
    if response.is_error:
        return None
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", itemprop="channelId")
    if not tag:
        return None
    return tag["content"]
