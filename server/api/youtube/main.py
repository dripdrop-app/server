import server.api.youtube.google_api as google_api
from fastapi import FastAPI, Depends, HTTPException, Query, Path, WebSocket
from fastapi.responses import PlainTextResponse
from importlib_metadata import email
from server.config import config
from server.dependencies import get_authenticated_user
from server.models.main import (
    db,
    YoutubeVideo,
    YoutubeVideoCategory,
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
from sqlalchemy import desc, func, select, update
from typing import List


app = FastAPI(dependencies=[Depends(get_authenticated_user)], responses={401: {}})


@app.get("/account", response_model=YoutubeResponses.Account)
async def get_youtube_account(
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == user.email)
    google_account = await db.fetch_one(query)
    if google_account:
        google_account = GoogleAccount.parse_obj(google_account)
        if config.env == "production":
            access_token = await update_google_access_token(google_account.email, db=db)
            if access_token != google_account.access_token:
                query = (
                    update(GoogleAccounts)
                    .values(access_token=access_token)
                    .where(GoogleAccounts.user_email == user.email)
                )
                await db.execute(query)
        else:
            access_token = google_account.access_token
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
        query = channel_subquery.where(YoutubeChannels.id == channel_id)
    channel_subquery = channel_subquery.alias("yt_channels")

    if channel_id:
        query = channel_subquery
    else:
        google_query = (
            select(GoogleAccounts)
            .where(GoogleAccounts.user_email == user.email)
            .alias(name="g_accounts")
        )
        query = google_query.join(
            YoutubeSubscriptions, YoutubeSubscriptions.email == google_query.c.email
        ).join(
            channel_subquery,
            channel_subquery.c.id == YoutubeSubscriptions.channel_id,
        )

    videos_query = select(YoutubeVideos)
    if channel_id:
        videos_query = videos_query.where(YoutubeVideos.channel_id == channel_id)
    videos_query = videos_query.alias(name="youtube_videos")
    query = query.join(
        videos_query, videos_query.c.channel_id == channel_subquery.c.id
    ).join(
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
    page: int = Path(1, ge=1),
    per_page: int = Path(50, le=50),
    video_categories: List[int] = Query([]),
    channel_id: str = Query(None),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    channel_subquery = select(YoutubeChannels)
    if channel_id:
        query = channel_subquery.where(YoutubeChannels.id == channel_id)
    channel_subquery = channel_subquery.alias("yt_channels")

    if channel_id:
        query = channel_subquery
    else:
        google_query = (
            select(GoogleAccounts)
            .where(GoogleAccounts.user_email == user.email)
            .alias(name="g_accounts")
        )
        query = google_query.join(
            YoutubeSubscriptions, YoutubeSubscriptions.email == google_query.c.email
        ).join(
            channel_subquery,
            channel_subquery.c.id == YoutubeSubscriptions.channel_id,
        )
    videos_query = select(YoutubeVideos)
    if channel_id:
        videos_query = videos_query.where(YoutubeVideos.channel_id == channel_id)
    if video_categories:
        videos_query = videos_query.where(
            YoutubeVideos.category_id.in_(video_categories)
        )
    videos_query = videos_query.alias(name="youtube_videos")

    query = query.join(videos_query, videos_query.c.channel_id == channel_subquery.c.id)
    count_query = select(func.count(videos_query.c.id)).select_from(query)
    count = await db.fetch_val(count_query)

    query = (
        select(videos_query, channel_subquery.c.title.label("channel_title"))
        .select_from(query)
        .order_by(desc(videos_query.c.published_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    videos = []
    for row in await db.fetch_all(query):
        video = YoutubeVideo.parse_obj(row)
        videos.append(
            YoutubeVideoResponse(
                id=video.id,
                title=video.title,
                thumbnail=video.thumbnail,
                channel_id=video.channel_id,
                published_at=video.published_at,
                category_id=video.category_id,
                created_at=video.created_at,
                channel_title=row["channel_title"],
            )
        )
    return YoutubeResponses.Videos(videos=videos, total_videos=count).dict()


@app.get(
    "/subscriptions/{page}/{per_page}", response_model=YoutubeResponses.Subscriptions
)
async def get_youtube_subscriptions(
    page: int = Path(1, ge=1),
    per_page: int = Path(50, le=50),
    user: AuthenticatedUser = Depends(get_authenticated_user),
):
    main_query = (
        select(GoogleAccounts)
        .where(GoogleAccounts.user_email == user.email)
        .alias(name="google_accounts")
        .join(YoutubeSubscriptions, YoutubeSubscriptions.email == GoogleAccounts.email)
        .join(YoutubeChannels, YoutubeChannels.id == YoutubeSubscriptions.channel_id)
    )

    query = select(func.count(YoutubeSubscriptions.id)).select_from(main_query)
    count = await db.fetch_val(query)

    query = (
        select(
            YoutubeSubscriptions,
            YoutubeChannels.title.label("channel_title"),
            YoutubeChannels.thumbnail.label("channel_thumbnail"),
        )
        .select_from(main_query)
        .order_by(YoutubeChannels.title)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    subscriptions = [
        YoutubeSubscriptionResponse.parse_obj(row) for row in await db.fetch_all(query)
    ]
    return YoutubeResponses.Subscriptions(
        subscriptions=subscriptions, total_subscriptions=count
    ).dict()


@app.websocket("/youtube/subscriptions/listen")
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
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == email)
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
