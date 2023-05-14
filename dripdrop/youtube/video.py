from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response, status
from sqlalchemy import select

from dripdrop.authentication.dependencies import (
    get_authenticated_user,
    AuthenticatedUser,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.youtube import utils
from dripdrop.youtube.models import (
    YoutubeVideo,
    YoutubeVideoQueue,
    YoutubeVideoLike,
    YoutubeVideoWatch,
)
from dripdrop.youtube.responses import ErrorMessages, VideoResponse

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
    (videos, *_) = await utils.execute_videos_query(
        session=session,
        user=user,
        video_ids=[video_id],
        subscribed_only=False,
    )
    video = videos[0] if videos else None
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.VIDEO_NOT_FOUND,
        )
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
    results = await session.execute(query)
    video = results.first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
    results = await session.execute(query)
    video = results.first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
    results = await session.scalars(query)
    video = results.first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
