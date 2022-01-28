import asyncio
import traceback
from asyncio.tasks import Task
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
    Path,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from server.api.youtube import google_api
from server.api.youtube.tasks import update_google_access_token
from server.config import config
from server.dependencies import get_authenticated_user
from server.models import (
    db,
    GoogleAccount,
    GoogleAccounts,
    YoutubeSubscriptions,
    YoutubeChannels,
    YoutubeVideos,
    YoutubeVideoCategories,
    AuthenticatedUser,
)
from server.models.api import YoutubeResponses
from server.redis import subscribe
from server.utils.enums import RedisChannels
from sqlalchemy import desc, func, select, update
from typing import List
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


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
            access_token = await update_google_access_token(google_account.email)
            if access_token != google_account.access_token:
                query = (
                    update(GoogleAccounts)
                    .values(access_token=access_token)
                    .where(GoogleAccounts.user_email == user.email)
                )
                await db.execute(query)
        else:
            access_token = google_account.access_token
        return JSONResponse(
            {
                "email": google_account.email,
                "refresh": not bool(access_token),
            }
        )
    raise HTTPException(404)


@app.websocket("/listen_subscription_job")
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
                google_account = GoogleAccount.parse_obj(google_account)
                await websocket.send_json(
                    {
                        "type": "SUBSCRIPTIONS_UPDATE",
                        "finished": not google_account.subscriptions_loading,
                    }
                )
        return

    task: Task = None
    try:
        await websocket.accept()
        task = asyncio.create_task(
            subscribe(RedisChannels.YOUTUBE_SUBSCRIPTION_JOB_CHANNEL, handler)
        )
        while True:
            await websocket.send_json({})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await websocket.close()
    except ConnectionClosedError:
        pass
    except ConnectionClosedOK:
        await websocket.close()
    except Exception:
        print(traceback.format_exc())
    finally:
        task.cancel()


@app.get("/oauth", response_class=PlainTextResponse)
async def create_oauth_link(user: AuthenticatedUser = Depends(get_authenticated_user)):
    oauth = google_api.create_oauth_url(
        f"{config.server_url}/auth/googleoauth2", user.email
    )
    return PlainTextResponse(oauth["url"])


@app.get("/videos/{page}/{per_page}", response_model=YoutubeResponses.Videos)
async def get_youtube_videos(
    page: int = Path(1, ge=1),
    per_page: int = Path(50, le=50),
    user: AuthenticatedUser = Depends(get_authenticated_user),
    video_categories: List[int] = Query([]),
    channel_id: str = Query(None),
):
    main_query = (
        select(GoogleAccounts)
        .where(GoogleAccounts.user_email == user.email)
        .alias(name="google_accounts")
        .join(YoutubeSubscriptions, YoutubeSubscriptions.email == GoogleAccounts.email)
        .join(YoutubeChannels, YoutubeChannels.id == YoutubeSubscriptions.channel_id)
    )

    videos_query = select(YoutubeVideos)
    if channel_id:
        videos_query = videos_query.where(YoutubeVideos.channel_id == channel_id)
    videos_query = videos_query.alias(name="youtube_videos")
    query = main_query.join(
        videos_query, videos_query.c.channel_id == YoutubeChannels.id
    ).join(
        YoutubeVideoCategories, YoutubeVideoCategories.id == videos_query.c.category_id
    )
    query = (
        select(YoutubeVideoCategories)
        .select_from(query)
        .distinct(YoutubeVideoCategories.id)
    )
    categories = await db.fetch_all(query)

    videos_query = select(YoutubeVideos)
    if channel_id:
        videos_query = videos_query.where(YoutubeVideos.channel_id == channel_id)
    if video_categories:
        videos_query = videos_query.where(
            YoutubeVideos.category_id.in_(video_categories)
        )
    videos_query = videos_query.alias(name="youtube_videos")
    query = main_query.join(
        videos_query, videos_query.c.channel_id == YoutubeChannels.id
    )

    count_query = select(func.count(videos_query.c.id)).select_from(query)
    count = await db.fetch_val(count_query)

    query = (
        select(videos_query, YoutubeChannels.title.label("channel_title"))
        .select_from(query)
        .order_by(desc(videos_query.c.published_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    videos = await db.fetch_all(query)

    return JSONResponse(
        {
            "videos": jsonable_encoder(videos),
            "total_videos": count,
            "categories": jsonable_encoder(categories),
        }
    )


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
    subscriptions = await db.fetch_all(query)
    return JSONResponse(
        {"subscriptions": jsonable_encoder(subscriptions), "total_subscriptions": count}
    )
