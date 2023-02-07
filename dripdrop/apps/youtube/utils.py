import math
from asgiref.sync import sync_to_async
from datetime import datetime
from sqlalchemy import select, func

from dripdrop.database import AsyncSession, Session
from dripdrop.services.google_api import google_api_service
from dripdrop.settings import settings

from .models import (
    GoogleAccount,
    YoutubeSubscription,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)


async def async_update_google_access_token(
    google_email: str = ..., session: AsyncSession = ...
):
    query = select(GoogleAccount).where(GoogleAccount.email == google_email)
    results = await session.scalars(query)
    account = results.first()
    if account:
        last_updated: datetime = account.last_updated
        difference = datetime.now(tz=settings.timezone) - last_updated.replace(
            tzinfo=settings.timezone
        )
        if difference.seconds >= account.expires:
            try:
                refresh_access_token = sync_to_async(
                    google_api_service.refresh_access_token
                )
                new_access_token = await refresh_access_token(
                    refresh_token=account.refresh_token
                )
                if new_access_token:
                    account.access_token = new_access_token["access_token"]
                    account.expires = new_access_token["expires_in"]
                    await session.commit()
            except Exception:
                account.access_token = ""
                account.expires = 0
                await session.commit()


def update_google_access_token(google_email: str = ..., session: Session = ...):
    query = select(GoogleAccount).where(GoogleAccount.email == google_email)
    results = session.scalars(query)
    account = results.first()
    if account:
        last_updated: datetime = account.last_updated
        difference = datetime.now(tz=settings.timezone) - last_updated.replace(
            tzinfo=settings.timezone
        )
        if difference.seconds >= account.expires:
            try:
                new_access_token = google_api_service.refresh_access_token(
                    refresh_token=account.refresh_token
                )
                if new_access_token:
                    account.access_token = new_access_token["access_token"]
                    account.expires = new_access_token["expires_in"]
                    session.commit()
            except Exception:
                account.access_token = ""
                account.expires = 0
                session.commit()


async def execute_videos_query(
    session: AsyncSession = ...,
    google_account: GoogleAccount = ...,
    channel_id: str | None = None,
    video_ids: list[str] | None = None,
    exclude_video_ids: list[str] | None = None,
    video_categories: list[int] | None = None,
    liked_only=False,
    queued_only=False,
    video_offset: int | None = None,
    queue_offest: int | None = None,
    limit: int | None = None,
):
    subscription_query = (
        select(YoutubeSubscription)
        .where(YoutubeSubscription.email == google_account.email)
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
        select(YoutubeVideoLike)
        .where(YoutubeVideoLike.email == google_account.email)
        .subquery()
    )
    video_queues_query = (
        select(YoutubeVideoQueue)
        .where(YoutubeVideoQueue.email == google_account.email)
        .offset(queue_offest)
        .subquery()
    )
    video_watches_query = (
        select(YoutubeVideoWatch)
        .where(YoutubeVideoWatch.email == google_account.email)
        .subquery()
    )
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
        subscription_query.join(
            channel_query,
            channel_query.columns.id == subscription_query.columns.channel_id,
        )
        .join(
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
    results = await session.execute(query.offset(video_offset))
    videos = results.mappings()
    if limit:
        videos = videos.fetchmany(limit)
    else:
        videos = videos.all()
    count = await session.scalar(select(func.count(query.columns.id)))
    total_pages = math.ceil(count / limit) if limit else 1
    return {"videos": videos, "total_pages": total_pages}
