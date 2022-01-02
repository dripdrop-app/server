from pydantic.fields import Field
from fastapi import FastAPI, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from server.api.youtube import google_api
from server.api.youtube.tasks import update_google_access_token
from server.config import config
from server.database import db, google_accounts, youtube_subscriptions, youtube_channels, youtube_videos
from server.dependencies import get_authenticated_user
from server.models import User
from sqlalchemy.sql.expression import select, desc

app = FastAPI()


@app.get('/account')
@db.transaction()
async def get_youtube_account(user: User = Depends(get_authenticated_user)):
    query = google_accounts.select().where(
        google_accounts.c.user_email == user.email)
    google_account = await db.fetch_one(query)
    if google_account:
        access_token = await update_google_access_token(google_account.get('email'))
        if access_token:
            google_email = await google_api.get_user_email(access_token)
            if google_email:
                return JSONResponse({
                    'email': google_email
                })
            query = google_accounts.delete().where(
                google_accounts.c.user_email == user.email)
            await db.execute(query)
    raise HTTPException(404)


@app.get('/oauth', response_class=PlainTextResponse)
async def create_oauth_link(user: User = Depends(get_authenticated_user)):
    oauth = google_api.create_oauth_url(
        f'{config.server_url}/auth/googleoauth2', user.email)
    return PlainTextResponse(oauth['url'])


@app.get('/videos/{page}/{per_page}')
async def get_youtube_videos(page: int = 1, per_page: int = Field(50, le=50), user: User = Depends(get_authenticated_user)):
    user_videos = google_accounts.join(
        youtube_subscriptions,
        google_accounts.c.email == youtube_subscriptions.c.email
    ).join(
        youtube_channels,
        youtube_subscriptions.c.channel_id == youtube_channels.c.id
    ).join(
        youtube_videos,
        youtube_channels.c.id == youtube_videos.c.channel_id
    )
    query = select(youtube_videos).select_from(user_videos).where(
        google_accounts.c.user_email == user.email).order_by(desc(youtube_videos.c.published_at)).offset(page * per_page).limit(per_page)
    youtube_user_videos = await db.fetch_all(query)
    return JSONResponse({'videos': [jsonable_encoder(video) for video in youtube_user_videos]})
