import asyncio
import logging
import server.utils.google_api as google_api
from asgiref.sync import sync_to_async
from asyncpg import UniqueViolationError
from fastapi import FastAPI, Depends, HTTPException, Query, Path, Response, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from server.config import config
from server.dependencies import get_authenticated_user, get_google_user
from server.models.main import (
    db,
    YoutubeVideoWatches,
    YoutubeVideoQueue,
    Users,
    YoutubeVideo,
    YoutubeVideoLikes,
    YoutubeVideoQueues,
    YoutubeChannel,
    GoogleAccount,
    GoogleAccounts,
    YoutubeSubscriptions,
    YoutubeChannels,
    YoutubeVideos,
    YoutubeVideoCategories,
    User,
)
from server.models.api import (
    YoutubeResponses,
    YoutubeSubscriptionResponse,
    YoutubeVideoCategoryResponse,
    YoutubeVideoResponse,
)
from server.rq import queue
from server.tasks.youtube import (
    update_google_access_token,
    update_user_youtube_subscriptions_job,
    update_youtube_video_categories,
)
from sqlalchemy import insert, select, update, delete
from typing import List

app = FastAPI(dependencies=[Depends(get_authenticated_user)], responses={401: {}})


async def get_related_info_for_video(
    video: YoutubeVideo, google_account: GoogleAccount
):
    video_query = (
        select(YoutubeVideos)
        .where(YoutubeVideos.id == video.id)
        .alias(name="youtube_videos")
    )
    video_like_query = (
        select(YoutubeVideoLikes)
        .where(YoutubeVideoLikes.email == google_account.email)
        .alias(name="youtube_video_likes")
    )
    video_queue_query = (
        select(YoutubeVideoQueues)
        .where(YoutubeVideoQueues.email == google_account.email)
        .alias(name="youtube_video_queues")
    )
    video_watch_query = (
        select(YoutubeVideoWatches)
        .where(YoutubeVideoWatches.email == google_account.email)
        .alias(name="youtube_video_watches")
    )
    query = (
        video_query.join(
            YoutubeChannels, YoutubeChannels.id == video_query.c.channel_id
        )
        .join(
            video_like_query,
            video_like_query.c.video_id == video_query.c.id,
            isouter=True,
        )
        .join(
            video_queue_query,
            video_queue_query.c.video_id == video_query.c.id,
            isouter=True,
        )
        .join(
            video_watch_query,
            video_watch_query.c.video_id == video_query.c.id,
            isouter=True,
        )
    )
    query = select(
        video_query,
        YoutubeChannels.title.label("channel_title"),
        video_like_query.c.created_at.label("liked"),
        video_queue_query.c.created_at.label("queued"),
        video_watch_query.c.created_at.label("watched"),
    ).select_from(query)
    row = await db.fetch_one(query)
    return YoutubeVideoResponse.parse_obj(row)


@app.get(
    "/googleoauth2", dependencies=[Depends(get_authenticated_user)], responses={401: {}}
)
async def google_oauth2(
    request: Request,
    state: str = Query(...),
    code: str = Query(...),
    error: str = Query(None),
):
    if error:
        raise HTTPException(400)
    email = state
    query = select(Users).where(Users.email == email)
    user = await db.fetch_one(query)
    if not user:
        return RedirectResponse("/")
    get_oauth_tokens = sync_to_async(google_api.get_oauth_tokens)
    tokens = await get_oauth_tokens(f"{request.base_url}api/youtube/googleoauth2", code)
    if tokens:
        get_user_email = sync_to_async(google_api.get_user_email)
        google_email = await get_user_email(tokens.get("access_token"))
        if google_email:
            try:
                query = insert(GoogleAccounts).values(
                    email=google_email,
                    user_email=email,
                    access_token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"],
                    expires=tokens["expires_in"],
                )
                await db.execute(query)
            except UniqueViolationError:
                query = (
                    update(GoogleAccounts)
                    .values(
                        access_token=tokens["access_token"],
                        refresh_token=tokens["refresh_token"],
                        expires=tokens["expires_in"],
                    )
                    .where(GoogleAccounts.email == google_email)
                )
                await db.execute(query)
            except Exception:
                return RedirectResponse("/youtube/videos")
            job = queue.enqueue(update_youtube_video_categories, False)
            queue.enqueue_call(
                update_user_youtube_subscriptions_job,
                args=(email,),
                depends_on=job,
            )
    else:
        logging.warning("Could not retrieve tokens")
    return RedirectResponse("/youtube/videos")


@app.get("/account", response_model=YoutubeResponses.Account)
async def get_youtube_account(
    google_account: GoogleAccount = Depends(get_google_user),
):
    access_token = google_account.access_token
    if config.env == "production":
        new_access_token = await update_google_access_token(google_account.email, db=db)
        if new_access_token != access_token:
            access_token = new_access_token
            query = (
                update(GoogleAccounts)
                .values(
                    access_token=new_access_token,
                )
                .where(GoogleAccounts.email == google_account.email)
            )
            await db.execute(query)
    return YoutubeResponses.Account(
        email=google_account.email, refresh=not bool(access_token)
    ).dict(by_alias=True)


@app.get("/oauth", response_class=PlainTextResponse)
async def create_oauth_link(
    request: Request, user: User = Depends(get_authenticated_user)
):
    oauth = google_api.create_oauth_url(
        f"{request.base_url}api/youtube/googleoauth2", user.email
    )
    return PlainTextResponse(oauth["url"])


@app.get("/videos/categories", response_model=YoutubeResponses.VideoCategories)
async def get_youtube_video_categories(
    google_account: GoogleAccount = Depends(get_google_user),
    channel_id: str = Query(None),
):
    channel_subquery = select(YoutubeChannels)
    if channel_id:
        channel_subquery = channel_subquery.where(YoutubeChannels.id == channel_id)
    channel_subquery = channel_subquery.alias(name="youtube_channels")
    if channel_id:
        query = channel_subquery.join(
            YoutubeVideos, YoutubeVideos.channel_id == channel_subquery.c.id
        )
    else:
        query = (
            select(YoutubeSubscriptions)
            .where(YoutubeSubscriptions.email == google_account.email)
            .alias(name="youtube_subscriptions")
            .join(
                channel_subquery,
                channel_subquery.c.id == YoutubeSubscriptions.channel_id,
            )
            .join(YoutubeVideos, YoutubeVideos.channel_id == channel_subquery.c.id)
        )
    query = query.join(
        YoutubeVideoCategories, YoutubeVideoCategories.id == YoutubeVideos.category_id
    )
    query = (
        select(YoutubeVideoCategories)
        .select_from(query)
        .distinct(YoutubeVideoCategories.id)
    )
    categories = [
        YoutubeVideoCategoryResponse.parse_obj(row)
        async for row in await db.iterate(query)
    ]
    return YoutubeResponses.VideoCategories(categories=categories).dict(by_alias=True)


@app.get("/videos/{page}/{per_page}", response_model=YoutubeResponses.Videos)
async def get_youtube_videos(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
    video_categories: List[int] = Query([]),
    channel_id: str = Query(None),
    liked_only: bool = Query(False),
    queued_only: bool = Query(False),
    google_account: GoogleAccount = Depends(get_google_user),
):
    videos_query = select(YoutubeVideos)
    if video_categories:
        videos_query = videos_query.where(
            YoutubeVideos.category_id.in_(video_categories)
        )
    if channel_id:
        videos_query = videos_query.where(YoutubeVideos.channel_id == channel_id)
    videos_query = videos_query.alias(name="youtube_videos")
    video_likes_query = (
        select(YoutubeVideoLikes)
        .where(YoutubeVideoLikes.email == google_account.email)
        .alias(name="youtube_video_likes")
    )
    video_queues_query = (
        select(YoutubeVideoQueues)
        .where(YoutubeVideoQueues.email == google_account.email)
        .alias(name="youtube_video_queues")
    )
    video_watches_query = (
        select(YoutubeVideoWatches)
        .where(YoutubeVideoWatches.email == google_account.email)
        .alias(name="youtube_video_watches")
    )
    channel_query = select(YoutubeChannels)
    if channel_id:
        channel_query = channel_query.where(YoutubeChannels.id == channel_id)
    channel_query = channel_query.alias(name="youtube_channels")
    query = (
        select(YoutubeSubscriptions)
        .where(YoutubeSubscriptions.email == google_account.email)
        .alias(name="youtube_subscriptions")
        .join(
            videos_query,
            videos_query.c.channel_id == YoutubeSubscriptions.channel_id,
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
        .join(channel_query, channel_query.c.id == videos_query.c.channel_id)
    )
    query = select(
        videos_query,
        channel_query.c.title.label("channel_title"),
        video_likes_query.c.created_at.label("liked"),
        video_queues_query.c.created_at.label("queued"),
        video_watches_query.c.created_at.label("watched"),
    ).select_from(query)
    if liked_only:
        query = query.order_by(video_likes_query.c.created_at.asc())
    elif queued_only:
        query = query.order_by(video_queues_query.c.created_at.asc())
    else:
        query = query.order_by(videos_query.c.published_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    videos = [YoutubeVideoResponse.parse_obj(row) for row in await db.fetch_all(query)]
    return YoutubeResponses.Videos(videos=videos).dict(by_alias=True)


@app.put("/videos/watch")
async def add_youtube_video_watch(
    video_id: str = Query(...), google_account: GoogleAccount = Depends(get_google_user)
):
    try:
        query = insert(YoutubeVideoWatches).values(
            email=google_account.email,
            video_id=video_id,
        )
        await db.execute(query)
    except UniqueViolationError:
        raise HTTPException(400)
    return Response(None, 200)


@app.put("/videos/like")
async def add_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
):
    try:
        query = insert(YoutubeVideoLikes).values(
            email=google_account.email,
            video_id=video_id,
        )
        await db.execute(query)
    except UniqueViolationError:
        raise HTTPException(400)
    return Response(None, 200)


@app.delete("/videos/like")
async def delete_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
):
    query = delete(YoutubeVideoLikes).where(
        YoutubeVideoLikes.email == google_account.email,
        YoutubeVideoLikes.video_id == video_id,
    )
    await db.execute(query)
    return Response(None, 200)


@app.put("/videos/queue")
async def add_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
):
    try:
        query = insert(YoutubeVideoQueues).values(
            email=google_account.email,
            video_id=video_id,
        )
        await db.execute(query)
    except UniqueViolationError:
        raise HTTPException(400)
    return Response(None, 200)


@app.delete("/videos/queue")
async def delete_youtube_video_queue(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
):
    query = delete(YoutubeVideoQueues).where(
        YoutubeVideoQueues.email == google_account.email
    )
    if video_id:
        query = query.where(YoutubeVideoQueues.video_id == video_id)
    await db.execute(query)
    return Response(None, 200)


@app.get("/videos/queue", response_model=YoutubeResponses.VideoQueue)
async def get_youtube_video_queue(
    index: int = Query(..., ge=1),
    google_account: GoogleAccount = Depends(get_google_user),
):
    async def get_video_queue(index):
        query = (
            select(YoutubeVideoQueues)
            .where(YoutubeVideoQueues.email == google_account.email)
            .offset(index)
        )
        video_queue = await db.fetch_one(query)
        if not video_queue:
            return None
        video_queue = YoutubeVideoQueue.parse_obj(video_queue)

        query = select(YoutubeVideos).where(YoutubeVideos.id == video_queue.video_id)
        video = YoutubeVideo.parse_obj(await db.fetch_one(query))
        return await get_related_info_for_video(video, google_account)

    index = index - 1
    current_video = await get_video_queue(index)
    if not current_video:
        raise HTTPException(404)
    prev_video = None if index == 0 else await get_video_queue(index - 1)
    next_video = await get_video_queue(index + 1)
    return YoutubeResponses.VideoQueue(
        current_video=current_video, prev=bool(prev_video), next=bool(next_video)
    ).dict(by_alias=True)


@app.get(
    "/video/{video_id}",
    dependencies=[Depends(get_google_user)],
    response_model=YoutubeResponses.Video,
)
async def get_youtube_video(
    video_id: str,
    related_videos_length: int = Query(5, le=5),
    google_account: GoogleAccount = Depends(get_google_user),
):
    video_query = (
        select(YoutubeVideos)
        .where(YoutubeVideos.id == video_id)
        .alias("youtube_videos")
    )
    query = video_query.join(
        YoutubeChannels, YoutubeChannels.id == YoutubeVideos.channel_id
    )
    query = select(
        video_query, YoutubeChannels.title.label("channel_title")
    ).select_from(query)
    video = await db.fetch_one(query)
    if not video:
        return HTTPException(404)
    video = await get_related_info_for_video(
        YoutubeVideo.parse_obj(video), google_account
    )
    related_videos = []
    if related_videos_length > 0:
        query = (
            select(YoutubeVideos)
            .where(
                YoutubeVideos.id != video.id,
                (YoutubeVideos.category_id == video.category_id)
                | (YoutubeVideos.channel_id == video.channel_id),
            )
            .order_by(YoutubeVideos.published_at.desc())
            .limit(related_videos_length)
        )
        related_videos = await asyncio.gather(
            *[
                get_related_info_for_video(YoutubeVideo.parse_obj(row), google_account)
                for row in await db.fetch_all(query)
            ]
        )
    return YoutubeResponses.Video(
        video=video,
        related_videos=related_videos,
    ).dict(by_alias=True)


@app.get(
    "/subscriptions/{page}/{per_page}", response_model=YoutubeResponses.Subscriptions
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    google_account: GoogleAccount = Depends(get_google_user),
):
    subscriptions_query = (
        select(YoutubeSubscriptions)
        .where(YoutubeSubscriptions.email == google_account.email)
        .alias(name="youtube_subscriptions")
    )
    query = subscriptions_query.join(
        YoutubeChannels, YoutubeChannels.id == YoutubeSubscriptions.channel_id
    )
    query = (
        select(
            subscriptions_query,
            YoutubeChannels.title.label("channel_title"),
            YoutubeChannels.thumbnail.label("channel_thumbnail"),
        )
        .select_from(query)
        .order_by(YoutubeChannels.title)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    subscriptions = [
        YoutubeSubscriptionResponse.parse_obj(row) for row in await db.fetch_all(query)
    ]
    return YoutubeResponses.Subscriptions(subscriptions=subscriptions).dict(
        by_alias=True
    )


@app.get("/channel/{channel_id}", response_model=YoutubeChannel)
async def get_youtube_channel(channel_id: str):
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    channel = await db.fetch_one(query)
    if not channel:
        raise HTTPException(404)
    return YoutubeChannel.parse_obj(channel).dict(by_alias=True)
