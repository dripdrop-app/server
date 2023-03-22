from fastapi import status
from httpx import AsyncClient

from dripdrop.settings import settings

QUEUE = "/api/youtube/videos/queue"


async def test_add_video_queue_when_not_logged_in(client: AsyncClient):
    response = await client.put(QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_add_video_queue_with_nonexistent_video(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.put(QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_video_queue(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    get_video_queue,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(channel_id=channel.id, email=user.email)
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    response = await client.put(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert await get_video_queue(email=user.email, video_id=video.id) is not None


async def test_add_video_queue_with_the_same_video(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(channel_id=channel.id, email=user.email)
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    response = await client.put(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = await client.put(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_delete_video_queue_when_not_logged_in(client: AsyncClient):
    response = await client.delete(QUEUE, params={"video_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_video_queue_with_nonexistent_video_queue(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.delete(QUEUE, params={"video_id": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_video_queue(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
    get_video_queue,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    await create_video_queue(email=user.email, video_id=video.id)
    response = await client.delete(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert await get_video_queue(email=user.email, video_id=video.id) is None


async def test_get_video_queue_with_empty_queue(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(QUEUE, params={"index": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_video_queue_with_single_video(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    video_queue = await create_video_queue(email=user.email, video_id=video.id)
    response = await client.get(QUEUE, params={"index": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "description": video.description,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": False,
        "next": False,
    }


async def test_get_video_queue_with_next_video(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    next_video = await create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="2",
    )
    video_queue = await create_video_queue(email=user.email, video_id=video.id)
    await create_video_queue(email=user.email, video_id=next_video.id)
    response = await client.get(QUEUE, params={"index": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "description": video.description,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": False,
        "next": True,
    }


async def test_get_video_queue_with_prev_video(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    prev_video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    video = await create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="2",
    )
    await create_video_queue(email=user.email, video_id=prev_video.id)
    video_queue = await create_video_queue(email=user.email, video_id=video.id)
    response = await client.get(QUEUE, params={"index": 2})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "description": video.description,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": True,
        "next": False,
    }


async def test_get_video_queue_with_prev_and_next_videos(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    prev_video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    video = await create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="2",
    )
    next_video = await create_video(
        id="3",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="3",
    )
    await create_video_queue(email=user.email, video_id=prev_video.id)
    video_queue = await create_video_queue(email=user.email, video_id=video.id)
    await create_video_queue(email=user.email, video_id=next_video.id)
    response = await client.get(QUEUE, params={"index": 2})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "description": video.description,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": True,
        "next": True,
    }
