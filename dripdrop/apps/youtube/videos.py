import math
import traceback
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response, status
from sqlalchemy import select, func

from dripdrop.dependencies import create_db_session, AsyncSession
from dripdrop.logging import logger

from .dependencies import get_google_user, GoogleAccount
from .models import (
    YoutubeVideoCategory,
    YoutubeChannels,
    YoutubeVideos,
    YoutubeSubscriptions,
    YoutubeVideoCategories,
    YoutubeVideoQueues,
    YoutubeVideoLikes,
    YoutubeVideoWatches,
)
from .responses import (
    VideoCategoriesResponse,
    VideosResponse,
    VideoQueueResponse,
    VideoResponse,
)

videos_api = APIRouter(
    prefix="/videos",
    tags=["YouTube Videos"],
    dependencies=[Depends(get_google_user)],
)


@videos_api.get("/categories", response_model=VideoCategoriesResponse)
async def get_youtube_video_categories(
    channel_id: str = Query(None),
    db: AsyncSession = Depends(create_db_session),
):
    channel_query = (
        select(YoutubeChannels)
        .where(
            YoutubeChannels.id == channel_id
            if channel_id
            else YoutubeChannels.id.is_not(None)
        )
        .alias(name=YoutubeChannels.__tablename__)
    )
    query = channel_query.join(
        YoutubeVideos,
        YoutubeVideos.channel_id == channel_query.c.id,
    ).join(
        YoutubeVideoCategories,
        YoutubeVideoCategories.id == YoutubeVideos.category_id,
    )
    results = await db.scalars(
        select(YoutubeVideoCategories)
        .select_from(query)
        .order_by(YoutubeVideoCategories.name.asc())
        .distinct(YoutubeVideoCategories.name)
    )
    categories = list(
        map(
            lambda result: YoutubeVideoCategory.from_orm(result),
            results.all(),
        )
    )
    return VideoCategoriesResponse(categories=categories)


@videos_api.get(
    "/{page}/{per_page}",
    response_model=VideosResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Video Categories must be an integer"
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
    db: AsyncSession = Depends(create_db_session),
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
            detail="Video Categories must be an integer",
        )

    videos_query = (
        select(YoutubeVideos)
        .where(
            YoutubeVideos.category_id.in_(video_categories)
            if len(video_categories) != 0
            else YoutubeVideos.category_id.is_not(None)
        )
        .alias(name=YoutubeVideos.__tablename__)
    )
    video_likes_query = (
        select(YoutubeVideoLikes)
        .where(YoutubeVideoLikes.email == google_account.email)
        .alias(name=YoutubeVideoLikes.__tablename__)
    )
    video_queues_query = (
        select(YoutubeVideoQueues)
        .where(YoutubeVideoQueues.email == google_account.email)
        .alias(name=YoutubeVideoQueues.__tablename__)
    )
    video_watches_query = (
        select(YoutubeVideoWatches)
        .where(YoutubeVideoWatches.email == google_account.email)
        .alias(name=YoutubeVideoWatches.__tablename__)
    )
    channel_query = (
        select(YoutubeChannels)
        .where(
            YoutubeChannels.id == channel_id
            if channel_id
            else YoutubeChannels.id.is_not(None)
        )
        .alias(name=YoutubeChannels.__tablename__)
    )
    subscription_query = (
        select(YoutubeSubscriptions)
        .where(
            YoutubeSubscriptions.email == google_account.email
            if not channel_id
            else YoutubeSubscriptions.id.is_not(None)
        )
        .alias(name=YoutubeSubscriptions.__tablename__)
    )
    query = select(
        videos_query,
        channel_query.c.title.label("channel_title"),
        channel_query.c.thumbnail.label("channel_thumbnail"),
        video_likes_query.c.created_at.label("liked"),
        video_watches_query.c.created_at.label("watched"),
        video_queues_query.c.created_at.label("queued"),
    ).select_from(
        subscription_query.join(
            channel_query,
            channel_query.c.id == YoutubeSubscriptions.channel_id,
        )
        .join(
            videos_query,
            videos_query.c.channel_id == channel_query.c.id,
        )
        .join(
            video_likes_query,
            video_likes_query.c.video_id == videos_query.c.id,
            isouter=not liked_only,
        )
        .join(
            video_queues_query,
            video_queues_query.c.video_id == videos_query.c.id,
            isouter=not queued_only,
        )
        .join(
            video_watches_query,
            video_watches_query.c.video_id == videos_query.c.id,
            isouter=True,
        )
    )
    if liked_only:
        query = query.order_by(video_likes_query.c.created_at.desc())
    elif queued_only:
        query = query.order_by(video_queues_query.c.created_at.asc())
    else:
        query = query.order_by(videos_query.c.published_at.desc())
    results = await db.execute(query.offset((page - 1) * per_page))
    videos = results.mappings().fetchmany(per_page)
    count = await db.scalar(select(func.count(query.c.id)))
    total_pages = math.ceil(count / per_page)
    return VideosResponse(videos=videos, total_pages=total_pages)


@videos_api.put(
    "/watch",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Video not found"}},
)
async def add_youtube_video_watch(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoWatches).where(
        YoutubeVideoWatches.email == google_account.email,
        YoutubeVideoLikes.video_id == video_id,
    )
    results = await db.scalars(query)
    watch = results.first()
    if not watch:
        db.add(YoutubeVideoWatches(email=google_account.email, video_id=video_id))
        await db.commit()
        return Response(None, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


@videos_api.put(
    "/like",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Video not found"}},
)
async def add_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoLikes).where(
        YoutubeVideoLikes.email == google_account.email,
        YoutubeVideoLikes.video_id == video_id,
    )
    results = await db.scalars(query)
    like = results.first()
    if not like:
        db.add(YoutubeVideoLikes(email=google_account.email, video_id=video_id))
        await db.commit()
        return Response(None, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")


@videos_api.delete(
    "/like", responses={404: {"description": "Could not remove video like"}}
)
async def delete_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):

    query = select(YoutubeVideoLikes).where(
        YoutubeVideoLikes.email == google_account.email,
        YoutubeVideoLikes.video_id == video_id,
    )
    results = await db.scalars(query)
    like = results.first()
    if not like:
        raise HTTPException(404)
    await db.delete(like)
    await db.commit()
    return Response(None, 200)


@videos_api.put(
    "/queue", responses={400: {"description": "Could not add video to queue"}}
)
async def add_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoQueues).where(
        YoutubeVideoQueues.email == google_account.email,
        YoutubeVideoQueues.video_id == video_id,
    )
    results = await db.scalars(query)
    queue = results.first()
    if not queue:
        db.add(YoutubeVideoQueues(email=google_account.email, video_id=video_id))
        await db.commit()
        return Response(None, 200)
    raise HTTPException(400)


@videos_api.delete(
    "/queue", responses={404: {"description": "Could not deleted video queue"}}
)
async def delete_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeVideoQueues).where(
        YoutubeVideoQueues.email == google_account.email,
        YoutubeVideoQueues.video_id == video_id,
    )
    results = await db.scalars(query)
    queue = results.first()
    if not queue:
        raise HTTPException(404)
    await db.delete(queue)
    await db.commit()
    return Response(None, 200)


@videos_api.get(
    "/queue",
    response_model=VideoQueueResponse,
    responses={404: {"description": "Video in queue not found"}},
)
async def get_youtube_video_queue(
    index: int = Query(..., ge=1),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    videos_query = select(YoutubeVideos).alias(name=YoutubeVideos.__tablename__)
    video_likes_query = (
        select(YoutubeVideoLikes)
        .where(YoutubeVideoLikes.email == google_account.email)
        .alias(name=YoutubeVideoLikes.__tablename__)
    )
    video_queues_query = (
        select(YoutubeVideoQueues)
        .where(YoutubeVideoQueues.email == google_account.email)
        .offset(max(index - 2, 0))
        .alias(name=YoutubeVideoQueues.__tablename__)
    )
    video_watches_query = (
        select(YoutubeVideoWatches)
        .where(YoutubeVideoWatches.email == google_account.email)
        .alias(name=YoutubeVideoWatches.__tablename__)
    )
    channel_query = select(YoutubeChannels).alias(name=YoutubeChannels.__tablename__)
    query = (
        select(
            videos_query,
            channel_query.c.title.label("channel_title"),
            channel_query.c.thumbnail.label("channel_thumbnail"),
            video_likes_query.c.created_at.label("liked"),
            video_watches_query.c.created_at.label("watched"),
            video_queues_query.c.created_at.label("queued"),
        )
        .select_from(
            video_queues_query.join(
                videos_query,
                video_queues_query.c.video_id == videos_query.c.id,
            )
            .join(
                channel_query,
                channel_query.c.id == videos_query.c.channel_id,
            )
            .join(
                video_likes_query,
                video_likes_query.c.video_id == videos_query.c.id,
                isouter=True,
            )
            .join(
                video_watches_query,
                video_watches_query.c.video_id == videos_query.c.id,
                isouter=True,
            )
        )
        .order_by(video_queues_query.c.created_at.asc())
    )
    results = await db.execute(query)
    videos = results.mappings().fetchmany(2 if index == 1 else 3)
    [prev_video, current_video, next_video] = [None] * 3
    if index != 1 and videos:
        prev_video = videos.pop(0)
    if videos:
        current_video = videos.pop(0)
    if videos:
        next_video = videos.pop(0)
    if not current_video:
        raise HTTPException(404)
    return VideoQueueResponse(
        current_video=current_video, prev=bool(prev_video), next=bool(next_video)
    )


@videos_api.get(
    "",
    dependencies=[Depends(get_google_user)],
    response_model=VideoResponse,
    responses={404: {"description": "Could not find Youtube video"}},
)
async def get_youtube_video(
    video_id: str = Query(...),
    related_videos_length: int = Query(5, ge=0),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    videos_query = (
        select(YoutubeVideos)
        .where(YoutubeVideos.id == video_id)
        .alias(name=YoutubeVideos.__tablename__)
    )
    video_likes_query = (
        select(YoutubeVideoLikes)
        .where(YoutubeVideoLikes.email == google_account.email)
        .alias(name=YoutubeVideoLikes.__tablename__)
    )
    video_queues_query = (
        select(YoutubeVideoQueues)
        .where(YoutubeVideoQueues.email == google_account.email)
        .alias(name=YoutubeVideoQueues.__tablename__)
    )
    video_watches_query = (
        select(YoutubeVideoWatches)
        .where(YoutubeVideoWatches.email == google_account.email)
        .alias(name=YoutubeVideoWatches.__tablename__)
    )
    channel_query = select(YoutubeChannels).alias(name=YoutubeChannels.__tablename__)
    query = select(
        videos_query,
        channel_query.c.title.label("channel_title"),
        channel_query.c.thumbnail.label("channel_thumbnail"),
        video_likes_query.c.created_at.label("liked"),
        video_watches_query.c.created_at.label("watched"),
        video_queues_query.c.created_at.label("queued"),
    ).select_from(
        videos_query.join(
            channel_query,
            channel_query.c.id == videos_query.c.channel_id,
        )
        .join(
            video_queues_query,
            video_queues_query.c.video_id == videos_query.c.id,
            isouter=True,
        )
        .join(
            video_likes_query,
            video_likes_query.c.video_id == videos_query.c.id,
            isouter=True,
        )
        .join(
            video_watches_query,
            video_watches_query.c.video_id == videos_query.c.id,
            isouter=True,
        )
    )
    results = await db.execute(query)
    video = results.mappings().first()
    if not video:
        raise HTTPException(404)
    related_videos = []
    if related_videos_length > 0:
        videos_query = (
            select(YoutubeVideos)
            .where(
                YoutubeVideos.id != video.id,
                (YoutubeVideos.category_id == video.category_id)
                | (YoutubeVideos.channel_id == video.channel_id),
            )
            .alias(name=YoutubeVideos.__tablename__)
        )
        query = (
            select(
                videos_query,
                channel_query.c.title.label("channel_title"),
                channel_query.c.thumbnail.label("channel_thumbnail"),
                video_likes_query.c.created_at.label("liked"),
                video_watches_query.c.created_at.label("watched"),
                video_queues_query.c.created_at.label("queued"),
            )
            .select_from(
                videos_query.join(
                    channel_query,
                    channel_query.c.id == videos_query.c.channel_id,
                )
                .join(
                    video_queues_query,
                    video_queues_query.c.video_id == videos_query.c.id,
                    isouter=True,
                )
                .join(
                    video_likes_query,
                    video_likes_query.c.video_id == videos_query.c.id,
                    isouter=True,
                )
                .join(
                    video_watches_query,
                    video_watches_query.c.video_id == videos_query.c.id,
                    isouter=True,
                )
            )
            .order_by(videos_query.c.published_at.desc())
        )
        results = await db.execute(query)
        related_videos = results.mappings().fetchmany(related_videos_length)
    return VideoResponse(video=video, related_videos=related_videos)
