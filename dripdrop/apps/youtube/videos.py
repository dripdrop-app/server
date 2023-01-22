import math
import traceback
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response, status
from sqlalchemy import select, func

from dripdrop.dependencies import create_db_session, AsyncSession
from dripdrop.logging import logger

from .dependencies import get_google_user, GoogleAccount
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

videos_api = APIRouter(
    prefix="/videos",
    tags=["YouTube Videos"],
    dependencies=[Depends(get_google_user)],
)


@videos_api.get("/categories", response_model=YoutubeVideoCategoriesResponse)
async def get_youtube_video_categories(
    channel_id: str = Query(None),
    session: AsyncSession = Depends(create_db_session),
):
    channel_query = (
        select(YoutubeChannel)
        .where(
            YoutubeChannel.id == channel_id
            if channel_id
            else YoutubeChannel.id.is_not(None)
        )
        .alias(name=YoutubeChannel.__tablename__)
    )
    query = channel_query.join(
        YoutubeVideo,
        YoutubeVideo.channel_id == channel_query.columns.id,
    ).join(
        YoutubeVideoCategory,
        YoutubeVideoCategory.id == YoutubeVideo.category_id,
    )
    results = await session.scalars(
        select(YoutubeVideoCategory)
        .select_from(query)
        .order_by(YoutubeVideoCategory.name.asc())
        .distinct(YoutubeVideoCategory.name)
    )
    categories: list[YoutubeVideoCategory] = results.all()
    return YoutubeVideoCategoriesResponse(categories=categories)


@videos_api.get(
    "/{page}/{per_page}",
    response_model=VideosResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.VIDEO_CATEGORIES_INVALID
        }
    },
)
async def get_youtube_videos(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    video_categories: str = Query(""),
    channel_id: str = Query(None),
    liked_only: bool = Query(False),
    queued_only: bool = Query(False),
    google_account: GoogleAccount = Depends(get_google_user),
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

    videos_query = (
        select(YoutubeVideo)
        .where(
            YoutubeVideo.category_id.in_(video_categories)
            if len(video_categories) != 0
            else YoutubeVideo.category_id.is_not(None)
        )
        .alias(name=YoutubeVideo.__tablename__)
    )
    video_likes_query = (
        select(YoutubeVideoLike)
        .where(YoutubeVideoLike.email == google_account.email)
        .alias(name=YoutubeVideoLike.__tablename__)
    )
    video_queues_query = (
        select(YoutubeVideoQueue)
        .where(YoutubeVideoQueue.email == google_account.email)
        .alias(name=YoutubeVideoQueue.__tablename__)
    )
    video_watches_query = (
        select(YoutubeVideoWatch)
        .where(YoutubeVideoWatch.email == google_account.email)
        .alias(name=YoutubeVideoWatch.__tablename__)
    )
    channel_query = (
        select(YoutubeChannel)
        .where(
            YoutubeChannel.id == channel_id
            if channel_id
            else YoutubeChannel.id.is_not(None)
        )
        .alias(name=YoutubeChannel.__tablename__)
    )
    subscription_query = (
        select(YoutubeSubscription)
        .where(
            YoutubeSubscription.email == google_account.email
            if not channel_id
            else YoutubeSubscription.id.is_not(None)
        )
        .alias(name=YoutubeSubscription.__tablename__)
    )
    query = select(
        videos_query,
        channel_query.columns.title.label("channel_title"),
        channel_query.columns.thumbnail.label("channel_thumbnail"),
        video_likes_query.columns.created_at.label("liked"),
        video_watches_query.columns.created_at.label("watched"),
        video_queues_query.columns.created_at.label("queued"),
    ).select_from(
        subscription_query.join(
            channel_query,
            channel_query.columns.id == YoutubeSubscription.channel_id,
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
    results = await session.execute(query.offset((page - 1) * per_page))
    videos = results.mappings().fetchmany(per_page)
    count = await session.scalar(select(func.count(query.columns.id)))
    total_pages = math.ceil(count / per_page)
    return VideosResponse(videos=videos, total_pages=total_pages)


@videos_api.put(
    "/watch",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_NOT_FOUND}
    },
)
async def add_youtube_video_watch(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoWatch).where(
        YoutubeVideoWatch.email == google_account.email,
        YoutubeVideoLike.video_id == video_id,
    )
    results = await session.scalars(query)
    watch = results.first()
    if not watch:
        session.add(YoutubeVideoWatch(email=google_account.email, video_id=video_id))
        await session.commit()
        return Response(None, status_code=status.HTTP_200_OK)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.VIDEO_NOT_FOUND
    )


@videos_api.put(
    "/like",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_NOT_FOUND}
    },
)
async def add_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == google_account.email,
        YoutubeVideoLike.video_id == video_id,
    )
    results = await session.scalars(query)
    like = results.first()
    if not like:
        session.add(YoutubeVideoLike(email=google_account.email, video_id=video_id))
        await session.commit()
        return Response(None, status_code=status.HTTP_200_OK)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=ErrorMessages.VIDEO_NOT_FOUND
    )


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
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):

    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == google_account.email,
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
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.ADD_VIDEO_QUEUE_ERROR
        }
    },
)
async def add_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.email == google_account.email,
        YoutubeVideoQueue.video_id == video_id,
    )
    results = await session.scalars(query)
    queue = results.first()
    if not queue:
        session.add(YoutubeVideoQueue(email=google_account.email, video_id=video_id))
        await session.commit()
        return Response(None, status_code=status.HTTP_200_OK)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=ErrorMessages.ADD_VIDEO_QUEUE_ERROR,
    )


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
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.email == google_account.email,
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
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):
    videos_query = select(YoutubeVideo).alias(name=YoutubeVideo.__tablename__)
    video_likes_query = (
        select(YoutubeVideoLike)
        .where(YoutubeVideoLike.email == google_account.email)
        .alias(name=YoutubeVideoLike.__tablename__)
    )
    video_queues_query = (
        select(YoutubeVideoQueue)
        .where(YoutubeVideoQueue.email == google_account.email)
        .offset(max(index - 2, 0))
        .alias(name=YoutubeVideoQueue.__tablename__)
    )
    video_watches_query = (
        select(YoutubeVideoWatch)
        .where(YoutubeVideoWatch.email == google_account.email)
        .alias(name=YoutubeVideoWatch.__tablename__)
    )
    channel_query = select(YoutubeChannel).alias(name=YoutubeChannel.__tablename__)
    query = (
        select(
            videos_query,
            channel_query.columns.title.label("channel_title"),
            channel_query.columns.thumbnail.label("channel_thumbnail"),
            video_likes_query.columns.created_at.label("liked"),
            video_watches_query.columns.created_at.label("watched"),
            video_queues_query.columns.created_at.label("queued"),
        )
        .select_from(
            video_queues_query.join(
                videos_query,
                video_queues_query.columns.video_id == videos_query.columns.id,
            )
            .join(
                channel_query,
                channel_query.columns.id == videos_query.columns.channel_id,
            )
            .join(
                video_likes_query,
                video_likes_query.columns.video_id == videos_query.columns.id,
                isouter=True,
            )
            .join(
                video_watches_query,
                video_watches_query.columns.video_id == videos_query.columns.id,
                isouter=True,
            )
        )
        .order_by(video_queues_query.columns.created_at.asc())
    )
    results = await session.execute(query)
    videos = results.mappings().fetchmany(2 if index == 1 else 3)
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


@videos_api.get(
    "",
    dependencies=[Depends(get_google_user)],
    response_model=VideoResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Could not find Youtube video"}
    },
)
async def get_youtube_video(
    video_id: str = Query(...),
    related_videos_length: int = Query(5, ge=0),
    google_account: GoogleAccount = Depends(get_google_user),
    session: AsyncSession = Depends(create_db_session),
):
    videos_query = (
        select(YoutubeVideo)
        .where(YoutubeVideo.id == video_id)
        .alias(name=YoutubeVideo.__tablename__)
    )
    video_likes_query = (
        select(YoutubeVideoLike)
        .where(YoutubeVideoLike.email == google_account.email)
        .alias(name=YoutubeVideoLike.__tablename__)
    )
    video_queues_query = (
        select(YoutubeVideoQueue)
        .where(YoutubeVideoQueue.email == google_account.email)
        .alias(name=YoutubeVideoQueue.__tablename__)
    )
    video_watches_query = (
        select(YoutubeVideoWatch)
        .where(YoutubeVideoWatch.email == google_account.email)
        .alias(name=YoutubeVideoWatch.__tablename__)
    )
    channel_query = select(YoutubeChannel).alias(name=YoutubeChannel.__tablename__)
    query = select(
        videos_query,
        channel_query.columns.title.label("channel_title"),
        channel_query.columns.thumbnail.label("channel_thumbnail"),
        video_likes_query.columns.created_at.label("liked"),
        video_watches_query.columns.created_at.label("watched"),
        video_queues_query.columns.created_at.label("queued"),
    ).select_from(
        videos_query.join(
            channel_query,
            channel_query.columns.id == videos_query.columns.channel_id,
        )
        .join(
            video_queues_query,
            video_queues_query.columns.video_id == videos_query.columns.id,
            isouter=True,
        )
        .join(
            video_likes_query,
            video_likes_query.columns.video_id == videos_query.columns.id,
            isouter=True,
        )
        .join(
            video_watches_query,
            video_watches_query.columns.video_id == videos_query.columns.id,
            isouter=True,
        )
    )
    results = await session.execute(query)
    video = results.mappings().first()
    if not video:
        raise HTTPException(404)
    related_videos = []
    if related_videos_length > 0:
        videos_query = (
            select(YoutubeVideo)
            .where(
                YoutubeVideo.id != video.id,
                (YoutubeVideo.category_id == video.category_id)
                | (YoutubeVideo.channel_id == video.channel_id),
            )
            .alias(name=YoutubeVideo.__tablename__)
        )
        query = (
            select(
                videos_query,
                channel_query.columns.title.label("channel_title"),
                channel_query.columns.thumbnail.label("channel_thumbnail"),
                video_likes_query.columns.created_at.label("liked"),
                video_watches_query.columns.created_at.label("watched"),
                video_queues_query.columns.created_at.label("queued"),
            )
            .select_from(
                videos_query.join(
                    channel_query,
                    channel_query.columns.id == videos_query.columns.channel_id,
                )
                .join(
                    video_queues_query,
                    video_queues_query.columns.video_id == videos_query.columns.id,
                    isouter=True,
                )
                .join(
                    video_likes_query,
                    video_likes_query.columns.video_id == videos_query.columns.id,
                    isouter=True,
                )
                .join(
                    video_watches_query,
                    video_watches_query.columns.video_id == videos_query.columns.id,
                    isouter=True,
                )
            )
            .order_by(videos_query.columns.published_at.desc())
        )
        results = await session.execute(query)
        related_videos = results.mappings().fetchmany(related_videos_length)
    return VideoResponse(video=video, related_videos=related_videos)
