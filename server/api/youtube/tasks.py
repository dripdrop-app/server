import asyncio
import datetime
from typing import Union
from server.api.youtube import google_api
from server.db import (
    database,
    google_accounts,
    youtube_subscriptions,
    youtube_channels,
    youtube_video_category,
    youtube_video_categories,
    youtube_jobs
)
from server.utils.wrappers import exception_handler


async def update_category(category):
    category_id = category['id']
    category_title = category['snippet']['title']
    query = youtube_video_categories.select().where(
        youtube_video_categories.c.id == category_id)
    existing_category = await database.fetch_one(query)
    if existing_category:
        if existing_category.get('name') != category_title:
            query = youtube_video_category.delete().where(
                youtube_video_category.c.category_id == category_id)
            await database.execute(query)
            query = youtube_video_categories.update().where(
                youtube_video_categories.c.name == category_title)
    else:
        query = youtube_video_categories.insert().values(
            id=category_id, name=category_title)
        await database.execute(query)


async def update_video_categories():
    video_categories = await google_api.get_video_categories()
    await asyncio.gather(update_category(category) for category in video_categories)


async def update_subscription(email: str, subscription):
    subscription_id = subscription['id']
    subscription_channel_id = subscription['snippet']['channelId']
    query = youtube_subscriptions.select().where(
        youtube_subscriptions.c.id == subscription['id'])
    existing_subscription = await database.fetch_one(query)
    if not existing_subscription:
        query = youtube_video_category.insert().values(
            id=subscription_id,
            channel_id=subscription_channel_id,
            email=email
        )
        await database.execute(query)
        query = youtube_channels.select().where(
            id=subscription_channel_id)
        existing_channel = await database.fetch_one(query)
        if not existing_channel:
            return subscription_channel_id
    return None


async def update_user_subscriptions(email: str, access_token: str):
    async for subscriptions in google_api.get_user_subscriptions(access_token):
        new_channel_ids = await asyncio.gather(
            update_subscription(email, subscription)
            for subscription in subscriptions
            if subscription['snippet']['resourceId']['kind'] == 'youtube#channel'
        )
        new_channels = await google_api.get_channels_info(filter(new_channel_ids))
        query = youtube_channels.insert()
        values = [
            {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'upload_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url']
            }
            for channel in new_channels
        ]
        await database.execute_many(query, values)
        yield subscriptions


@exception_handler()
async def update_subscriptions_job(email: Union[str, None]):
    await update_video_categories()
    if email:
        query = google_accounts.select().where(google_accounts.c.email == email)
    else:
        query = google_accounts.select()

    async for google_account in database.iterate(query):
        email = google_account.get('email')
        query = youtube_jobs.select().where(youtube_jobs.c.email == email)
        job = await database.fetch_one(query)
        if job:
            continue
        query = youtube_jobs.insert().values(email=email)
        await database.execute(query)

        last_updated = google_account.get('last_updated').timestamp()
        expires = google_account.get('expires')
        access_token = google_account.get('access_token')

        if datetime.datetime.now().timestamp() - last_updated >= expires:
            new_access_token = await google_api.refresh_access_token(google_account.get('refresh_token'))
            access_token = new_access_token['access_token']
            query = google_accounts.update().values(
                access_token=new_access_token['access_token'],
                expires=new_access_token['expires_in']
            ).where(google_accounts.c.email == google_account.get('email'))
            await database.execute(query)

        current_subscriptions = []
        async for subscriptions in update_user_subscriptions(access_token):
            for subscription in subscriptions:
                current_subscriptions.append(subscription['id'])

        query = youtube_subscriptions.delete().where(
            youtube_subscriptions.c.id.notin_(current_subscriptions))
        await database.execute(query)

        query = youtube_jobs.delete().where(youtube_jobs.c.email == email)
        await database.execute(query)
        await asyncio.sleep(1)
