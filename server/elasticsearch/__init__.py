from async_timeout import asyncio
from elasticsearch import AsyncElasticsearch
from server.config import config
from server.models import (
    db,
    YoutubeSubscription,
    YoutubeSubscriptions,
    YoutubeVideo,
    YoutubeVideoCategories,
    YoutubeVideoCategory,
    YoutubeVideos,
    YoutubeChannel,
    YoutubeChannels,
)
from sqlalchemy import select

es = AsyncElasticsearch(hosts=[config.elasticsearch_url])


async def create_or_update_indices(index):
    if await es.indices.exists(index=index["name"]):
        await es.indices.put_mapping(index=index["name"], body=index["mappings"])
    else:
        await es.indices.create(index=index["name"], mappings=index["mappings"])


youtube_subscriptions_index = {
    "name": "youtube_subscriptions",
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "channel": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "keyword"},
                    "thumbnail": {"type": "text"},
                },
            },
            "email": {"type": "keyword"},
            "published_at": {"type": "date"},
            "created_at": {"type": "date"},
        }
    },
}


async def create_youtube_subscription(id, channel_id, email, published_at, created_at):
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    channel = YoutubeChannel.parse_obj(await db.fetch_one(query=query))
    await es.update(
        index=youtube_subscriptions_index["name"],
        id=id,
        doc={
            "id": id,
            "channel": {
                "id": channel.id,
                "title": channel.title,
                "thumbnail": channel.thumbnail,
            },
            "email": email,
            "published_at": published_at,
            "created_at": created_at,
        },
        doc_as_upsert=True,
    )


async def populate_youtube_subscriptions_index():
    await create_or_update_indices(youtube_subscriptions_index)
    query = select(YoutubeSubscriptions)
    tasks = []
    async for subscription in db.iterate(query):
        subscription = YoutubeSubscription.parse_obj(subscription)
        tasks.append(
            create_youtube_subscription(
                id=subscription.id,
                channel_id=subscription.channel_id,
                email=subscription.email,
                published_at=subscription.published_at,
                created_at=subscription.created_at,
            )
        )
    await asyncio.gather(*tasks)


youtube_videos_index = {
    "name": "youtube_videos",
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "title": {"type": "keyword"},
            "thumbnail": {"type": "text"},
            "channel": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "keyword"},
                },
            },
            "published_at": {"type": "date"},
            "created_at": {"type": "date"},
            "category": {
                "type": "nested",
                "properties": {"id": {"type": "keyword"}, "name": {"type": "keyword"}},
            },
        }
    },
}


async def create_youtube_video(
    id,
    title,
    channel_id,
    category_id,
    published_at,
    created_at,
    thumbnail,
):
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    channel = YoutubeChannel.parse_obj(await db.fetch_one(query=query))
    query = select(YoutubeVideoCategories).where(
        YoutubeVideoCategories.id == category_id
    )
    category = YoutubeVideoCategory.parse_obj(await db.fetch_one(query=query))
    await es.update(
        index=youtube_videos_index["name"],
        id=id,
        doc={
            "id": id,
            "title": title,
            "thumbnail": thumbnail,
            "channel": {"id": channel.id, "title": channel.title},
            "published_at": published_at,
            "created_at": created_at,
            "category": {"id": category.id, "name": category.name},
        },
        doc_as_upsert=True,
    )


async def populate_youtube_videos_index():
    await create_or_update_indices(youtube_videos_index)
    query = select(YoutubeVideos)
    tasks = []
    async for video in db.iterate(query):
        video = YoutubeVideo.parse_obj(video)
        tasks.append(
            create_youtube_video(
                id=video.title,
                title=video.title,
                channel_id=video.channel_id,
                category_id=video.category_id,
                created_at=video.created_at,
                published_at=video.published_at,
                thumbnail=video.published_at,
            )
        )
    await asyncio.gather(*tasks)
