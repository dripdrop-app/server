import math
import traceback
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy import select, func, and_

from dripdrop.authentication.dependencies import (
    get_authenticated_user,
    AuthenticatedUser,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.logger import logger
from dripdrop.youtube import utils
from dripdrop.youtube.models import (
    YoutubeVideoCategory,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeSubscription,
)
from dripdrop.youtube.responses import (
    ErrorMessages,
    YoutubeVideoCategoriesResponse,
    VideosResponse,
    VideoQueueResponse,
)


api = APIRouter(
    prefix="/videos",
    tags=["YouTube Videos"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.get("/categories", response_model=YoutubeVideoCategoriesResponse)
async def get_youtube_video_categories(
    session: DatabaseSession, user: AuthenticatedUser, channel_id: str = Query(None)
):
    query = (
        select(YoutubeVideoCategory.id, YoutubeVideoCategory.name)
        .join(YoutubeVideo, YoutubeVideo.category_id == YoutubeVideoCategory.id)
        .join(YoutubeChannel, YoutubeChannel.id == YoutubeVideo.channel_id)
        .join(
            YoutubeSubscription,
            YoutubeSubscription.channel_id == YoutubeChannel.id,
            isouter=True,
        )
        .order_by(YoutubeVideoCategory.name.asc())
        .distinct()
    )
    if not channel_id:
        query = query.where(
            YoutubeSubscription.email == user.email,
            YoutubeSubscription.deleted_at.is_(None),
        )
    else:
        query = query.where(YoutubeChannel.id == channel_id)
    results = await session.execute(query)
    categories = results.mappings().all()
    return YoutubeVideoCategoriesResponse(categories=categories)


@api.get(
    "/{page}/{per_page}",
    response_model=VideosResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.VIDEO_CATEGORIES_INVALID
        },
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.PAGE_NOT_FOUND},
    },
)
async def get_youtube_videos(
    user: AuthenticatedUser,
    session: DatabaseSession,
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    video_categories: str = Query(""),
    channel_id: str | None = Query(None),
    liked_only: bool = Query(False),
    queued_only: bool = Query(False),
):
    try:
        if video_categories:
            video_categories = list(
                map(lambda category: int(category), video_categories.split(","))
            )
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.VIDEO_CATEGORIES_INVALID,
        )

    offset = (page - 1) * page
    query = select(YoutubeVideo)
    if channel_id:
        query = query.where(YoutubeVideo.channel_id == channel_id)
    else:
        if not queued_only and not liked_only:
            query = query.where(
                YoutubeVideo.channel_id.in_(
                    select(YoutubeChannel.id)
                    .join(
                        YoutubeSubscription,
                        YoutubeChannel.id == YoutubeSubscription.channel_id,
                    )
                    .where(
                        YoutubeSubscription.email == user.email,
                        YoutubeSubscription.deleted_at.is_(None),
                    )
                )
            )
    if video_categories:
        query = query.where(YoutubeVideo.category_id.in_(video_categories))

    if liked_only:
        query = (
            query.join(YoutubeVideoLike, YoutubeVideo.id == YoutubeVideoLike.video_id)
            .where(YoutubeVideoLike.email == user.email)
            .order_by(YoutubeVideoLike.created_at.desc())
        )
    elif queued_only:
        query = (
            query.join(
                YoutubeVideoQueue,
                YoutubeVideo.id == YoutubeVideoQueue.video_id,
            )
            .where(YoutubeVideoQueue.email == user.email)
            .order_by(YoutubeVideoQueue.created_at.asc())
        )
    else:
        query = query.order_by(YoutubeVideo.published_at.desc())

    videos_query = query.offset(offset).limit(per_page)

    results = await session.scalars(videos_query)
    videos = await utils.get_videos_attributes(
        session=session, user=user, videos=results.all()
    )

    count = await session.scalar(select(func.count(query.subquery().columns.id)))
    total_pages = 1
    if count is not None and per_page is not None:
        total_pages = math.ceil(count / per_page)

    if page > total_pages and page != 1:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return VideosResponse(videos=videos, total_pages=total_pages)


@api.get(
    "/queue",
    response_model=VideoQueueResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_QUEUE_NOT_FOUND}
    },
)
async def get_youtube_video_queue(
    user: AuthenticatedUser, session: DatabaseSession, index: int = Query(..., ge=1)
):
    query = (
        select(YoutubeVideo)
        .join(
            YoutubeVideoQueue,
            and_(
                YoutubeVideo.id == YoutubeVideoQueue.video_id,
                YoutubeVideoQueue.email == user.email,
            ),
        )
        .offset(max(index - 2, 0))
        .limit(2 if index == 1 else 3)
    )
    results = await session.scalars(query)
    videos = results.all()

    [prev_video, current_video, next_video] = [None] * 3

    if index != 1 and videos:
        prev_video = videos.pop(0)
    if videos:
        current_video = videos.pop(0)
        current_videos = await utils.get_videos_attributes(
            session=session, user=user, videos=[current_video]
        )
        current_video = current_videos[0]
    if videos:
        next_video = videos.pop(0)
    if not current_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.VIDEO_QUEUE_NOT_FOUND,
        )
    return VideoQueueResponse(
        current_video=current_video, prev=bool(prev_video), next=bool(next_video)
    )
