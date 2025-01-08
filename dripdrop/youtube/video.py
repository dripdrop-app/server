from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.youtube.models import (
    YoutubeVideo,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)
from dripdrop.youtube.responses import (
    ErrorMessages,
    VideoResponse,
    YoutubeVideoResponse,
)

api = APIRouter(
    prefix="/video/{video_id}",
    tags=["Youtube Video"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.get(
    "",
    response_model=VideoResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_NOT_FOUND}
    },
)
async def get_youtube_video(
    user: AuthenticatedUser,
    session: DatabaseSession,
    video_id: str = Path(...),
    related_videos_length: int = Query(5, ge=0),
):
    query = (
        select(YoutubeVideo)
        .where(YoutubeVideo.id == video_id)
        .options(
            joinedload(YoutubeVideo.channel),
            joinedload(YoutubeVideo.category),
            selectinload(YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)),
            selectinload(
                YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)
            ),
            selectinload(
                YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)
            ),
        )
    )
    video = await session.scalar(query)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    video = YoutubeVideoResponse(
        **video.__dict__,
        channel_title=video.channel.title,
        channel_thumbnail=video.channel.thumbnail,
        category_name=video.category.name,
        watched=video.watches[0].created_at if video.watches else None,
        liked=video.likes[0].created_at if video.likes else None,
        queued=video.queues[0].created_at if video.queues else None,
    )
    related_videos = []
    if related_videos_length > 0:
        query = (
            select(YoutubeVideo)
            .where(
                YoutubeVideo.id != video.id,
                YoutubeVideo.category_id == video.category_id,
            )
            .order_by(YoutubeVideo.published_at.desc())
            .limit(related_videos_length)
            .options(
                joinedload(YoutubeVideo.channel),
                joinedload(YoutubeVideo.category),
                selectinload(
                    YoutubeVideo.likes.and_(YoutubeVideoLike.email == user.email)
                ),
                selectinload(
                    YoutubeVideo.watches.and_(YoutubeVideoWatch.email == user.email)
                ),
                selectinload(
                    YoutubeVideo.queues.and_(YoutubeVideoQueue.email == user.email)
                ),
            )
        )
        results = await session.scalars(query)
        related_videos = results.all()
        related_videos = [
            YoutubeVideoResponse(
                **video.__dict__,
                channel_title=video.channel.title,
                channel_thumbnail=video.channel.thumbnail,
                category_name=video.category.name,
                watched=video.watches[0].created_at if video.watches else None,
                liked=video.likes[0].created_at if video.likes else None,
                queued=video.queues[0].created_at if video.queues else None,
            )
            for video in related_videos
        ]
    return VideoResponse(video=video, related_videos=related_videos)


@api.put(
    "/watch",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_NOT_FOUND},
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.ADD_VIDEO_WATCH_ERROR
        },
    },
)
async def add_youtube_video_watch(
    user: AuthenticatedUser, session: DatabaseSession, video_id: str = Path(...)
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    video = await session.scalar(query)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    query = select(YoutubeVideoWatch).where(
        YoutubeVideoWatch.email == user.email,
        YoutubeVideoWatch.video_id == video_id,
    )
    watch = await session.scalar(query)
    if watch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.ADD_VIDEO_WATCH_ERROR,
        )
    session.add(YoutubeVideoWatch(email=user.email, video_id=video_id))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@api.put(
    "/like",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_NOT_FOUND},
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.ADD_VIDEO_LIKE_ERROR
        },
    },
)
async def add_youtube_video_like(
    user: AuthenticatedUser, session: DatabaseSession, video_id: str = Path(...)
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    video = await session.scalar(query)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    like = await session.scalar(query)
    if like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.ADD_VIDEO_LIKE_ERROR,
        )
    session.add(YoutubeVideoLike(email=user.email, video_id=video_id))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@api.delete(
    "/like",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessages.REMOVE_VIDEO_LIKE_ERROR
        }
    },
)
async def delete_youtube_video_like(
    user: AuthenticatedUser, session: DatabaseSession, video_id: str = Path(...)
):
    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.email == user.email,
        YoutubeVideoLike.video_id == video_id,
    )
    like = await session.scalar(query)
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.REMOVE_VIDEO_LIKE_ERROR,
        )
    await session.delete(like)
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@api.put(
    "/queue",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.VIDEO_NOT_FOUND},
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.ADD_VIDEO_QUEUE_ERROR
        },
    },
)
async def add_youtube_video_queue(
    user: AuthenticatedUser, session: DatabaseSession, video_id: str = Path(...)
):
    query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
    video = await session.scalar(query)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.video_id == video_id,
        YoutubeVideoQueue.email == user.email,
    )
    video_queue = await session.scalar(query)
    if video_queue:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.ADD_VIDEO_QUEUE_ERROR,
        )
    session.add(YoutubeVideoQueue(email=user.email, video_id=video_id))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)


@api.delete(
    "/queue",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": ErrorMessages.REMOVE_VIDEO_QUEUE_ERROR
        }
    },
)
async def delete_youtube_video_queue(
    user: AuthenticatedUser, session: DatabaseSession, video_id: str = Path(...)
):
    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.email == user.email,
        YoutubeVideoQueue.video_id == video_id,
    )
    queue = await session.scalar(query)
    if not queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.REMOVE_VIDEO_QUEUE_ERROR,
        )
    await session.delete(queue)
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)
