from asgiref.sync import sync_to_async
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from sqlalchemy import select

from dripdrop.apps.authentication.models import User
from dripdrop.dependencies import (
    get_authenticated_user,
    create_db_session,
    AsyncSession,
)
from dripdrop.rq import queue
from dripdrop.logging import logger
from dripdrop.services.google_api import google_api_service
from dripdrop.settings import settings

from .channels import channels_api
from .dependencies import get_google_user
from .models import GoogleAccount
from .responses import AccountResponse
from .subscriptions import subscriptions_api
from .tasks import youtube_tasker
from .videos import videos_api

app = FastAPI(
    openapi_tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Google account not connected"}
    },
)
app.include_router(videos_api)
app.include_router(subscriptions_api)
app.include_router(channels_api)


@app.get(
    "/googleoauth2",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Error getting oauth tokens"}
    },
)
async def google_oauth2(
    request: Request,
    state: str = Query(...),
    code: str = Query(...),
    error: str = Query(None),
    db: AsyncSession = Depends(create_db_session),
):
    if error:
        raise HTTPException(400)
    email = state
    query = select(User).where(User.email == email)
    results = await db.scalars(query)
    user: User | None = results.first()
    if not user:
        return RedirectResponse("/")
    get_oauth_tokens = sync_to_async(google_api_service.get_oauth_tokens)
    tokens = None
    try:
        tokens = await get_oauth_tokens(
            f"{request.base_url}api/youtube/googleoauth2", code
        )
        get_user_email = sync_to_async(google_api_service.get_user_email)
        google_email = await get_user_email(tokens.get("access_token"))
        query = select(GoogleAccount).where(GoogleAccount.email == google_email)
        results = await db.scalars(query)
        google_account: GoogleAccount | None = results.first()
        if google_account:
            google_account.access_token = tokens["access_token"]
            google_account.refresh_token = tokens["refresh_token"]
            google_account.expires = tokens["expires_in"]
            await db.commit()
        else:
            db.add(
                GoogleAccount(
                    email=google_email,
                    user_email=email,
                    access_token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"],
                    expires=tokens["expires_in"],
                )
            )
            await db.commit()
        job = queue.enqueue(
            youtube_tasker.update_youtube_video_categories, args=(False,)
        )
        queue.enqueue(
            youtube_tasker.update_user_youtube_subscriptions_job,
            args=(email,),
            depends_on=job,
        )
    except Exception as e:
        logger.error(e.message)
    return RedirectResponse("/youtube/videos")


@app.get("/account", response_model=AccountResponse)
async def get_youtube_account(
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    if settings.env == "production":
        await youtube_tasker.update_google_access_token(google_account.email)
    query = select(GoogleAccount).where(GoogleAccount.email == google_account.email)
    results = await db.scalars(query)
    account: GoogleAccount = results.first()
    return AccountResponse(email=account.email, refresh=not bool(account.access_token))


@app.get("/oauth", response_class=PlainTextResponse)
async def create_oauth_link(
    request: Request, user: User = Depends(get_authenticated_user)
):
    oauth = google_api_service.create_oauth_url(
        f"{request.base_url}api/youtube/googleoauth2", user.email
    )
    return PlainTextResponse(oauth["url"])
