import math
import traceback
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import joinedload, selectinload

from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.logger import logger
from dripdrop.youtube.models import (
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)
from dripdrop.youtube.requests import VideosQueryParams
from dripdrop.youtube.responses import (
    ErrorMessages,
    VideoQueueResponse,
    VideosResponse,
    YoutubeVideoCategoriesResponse,
    YoutubeVideoResponse,
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
        select(YoutubeVideoCategory)
        .join(YoutubeVideo)
        .join(YoutubeChannel)
        .join(YoutubeSubscription, isouter=True)
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
    categories = results.scalars().all()
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
    query_params: Annotated[VideosQueryParams, Query()],
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
):
    video_categories = []
    try:
        if query_params.video_categories:
            video_categories = [
                int(category) for category in query_params.video_categories.split(",")
            ]
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.VIDEO_CATEGORIES_INVALID,
        )

    offset = (page - 1) * per_page
    query = select(YoutubeVideo)
    if query_params.channel_id:
        query = query.where(YoutubeVideo.channel_id == query_params.channel_id)
    else:
        if not query_params.queued_only and not query_params.liked_only:
            query = query.where(
                YoutubeVideo.channel_id.in_(
                    select(YoutubeChannel.id)
                    .join(YoutubeSubscription)
                    .where(
                        YoutubeSubscription.email == user.email,
                        YoutubeSubscription.deleted_at.is_(None),
                    )
                )
            )
    if video_categories:
        query = query.where(YoutubeVideo.category_id.in_(video_categories))

    if query_params.liked_only:
        query = (
            query.join(YoutubeVideoLike)
            .where(YoutubeVideoLike.email == user.email)
            .order_by(YoutubeVideoLike.created_at.desc())
        )
    elif query_params.queued_only:
        query = (
            query.join(YoutubeVideoQueue)
            .where(YoutubeVideoQueue.email == user.email)
            .order_by(YoutubeVideoQueue.created_at.asc())
        )
    else:
        query = query.order_by(YoutubeVideo.published_at.desc())

    query = query.order_by(YoutubeVideo.title.desc())

    videos_query = (
        query.offset(offset)
        .limit(per_page)
        .options(
            joinedload(YoutubeVideo.channel),
            joinedload(YoutubeVideo.category),
            selectinload(YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)),
            selectinload(
                YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)
            ),
            selectinload(
                YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)
            ),
        )
    )

    results = await session.scalars(videos_query)
    videos = results.all()
    videos = [
        YoutubeVideoResponse(
            **video.__dict__,
            channel_title=video.channel.title,
            channel_thumbnail=video.channel.thumbnail,
            category_name=video.category.name,
            watched=video.watches[0].created_at if video.watches else None,
            liked=video.likes[0].created_at if video.likes else None,
            queued=video.queues[0].created_at if video.queues else None,
        )
        for video in videos
    ]

    count_query = select(func.count(query.subquery().columns.id))
    count = await session.scalar(count_query)
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
        .options(
            joinedload(YoutubeVideo.channel),
            joinedload(YoutubeVideo.category),
            selectinload(YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)),
            selectinload(
                YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)
            ),
            selectinload(
                YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)
            ),
        )
    )
    results = await session.scalars(query)
    videos = [result for result in results.all()]

    [prev_video, current_video, next_video] = [None] * 3

    if index != 1 and videos:
        prev_video = videos.pop(0)
    if videos:
        current_video = videos.pop(0)
        current_video = YoutubeVideoResponse(
            **current_video.__dict__,
            channel_title=current_video.channel.title,
            channel_thumbnail=current_video.channel.thumbnail,
            category_name=current_video.category.name,
            watched=(
                current_video.watches[0].created_at if current_video.watches else None
            ),
            liked=current_video.likes[0].created_at if current_video.likes else None,
            queued=current_video.queues[0].created_at if current_video.queues else None,
        )
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
