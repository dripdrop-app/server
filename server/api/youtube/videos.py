import math
from fastapi import APIRouter, Depends, Query, Path, HTTPException, Response
from server.dependencies import (
    get_google_user,
    create_db_session,
    DBSession,
    GoogleAccount,
)
from server.models.api import (
    YoutubeResponses,
    YoutubeVideoCategory,
)
from server.models.orm import (
    YoutubeChannels,
    YoutubeVideos,
    YoutubeSubscriptions,
    YoutubeVideoCategories,
    YoutubeVideoQueues,
    YoutubeVideoLikes,
    YoutubeVideoWatches,
)
from sqlalchemy import select, func

youtube_videos_api = APIRouter(
    prefix="/videos",
    tags=["YouTube Videos"],
    dependencies=[Depends(get_google_user)],
    responses={401: {}},
)


@youtube_videos_api.get("/categories", response_model=YoutubeResponses.VideoCategories)
async def get_youtube_video_categories(
    channel_id: str = Query(None),
    db: DBSession = Depends(create_db_session),
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
    return YoutubeResponses.VideoCategories(categories=categories).dict(by_alias=True)


@youtube_videos_api.get("/{page}/{per_page}", response_model=YoutubeResponses.Videos)
async def get_youtube_videos(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    video_categories: list[int] = Query([]),
    channel_id: str = Query(None),
    liked_only: bool = Query(False),
    queued_only: bool = Query(False),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
):
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
        .where(YoutubeSubscriptions.email == google_account.email)
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
    return YoutubeResponses.Videos(videos=videos, total_pages=total_pages).dict(
        by_alias=True
    )


@youtube_videos_api.put("/watch")
async def add_youtube_video_watch(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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
        return Response(None, 200)
    raise HTTPException(400)


@youtube_videos_api.put("/like")
async def add_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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
        return Response(None, 200)
    raise HTTPException(400)


@youtube_videos_api.delete("/like", responses={404: {}})
async def delete_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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


@youtube_videos_api.put("/queue", responses={400: {}})
async def add_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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


@youtube_videos_api.delete("/queue", responses={404: {}})
async def delete_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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


@youtube_videos_api.get(
    "/queue",
    response_model=YoutubeResponses.VideoQueue,
    responses={404: {}},
)
async def get_youtube_video_queue(
    index: int = Query(..., ge=1),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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
        .offset(min(index - 1, 0))
        .order(YoutubeVideoQueues.created_at.asc())
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
    results = await db.execute(query)
    videos = results.mappings().fetchmany(2 if index - 1 == 0 else 3)
    [prev_video, current_video, next_video] = (
        [None, *videos] if index - 1 == 0 else videos
    )
    if not current_video:
        raise HTTPException(404)
    return YoutubeResponses.VideoQueue(
        current_video=current_video,
        prev=bool(prev_video),
        next=bool(next_video),
    ).dict(by_alias=True)


@youtube_videos_api.get(
    "",
    dependencies=[Depends(get_google_user)],
    response_model=YoutubeResponses.Video,
    responses={404: {}},
)
async def get_youtube_video(
    video_id: str = Query(...),
    related_videos_length: int = Query(5, ge=0),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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
            .order_by(YoutubeVideos.published_at.desc())
            .alias(name=YoutubeVideos.__tablename__)
        )
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
        related_videos = results.mappings().fetchmany(related_videos_length)
    return YoutubeResponses.Video(video=video, related_videos=related_videos).dict(
        by_alias=True
    )
