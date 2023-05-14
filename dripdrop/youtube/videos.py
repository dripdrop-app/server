import traceback
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy import select

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
    videos, total_pages = await utils.execute_videos_query(
        session=session,
        user=user,
        channel_id=channel_id,
        video_categories=video_categories,
        liked_only=liked_only,
        queued_only=queued_only,
        offset=(page - 1) * per_page,
        limit=per_page,
        subscribed_only=channel_id is None and not liked_only and not queued_only,
    )
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
    (videos, *_) = await utils.execute_videos_query(
        session=session,
        user=user,
        queued_only=True,
        offset=max(index - 2, 0),
        limit=2 if index == 1 else 3,
        subscribed_only=False,
    )

    [prev_video, current_video, next_video] = [None] * 3

    if index != 1 and videos:
        prev_video = videos.pop(0)
    if videos:
        current_video = videos.pop(0)
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
