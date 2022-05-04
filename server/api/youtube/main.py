import server.utils.google_api as google_api
from asyncpg import UniqueViolationError
from fastapi import FastAPI, Depends, HTTPException, Query, Path, WebSocket, Response
from fastapi.responses import PlainTextResponse
from server.config import config
from server.dependencies import get_authenticated_user
from server.models.main import (
    db,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLikes,
    GoogleAccount,
    GoogleAccounts,
    YoutubeSubscriptions,
    YoutubeChannels,
    YoutubeVideos,
    YoutubeVideoCategories,
    AuthenticatedUser,
)
from server.models.api import (
    YoutubeResponses,
    YoutubeSubscriptionResponse,
    YoutubeVideoCategoryResponse,
    YoutubeVideoResponse,
)
from server.redis import (
    create_websocket_redis_channel_listener,
    RedisChannels,
)
from server.tasks.youtube import update_google_access_token
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
        liked=bool(row["liked"]),
    )


@app.get("/account", response_model=YoutubeResponses.Account)
async def get_youtube_account(
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == user.email)
    google_account = await db.fetch_one(query)
    if google_account:
        google_account = GoogleAccount.parse_obj(google_account)
        access_token = google_account.access_token
        if config.env == "production":
            new_access_token = await update_google_access_token(
                google_account.email, db=db
            )
            if not new_access_token:
                return YoutubeResponses.Account(email="", refresh=False)
            elif new_access_token != access_token:
                access_token = new_access_token
                query = (
                    update(GoogleAccounts)
                    .values(access_token=new_access_token)
                    .where(GoogleAccounts.user_email == user.email)
                )
                await db.execute(query)
        return YoutubeResponses.Account(
            email=google_account.email, refresh=not bool(access_token)
        ).dict()
    raise HTTPException(404)


@app.get("/oauth", response_class=PlainTextResponse)
async def create_oauth_link(user: AuthenticatedUser = Depends(get_authenticated_user)):
    oauth = google_api.create_oauth_url(
        f"{config.server_url}/auth/googleoauth2", user.email
    )
    return PlainTextResponse(oauth["url"])


@app.get("/videos/categories", response_model=YoutubeResponses.VideoCategories)
async def get_youtube_video_categories(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    channel_id: str = Query(None),
):
    channel_subquery = select(YoutubeChannels)
    if channel_id:
        channel_subquery = channel_subquery.where(YoutubeChannels.id == channel_id)
    channel_subquery = channel_subquery.alias(name="youtube_channels")

    videos_query = select(YoutubeVideos).alias(name="youtube_videos")

    if channel_id:
        query = channel_subquery.join(
            videos_query, videos_query.c.channel_id == channel_subquery.c.id
        )
    else:
        google_account_subquery = (
            select(GoogleAccounts)
            .where(GoogleAccounts.user_email == user.email)
            .alias(name="google_accounts")
        )
        query = (
            google_account_subquery.join(
                YoutubeSubscriptions, YoutubeSubscriptions.email == GoogleAccounts.email
            )
            .join(
                channel_subquery,
                channel_subquery.c.id == YoutubeSubscriptions.channel_id,
            )
            .join(videos_query, videos_query.c.channel_id == channel_subquery.c.id)
        )

    query = query.join(
        YoutubeVideoCategories, YoutubeVideoCategories.id == videos_query.c.category_id
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
    user: AuthenticatedUser = Depends(get_authenticated_user),
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
        .where(YoutubeVideoLikes.email == user.email)
        .alias(name="youtube_video_likes")
    )

    if channel_id:
        query = channel_query.join(
            videos_query, videos_query.c.channel_id == channel_query.c.id
        )
    else:
        google_account_subquery = (
            select(GoogleAccounts)
            .where(GoogleAccounts.user_email == user.email)
            .alias(name="google_accounts")
        )
        query = (
            google_account_subquery.join(
                YoutubeSubscriptions, YoutubeSubscriptions.email == GoogleAccounts.email
            )
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
    )
    query = select(
        videos_query,
        video_likes_query.c.video_id.label("liked"),
        channel_query.c.title.label("channel_title"),
    ).select_from(query)
    if liked_only:
        query = query.order_by(video_likes_query.c.created_at.desc())
    else:
        query = query.order_by(videos_query.c.published_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    videos = []
    for row in await db.fetch_all(query):
        video = YoutubeVideo.parse_obj(row)
        videos.append(convertVideoToResponse(video, row))
    return YoutubeResponses.Videos(videos=videos).dict()


@app.get("/video/{video_id}", response_model=YoutubeResponses.Video)
async def get_youtube_video(video_id: str, related_videos_length: int = Query(0, le=5)):
    video_query = (
        select(YoutubeVideos)
        .where(YoutubeVideos.id == video_id)
        .alias(name="youtube_videos")
    )
    channel_query = select(YoutubeChannels).alias(name="youtube_channels")
    video_likes_query = select(YoutubeVideoLikes).alias(name="youtube_video_likes")

    query = video_query.join(
        channel_query, channel_query.c.id == video_query.c.channel_id
    ).join(
        video_likes_query,
        video_likes_query.c.video_id == video_query.c.id,
        isouter=True,
    )
    query = select(
        video_query,
        video_likes_query.c.video_id.label("liked"),
        channel_query.c.title.label("channel_title"),
    ).select_from(query)

    row = await db.fetch_one(query)
    if row:
        video = YoutubeVideo.parse_obj(row)
        video = convertVideoToResponse(video, row)

        related_videos_query = (
            select(YoutubeVideos)
            .where(
                YoutubeVideos.id != video.id,
                (YoutubeVideos.category_id == video.category_id)
                | (YoutubeVideos.channel_id == video.channel_id),
            )
            .alias(name="related_youtube_videos")
        )

        query = related_videos_query.join(
            channel_query, channel_query.c.id == related_videos_query.c.channel_id
        ).join(
            video_likes_query,
            video_likes_query.c.video_id == related_videos_query.c.id,
            isouter=True,
        )
        query = (
            select(
                related_videos_query,
                video_likes_query.c.video_id.label("liked"),
                channel_query.c.title.label("channel_title"),
            )
            .select_from(query)
            .order_by(related_videos_query.c.published_at.desc())
            .limit(related_videos_length)
        )

        rows = await db.fetch_all(query)
        related_videos = []
        for row in rows:
            related_video = YoutubeVideo.parse_obj(row)
            related_videos.append(convertVideoToResponse(related_video, row))

        return YoutubeResponses.Video(
            video=video,
            relatedVideos=related_videos,
        )
    raise HTTPException(404)


@app.get(
    "/subscriptions/{page}/{per_page}", response_model=YoutubeResponses.Subscriptions
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    query = (
        select(GoogleAccounts)
        .where(GoogleAccounts.user_email == user.email)
        .alias(name="google_accounts")
        .join(YoutubeSubscriptions, YoutubeSubscriptions.email == GoogleAccounts.email)
        .join(YoutubeChannels, YoutubeChannels.id == YoutubeSubscriptions.channel_id)
    )
    query = (
        select(
            YoutubeSubscriptions,
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


@app.websocket("/subscriptions/listen")
async def listen_subscription_job(
    websocket: WebSocket, user: AuthenticatedUser = Depends(get_authenticated_user)
):
    async def handler(msg):
        user_email = msg.get("data").decode()
        if user.email == user_email:
            query = select(GoogleAccounts).where(
                GoogleAccounts.user_email == user_email
            )
            google_account = await db.fetch_one(query)
            if google_account:
                try:
                    google_account = GoogleAccount.parse_obj(google_account)
                    await websocket.send_json(
                        {
                            "type": "SUBSCRIPTIONS_UPDATE",
                            "finished": not google_account.subscriptions_loading,
                        }
                    )
                except Exception:
                    pass
        return

    await websocket.accept()
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == user.email)
    google_account = GoogleAccount.parse_obj(await db.fetch_one(query))
    await websocket.send_json(
        YoutubeResponses.SubscriptionUpdate(
            status=google_account.subscriptions_loading
        ).dict()
    )
    await create_websocket_redis_channel_listener(
        websocket=websocket,
        channel=RedisChannels.YOUTUBE_SUBSCRIPTION_JOB_CHANNEL,
        handler=handler,
    )


@app.put("/videos/like")
async def add_youtube_video_like(
    video_id: str = Query(...),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    try:
        query = insert(YoutubeVideoLikes).values(email=user.email, video_id=video_id)
        await db.execute(query)
    except UniqueViolationError:
        raise HTTPException(400)
    return Response(None, 200)


@app.put("/videos/unlike")
async def delete_youtube_video_like(
    video_id: str = Query(...),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    query = delete(YoutubeVideoLikes).where(
        YoutubeVideoLikes.email == user.email, YoutubeVideoLikes.video_id == video_id
    )
    await db.execute(query)
    return Response(None, 200)
