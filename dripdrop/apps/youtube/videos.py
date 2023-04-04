import traceback
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response, status
from sqlalchemy import select

from dripdrop.dependencies import (
    create_db_session,
    AsyncSession,
    User,
    get_authenticated_user,
)
from dripdrop.logging import logger

from .models import (
    YoutubeVideoCategory,
    YoutubeChannel,
    YoutubeVideo,
    YoutubeSubscription,
    YoutubeVideoQueue,
    YoutubeVideoLike,
    YoutubeVideoWatch,
)
from .responses import (
    ErrorMessages,
    YoutubeVideoCategoriesResponse,
    VideosResponse,
    VideoQueueResponse,
    VideoResponse,
)
from . import utils

videos_api = APIRouter(
    prefix="/videos",
    tags=["YouTube Videos"],
    dependencies=[Depends(get_authenticated_user)],
)


@videos_api.get("/categories", response_model=YoutubeVideoCategoriesResponse)
async def get_youtube_video_categories(
    channel_id: str = Query(None),
    session: AsyncSession = Depends(create_db_session),
    user: User = Depends(get_authenticated_user),
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


@videos_api.get(
    "",
    response_model=VideoResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Could not find Youtube video"}
    },
)
async def get_youtube_video(
    video_id: str = Query(...),
    related_videos_length: int = Query(5, ge=0),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    (videos, *_) = await utils.execute_videos_query(
        session=session,
        user=user,
        video_ids=[video_id],
        subscribed_only=False,
    )
    video = videos[0] if videos else None
    if not video:
        raise HTTPException(404)
    related_videos = []
    if related_videos_length > 0:
        (related_videos, *_) = await utils.execute_videos_query(
            session=session,
            user=user,
            video_categories=[video.category_id],
            limit=related_videos_length,
            exclude_video_ids=[video.id],
            subscribed_only=False,
        )
    return VideoResponse(video=video, related_videos=related_videos)


@videos_api.get(
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
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    video_categories: str = Query(""),
    channel_id: str | None = Query(None),
    liked_only: bool = Query(False),
    queued_only: bool = Query(False),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
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


@videos_api.put(
    "/watch",
    responses={status.HTTP_400_BAD_REQUEST: {}},
)
async def add_youtube_video_watch(
    video_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    results = await session.execute(query)
    video = results.first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    query = select(YoutubeVideoWatch).where(
        YoutubeVideoWatch.email == user.email,
        YoutubeVideoWatch.video_id == video_id,
    )
    results = await session.scalars(query)
    watch = results.first()
    if watch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.ADD_VIDEO_WATCH_ERROR,
        )
    session.add(YoutubeVideoWatch(email=user.email, video_id=video_id))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@videos_api.put(
    "/like",
    responses={status.HTTP_400_BAD_REQUEST: {}},
)
async def add_youtube_video_like(
    video_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    results = await session.execute(query)
    video = results.first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    results = await session.scalars(query)
    like = results.first()
    if like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.ADD_VIDEO_LIKE_ERROR,
        )
    session.add(YoutubeVideoLike(email=user.email, video_id=video_id))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@videos_api.delete(
    "/like",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessages.REMOVE_VIDEO_LIKE_ERROR
        }
    },
)
async def delete_youtube_video_like(
    video_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    results = await session.scalars(query)
    like = results.first()
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.REMOVE_VIDEO_LIKE_ERROR,
        )
    await session.delete(like)
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@videos_api.put(
    "/queue",
    responses={
        status.HTTP_400_BAD_REQUEST: {},
    },
)
async def add_youtube_video_queue(
    video_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    results = await session.scalars(query)
    video = results.first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.video_id == video_id,
        YoutubeVideoQueue.email == user.email,
    )
    results = await session.scalars(query)
    video_queue = results.first()
    if video_queue:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.ADD_VIDEO_QUEUE_ERROR,
        )
    session.add(YoutubeVideoQueue(email=user.email, video_id=video_id))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@videos_api.delete(
    "/queue",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessages.REMOVE_VIDEO_QUEUE_ERROR
        }
    },
)
async def delete_youtube_video_queue(
    video_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.email == user.email,
        YoutubeVideoQueue.video_id == video_id,
    )
    results = await session.scalars(query)
    queue = results.first()
    if not queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.REMOVE_VIDEO_QUEUE_ERROR,
        )
    await session.delete(queue)
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@videos_api.get(
    "/queue",
    response_model=VideoQueueResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_QUEUE_NOT_FOUND}
    },
)
async def get_youtube_video_queue(
    index: int = Query(..., ge=1),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
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
