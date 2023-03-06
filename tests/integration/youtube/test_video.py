from fastapi import status
from httpx import AsyncClient

from dripdrop.settings import settings

VIDEOS_URL = "/api/youtube/videos"


async def test_get_video_when_not_logged_in(client: AsyncClient):
    response = await client.get(
        f"{VIDEOS_URL}", params={"video_id": "1", "related_videos_length": 1}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_video_with_nonexistent_video(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(
        f"{VIDEOS_URL}", params={"video_id": "1", "related_videos_length": 1}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_video_with_no_related_videos(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video,
    create_video_category,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    other_category = await create_video_category(id=2, name="category_2")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=other_category.id,
    )
    response = await client.get(
        f"{VIDEOS_URL}", params={"video_id": "1", "related_videos_length": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "video": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": None,
            "watched": None,
        },
        "relatedVideos": [],
    }


async def test_get_video_with_related_videos_by_common_category(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video,
    create_video_category,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    other_channel = await create_channel(
        id="2", title="channel_2", thumbnail="thumbnail"
    )
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    related_video = await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=other_channel.id,
        category_id=category.id,
    )
    response = await client.get(
        f"{VIDEOS_URL}", params={"video_id": "1", "related_videos_length": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "video": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": None,
            "watched": None,
        },
        "relatedVideos": [
            {
                "id": related_video.id,
                "title": related_video.title,
                "thumbnail": related_video.thumbnail,
                "categoryId": category.id,
                "publishedAt": related_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": other_channel.id,
                "channelTitle": other_channel.title,
                "channelThumbnail": other_channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": None,
            }
        ],
    }
