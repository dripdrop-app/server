from fastapi import FastAPI, Depends, HTTPException, Query, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from server.api.youtube import google_api
from server.api.youtube.tasks import update_google_access_token
from server.config import config
from server.database import GoogleAccount, YoutubeVideo, db, google_accounts, youtube_subscriptions, youtube_channels, youtube_videos, youtube_video_categories
from server.dependencies import get_authenticated_user
from server.models import SessionUser, YoutubeResponses
from sqlalchemy.sql.expression import desc, func, select, distinct
from typing import List

app = FastAPI(dependencies=[Depends(get_authenticated_user)])


@app.get('/account', response_model=YoutubeResponses.Account)
async def get_youtube_account(user: SessionUser = Depends(get_authenticated_user)):
    query = google_accounts.select().where(
        google_accounts.c.user_email == user.email)
    google_account = await db.fetch_one(query)
    if google_account:
        google_account = GoogleAccount.parse_obj(google_account)
        access_token = await update_google_access_token(google_account.email)
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
async def create_oauth_link(user: SessionUser = Depends(get_authenticated_user)):
    oauth = google_api.create_oauth_url(
        f'{config.server_url}/auth/googleoauth2', user.email)
    return PlainTextResponse(oauth['url'])


@app.get('/videos/{page}/{per_page}', response_model=YoutubeResponses.Videos)
async def get_youtube_videos(
    page: int = 1,
    per_page: int = Path(50, le=50),
    user: SessionUser = Depends(get_authenticated_user),
    video_categories: List[int] = Query([])
):
    google_account_subquery = google_accounts.select().where(
        google_accounts.c.user_email == user.email).alias('google_accounts_sub')

    youtube_videos_all_query = youtube_videos
    youtube_videos_sub_query = youtube_videos.select().where(
        youtube_videos.c.category_id.in_(video_categories)).alias('youtube_videos_sub')

    joins = google_account_subquery.join(
        youtube_subscriptions, google_account_subquery.c.email == youtube_subscriptions.c.email)
    joins = joins.join(youtube_channels, youtube_subscriptions.c.channel_id ==
                       youtube_channels.c.id)

    all_joins = joins.join(youtube_videos_all_query, youtube_channels.c.id ==
                           youtube_videos_all_query.c.channel_id)
    sub_joins = joins.join(youtube_videos_sub_query, youtube_channels.c.id ==
                           youtube_videos_sub_query.c.channel_id)

    if len(video_categories) == 0:
        joins = all_joins
        youtube_videos_query = youtube_videos_all_query
    else:
        joins = sub_joins
        youtube_videos_query = youtube_videos_sub_query

    query = select([func.count(youtube_videos_query.c.id)]
                   ).select_from(joins)
    count = await db.fetch_val(query)

    query = select(
        [distinct(youtube_videos_all_query.c.category_id)]).select_from(all_joins)
    category_ids = [row.get('category_id') for row in await db.fetch_all(query)]

    query = youtube_video_categories.select().where(
        youtube_video_categories.c.id.in_(category_ids))
    categories = await db.fetch_all(query)

    query = select(youtube_videos_query, youtube_channels.c.title.label('channel_title')).select_from(
        joins).order_by(desc(youtube_videos_query.c.published_at)).offset((page - 1) * per_page).limit(per_page)
    videos = await db.fetch_all(query)
    return JSONResponse({'videos': jsonable_encoder(videos), 'total_videos': count, 'categories': jsonable_encoder(categories)})


@app.get('/subscriptions/{page}/{per_page}', response_model=YoutubeResponses.Subscriptions)
async def get_youtube_subscriptions(page: int = 1, per_page: int = Path(50, le=50), user: SessionUser = Depends(get_authenticated_user)):
    google_account_subquery = google_accounts.select().where(
        google_accounts.c.user_email == user.email).alias('google_accounts_sub')
    joins = google_account_subquery.join(
        youtube_subscriptions, google_account_subquery.c.email == youtube_subscriptions.c.email
    )
    joins = joins.join(
        youtube_channels, youtube_subscriptions.c.channel_id == youtube_channels.c.id)

    query = select([func.count(youtube_subscriptions.c.id)]).select_from(joins)
    count = await db.fetch_val(query)

    query = select(youtube_subscriptions, youtube_channels.c.title.label(
        'channel_title'), youtube_channels.c.thumbnail.label('channel_thumbnail')).select_from(joins).order_by(youtube_channels.c.title).offset((page - 1) * per_page).limit(per_page)
    subscriptions = await db.fetch_all(query)
    return JSONResponse({'subscriptions': jsonable_encoder(subscriptions), 'total_subscriptions': count})
