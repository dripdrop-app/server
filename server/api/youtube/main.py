import logging
import server.utils.google_api as google_api
from asyncpg import UniqueViolationError
from fastapi import FastAPI, Depends, HTTPException, Query, Path, Response
from fastapi.responses import PlainTextResponse, RedirectResponse
from server.config import config
from server.dependencies import get_authenticated_user, get_google_user
from server.models.main import (
    db,
    Users,
    YoutubeVideo,
    YoutubeVideoCategory,
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


def convertVideoToResponse(video: YoutubeVideo, row):
    return YoutubeVideoResponse(
        id=video.id,
        title=video.title,
        thumbnail=video.thumbnail,
        channel_id=video.channel_id,
        category_id=video.category_id,
        published_at=video.published_at,
        created_at=video.created_at,
        channel_title=row["channel_title"],
        liked=row.get("liked"),
        queued=row.get("queued"),
    )


@app.get(
    "/googleoauth2", dependencies=[Depends(get_authenticated_user)], responses={401: {}}
)
async def google_oauth2(
    state: str = Query(...), code: str = Query(...), error: str = Query(None)
):
    if error:
        raise HTTPException(400)

    email = state
    query = select(Users).where(Users.email == email)
    user = await db.fetch_one(query)
    if not user:
        return RedirectResponse("/")

    tokens = await google_api.get_oauth_tokens(
        f"{config.server_url}/api/youtube/googleoauth2", code
    )
    if tokens:
        google_email = await google_api.get_user_email(tokens.get("access_token"))
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
                .values(access_token=new_access_token)
                .where(GoogleAccounts.email == google_account.email)
            )
            await db.execute(query)
    return YoutubeResponses.Account(
        email=google_account.email, refresh=not bool(access_token)
    ).dict()


@app.get("/oauth", response_class=PlainTextResponse)
async def create_oauth_link(user: User = Depends(get_authenticated_user)):
    oauth = google_api.create_oauth_url(
        f"{config.server_url}/api/youtube/googleoauth2", user.email
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
    categories = []
    for row in await db.fetch_all(query):
        category = YoutubeVideoCategory.parse_obj(row)
        categories.append(
            YoutubeVideoCategoryResponse(
                id=category.id,
                name=category.name,
                created_at=category.created_at,
            )
        )
    return YoutubeResponses.VideoCategories(categories=categories).dict()


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
    channel_query = select(YoutubeChannels)
    if channel_id:
        channel_query = channel_query.where(YoutubeChannels.id == channel_id)
    channel_query = channel_query.alias(name="youtube_channels")

    videos_query = select(YoutubeVideos)
    if video_categories:
        videos_query = videos_query.where(
            YoutubeVideos.category_id.in_(video_categories)
        )
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

    if channel_id:
        query = channel_query.join(
            videos_query, videos_query.c.channel_id == channel_query.c.id
        )
    else:
        query = (
            select(YoutubeSubscriptions)
            .where(YoutubeSubscriptions.email == google_account.email)
            .alias(name="youtube_subscriptions")
            .join(
                channel_query,
                channel_query.c.id == YoutubeSubscriptions.channel_id,
            )
            .join(videos_query, videos_query.c.channel_id == channel_query.c.id)
        )

    query = query.join(
        video_likes_query,
        video_likes_query.c.video_id == videos_query.c.id,
        isouter=not liked_only,
    ).join(
        video_queues_query,
        video_queues_query.c.video_id == videos_query.c.id,
        isouter=not queued_only,
    )

    query = select(
        videos_query,
        video_likes_query.c.created_at.label("liked"),
        video_queues_query.c.created_at.label("queued"),
        channel_query.c.title.label("channel_title"),
    ).select_from(query)
    if liked_only:
        query = query.order_by(video_likes_query.c.created_at.asc())
    elif queued_only:
        query = query.order_by(video_queues_query.c.created_at.asc())
    else:
        query = query.order_by(videos_query.c.published_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    videos = []
    rows = await db.fetch_all(query)
    for row in rows:
        video = YoutubeVideo.parse_obj(row)
        videos.append(convertVideoToResponse(video, row))
    return YoutubeResponses.Videos(videos=videos).dict()


@app.put("/videos/like")
async def add_youtube_video_like(
    video_id: str = Query(...),
    google_account: GoogleAccount = Depends(get_google_user),
):
    try:
        query = insert(YoutubeVideoLikes).values(
            email=google_account.email, video_id=video_id
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
            email=google_account.email, video_id=video_id
        )
        await db.execute(query)
    except UniqueViolationError:
        raise HTTPException(400)
    return Response(None, 200)


@app.delete("/videos/queue")
async def delete_youtube_video_queue(
    video_id: str = Query(None),
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
    index = index - 1
    video_queues_query = (
        select(YoutubeVideoQueues)
        .where(YoutubeVideoQueues.email == google_account.email)
        .alias(name="youtube_video_queues")
    )
    video_likes_query = (
        select(YoutubeVideoLikes)
        .where(YoutubeVideoLikes.email == google_account.email)
        .alias(name="youtube_video_likes")
    )
    query = (
        video_queues_query.join(
            YoutubeVideos, YoutubeVideos.id == video_queues_query.c.video_id
        )
        .join(
            video_likes_query,
            video_likes_query.c.video_id == video_queues_query.c.video_id,
            isouter=True,
        )
        .join(YoutubeChannels, YoutubeChannels.id == YoutubeVideos.channel_id)
    )

    def create_video_query(index: int):
        return (
            select(
                YoutubeVideos,
                video_likes_query.c.created_at.label("liked"),
                video_queues_query.c.created_at.label("queued"),
                YoutubeChannels.title.label("channel_title"),
            )
            .select_from(query)
            .order_by(YoutubeVideoQueues.created_at.asc())
            .offset(index)
            .limit(1)
        )

    current_video_row = await db.fetch_one(create_video_query(index))
    if not current_video_row:
        raise HTTPException(404)
    current_video = convertVideoToResponse(
        YoutubeVideo.parse_obj(current_video_row), current_video_row
    )

    prev_video = None
    prev_video_row = (
        None if index == 0 else await db.fetch_one(create_video_query(index - 1))
    )
    if prev_video_row:
        prev_video = convertVideoToResponse(
            YoutubeVideo.parse_obj(prev_video_row), prev_video_row
        )

    next_video = None
    next_video_row = await db.fetch_one(create_video_query(index + 1))
    if next_video_row:
        next_video = convertVideoToResponse(
            YoutubeVideo.parse_obj(next_video_row), next_video_row
        )

    return YoutubeResponses.VideoQueue(
        current_video=current_video, prev=bool(prev_video), next=bool(next_video)
    )


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
        .alias(name="youtube_videos")
    )
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
    query = (
        video_query.join(
            YoutubeChannels, YoutubeChannels.id == video_query.c.channel_id
        )
        .join(
            video_queues_query,
            video_queues_query.c.video_id == video_query.c.id,
            isouter=True,
        )
        .join(
            video_likes_query,
            video_likes_query.c.video_id == video_query.c.id,
            isouter=True,
        )
    )
    query = select(
        video_query,
        video_likes_query.c.created_at.label("liked"),
        video_queues_query.c.created_at.label("queued"),
        YoutubeChannels.title.label("channel_title"),
    ).select_from(query)

    row = await db.fetch_one(query)
    if row:
        video = YoutubeVideo.parse_obj(row)
        video = convertVideoToResponse(video, row)
        related_videos = []

        if related_videos_length > 0:
            related_videos_query = (
                select(YoutubeVideos)
                .where(
                    YoutubeVideos.id != video.id,
                    (YoutubeVideos.category_id == video.category_id)
                    | (YoutubeVideos.channel_id == video.channel_id),
                )
                .alias(name="related_youtube_videos")
            )

            query = (
                related_videos_query.join(
                    YoutubeChannels,
                    YoutubeChannels.id == related_videos_query.c.channel_id,
                )
                .join(
                    video_likes_query,
                    video_likes_query.c.video_id == related_videos_query.c.id,
                    isouter=True,
                )
                .join(
                    video_queues_query,
                    video_queues_query.c.video_id == related_videos_query.c.id,
                    isouter=True,
                )
            )
            query = (
                select(
                    related_videos_query,
                    video_likes_query.c.created_at.label("liked"),
                    video_queues_query.c.created_at.label("queued"),
                    YoutubeChannels.title.label("channel_title"),
                )
                .select_from(query)
                .order_by(related_videos_query.c.published_at.desc())
                .limit(related_videos_length)
            )

            rows = await db.fetch_all(query)
            for row in rows:
                related_video = YoutubeVideo.parse_obj(row)
                related_videos.append(convertVideoToResponse(related_video, row))

        return YoutubeResponses.Video(
            video=video,
            related_videos=related_videos,
        )
    raise HTTPException(404)


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
    return YoutubeResponses.Subscriptions(subscriptions=subscriptions).dict()


@app.get("/channel/{channel_id}", response_model=YoutubeChannel)
async def get_youtube_channel(channel_id: str):
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    channel = await db.fetch_one(query)
    if channel:
        channel = YoutubeChannel.parse_obj(channel)
        return channel
    raise HTTPException(404)
