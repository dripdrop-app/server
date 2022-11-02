from .channels import youtube_channels_api
from .subscriptions import youtube_subscriptions_api
from .videos import youtube_videos_api
from asgiref.sync import sync_to_async
from fastapi import (
    Depends,
    APIRouter,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import PlainTextResponse, RedirectResponse
from server.config import config
from server.dependencies import (
    get_authenticated_user,
    get_google_user,
    create_db_session,
    DBSession,
    GoogleAccount,
)
from server.logging import logger
from server.models.api import (
    YoutubeResponses,
)
from server.models.api import User
from server.models.orm import (
    Users,
    GoogleAccounts,
)
from server.services.google_api import google_api_service
from server.services.rq import queue
from server.tasks.youtube import youtube_tasker
from sqlalchemy import select

youtube_api = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={401: {}},
)
youtube_api.include_router(youtube_videos_api)
youtube_api.include_router(youtube_subscriptions_api)
youtube_api.include_router(youtube_channels_api)


@youtube_api.get("/googleoauth2", responses={401: {}})
async def google_oauth2(
    request: Request,
    state: str = Query(...),
    code: str = Query(...),
    error: str = Query(None),
    db: DBSession = Depends(create_db_session),
):
    if error:
        raise HTTPException(400)
    email = state
    query = select(Users).where(Users.email == email)
    results = await db.scalars(query)
    user = results.first()
    if not user:
        return RedirectResponse("/")
    get_oauth_tokens = sync_to_async(google_api_service.get_oauth_tokens)
    tokens = await get_oauth_tokens(f"{request.base_url}api/youtube/googleoauth2", code)
    if tokens:
        get_user_email = sync_to_async(google_api_service.get_user_email)
        google_email = await get_user_email(tokens.get("access_token"))
        if google_email:
            query = select(GoogleAccounts).where(GoogleAccounts.email == google_email)
            results = await db.scalars(query)
            google_account = results.first()
            if google_account:
                google_account.access_token = tokens["access_token"]
                google_account.refresh_token = tokens["refresh_token"]
                google_account.expires = tokens["expires_in"]
                await db.commit()
            else:
                db.add(
                    GoogleAccounts(
                        email=google_email,
                        user_email=email,
                        access_token=tokens["access_token"],
                        refresh_token=tokens["refresh_token"],
                        expires=tokens["expires_in"],
                    )
                )
                await db.commit()
            job = queue.enqueue(
                youtube_tasker.update_youtube_video_categories,
                args=(False,),
            )
            queue.enqueue(
                youtube_tasker.update_user_youtube_subscriptions_job,
                args=(email,),
                depends_on=job,
            )
    else:
        logger.warning("Could not retrieve tokens")
    return RedirectResponse("/youtube/videos")


@youtube_api.get("/account", response_model=YoutubeResponses.Account)
async def get_youtube_account(
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
):
    access_token = google_account.access_token
    if config.env == "production":
        new_access_token = await youtube_tasker.update_google_access_token(
            google_account.email
        )
        if new_access_token != access_token:
            access_token = new_access_token
            query = select(GoogleAccounts).where(
                GoogleAccounts.email == google_account.email
            )
            results = await db.scalars(query)
            account = results.first()
            account.access_token = new_access_token
            await db.commit()
    return YoutubeResponses.Account(
        email=google_account.email,
        refresh=not bool(access_token),
    ).dict(by_alias=True)


@youtube_api.get("/oauth", response_class=PlainTextResponse)
async def create_oauth_link(
    request: Request,
    user: User = Depends(get_authenticated_user),
):
    oauth = google_api_service.create_oauth_url(
        f"{request.base_url}api/youtube/googleoauth2",
        user.email,
    )
    return PlainTextResponse(oauth["url"])
