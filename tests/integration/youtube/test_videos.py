from datetime import datetime
from fastapi import status
from httpx import AsyncClient

from dripdrop.settings import settings

VIDEOS_URL = "/api/youtube/videos"


async def test_get_videos_when_not_logged_in(client: AsyncClient):
    response = await client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_videos_with_no_videos(client: AsyncClient, create_and_login_user):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"totalPages": 0, "videos": []}


async def test_get_videos_with_no_subscriptions(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"totalPages": 0, "videos": []}


async def test_get_videos_with_channel_id(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    other_channel = await create_channel(id="2", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    await create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=other_channel.id,
        category_id=category.id,
        description="2",
    )
    response = await client.get(f"{VIDEOS_URL}/1/10", params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
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
                "queued": None,
                "watched": None,
            }
        ],
    }


async def test_get_videos_with_out_of_range_page(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(f"{VIDEOS_URL}/2/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_videos_with_single_result(
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
    response = await client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
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
                "queued": None,
                "watched": None,
            }
        ],
    }


async def test_get_videos_with_multiple_videos(
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
    videos = []
    for i in range(5):
        videos.append(
            await create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
        )
    videos.sort(key=lambda video: video.published_at, reverse=True)
    response = await client.get(f"{VIDEOS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda video: {
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
                    "queued": None,
                    "watched": None,
                },
                videos,
            )
        ),
    }


async def test_get_videos_with_multiple_pages(
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
    videos = []
    for i in range(5):
        videos.append(
            await create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
        )
    videos.sort(key=lambda video: video.published_at, reverse=True)
    response = await client.get(f"{VIDEOS_URL}/2/2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 3,
        "videos": list(
            map(
                lambda video: {
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
                    "queued": None,
                    "watched": None,
                },
                videos[2:4],
            )
        ),
    }


async def test_get_videos_in_descending_order_by_published_date(
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
    videos = []
    for i in range(5):
        videos.append(
            await create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
        )
    videos.sort(key=lambda video: video.published_at, reverse=True)
    response = await client.get(f"{VIDEOS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda video: {
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
                    "queued": None,
                    "watched": None,
                },
                videos,
            )
        ),
    }


async def test_get_videos_with_deleted_subscriptions(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(
        channel_id=channel.id,
        email=user.email,
        deleted_at=datetime.now(settings.timezone),
    )
    category = await create_video_category(id=1, name="category")
    await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"totalPages": 0, "videos": []}


async def test_videos_with_watched_populated(
    client: AsyncClient,
    create_and_login_user,
    create_user,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    create_video_watch,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    other_user = await create_user(email="other@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(channel_id=channel.id, email=user.email)
    await create_subscription(channel_id=channel.id, email=other_user.email)
    category = await create_video_category(id=1, name="category")
    watched_video = await create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    other_video = await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="2",
    )
    watch = await create_video_watch(email=user.email, video_id=watched_video.id)
    await create_video_watch(email=other_user.email, video_id=other_video.id)
    response = await client.get(f"{VIDEOS_URL}/1/5")
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": other_video.id,
                "title": other_video.title,
                "thumbnail": other_video.thumbnail,
                "categoryId": category.id,
                "description": other_video.description,
                "publishedAt": other_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": None,
            },
            {
                "id": watched_video.id,
                "title": watched_video.title,
                "thumbnail": watched_video.thumbnail,
                "categoryId": category.id,
                "description": watched_video.description,
                "publishedAt": watched_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": watch.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            },
        ],
    }


async def test_get_videos_with_specific_video_category(
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
    other_category = await create_video_category(id=2, name="other category")
    video_in_category = await create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=other_category.id,
        description="2",
    )
    response = await client.get(
        f"{VIDEOS_URL}/1/5", params={"video_categories": str(category.id)}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": video_in_category.id,
                "title": video_in_category.title,
                "thumbnail": video_in_category.thumbnail,
                "categoryId": category.id,
                "description": video_in_category.description,
                "publishedAt": video_in_category.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": None,
            }
        ],
    }


async def test_get_videos_with_queued_only(
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
    queued_video = await create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="2",
    )
    queue = await create_video_queue(email=user.email, video_id=queued_video.id)
    response = await client.get(f"{VIDEOS_URL}/1/5", params={"queued_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": queued_video.id,
                "title": queued_video.title,
                "thumbnail": queued_video.thumbnail,
                "categoryId": category.id,
                "description": queued_video.description,
                "publishedAt": queued_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": queue.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "watched": None,
            }
        ],
    }


async def test_get_videos_with_queued_only_in_ascending_order_by_created_date(
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
    videos = []
    for i in range(5):
        videos.append(
            await create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
        )
    queues = []
    for video in videos:
        queues.append(await create_video_queue(email=user.email, video_id=video.id))
    queues.sort(key=lambda queue: queue.created_at)
    videos = list(
        map(
            lambda queue: next(
                filter(lambda video: video.id == queue.video_id, videos)
            ),
            queues,
        )
    )
    response = await client.get(f"{VIDEOS_URL}/1/5", params={"queued_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda i: {
                    "id": videos[i].id,
                    "title": videos[i].title,
                    "thumbnail": videos[i].thumbnail,
                    "categoryId": category.id,
                    "description": videos[i].description,
                    "publishedAt": videos[i]
                    .published_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": queues[i]
                    .created_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "watched": None,
                },
                range(len(videos)),
            )
        ),
    }


async def test_get_videos_with_liked_only(
    client: AsyncClient,
    create_and_login_user,
    create_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_like,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    other_user = await create_user(email="other@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    liked_video = await create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="1",
    )
    other_liked_video = await create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
        description="2",
    )
    like = await create_video_like(email=user.email, video_id=liked_video.id)
    await create_video_like(email=other_user.email, video_id=other_liked_video.id)
    response = await client.get(f"{VIDEOS_URL}/1/5", params={"liked_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": liked_video.id,
                "title": liked_video.title,
                "thumbnail": liked_video.thumbnail,
                "categoryId": category.id,
                "description": liked_video.description,
                "publishedAt": liked_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": like.created_at.replace(tzinfo=settings.timezone).isoformat(),
                "queued": None,
                "watched": None,
            }
        ],
    }


async def test_get_videos_with_liked_only_in_descending_order_by_created_date(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_video_category,
    create_video,
    create_video_like,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    videos = []
    for i in range(5):
        videos.append(
            await create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
        )
    likes = []
    for video in videos:
        likes.append(await create_video_like(email=user.email, video_id=video.id))
    likes.sort(key=lambda like: like.created_at, reverse=True)
    videos = list(
        map(
            lambda like: next(
                filter(lambda video: video.id == like.video_id, videos), videos
            ),
            likes,
        )
    )
    response = await client.get(f"{VIDEOS_URL}/1/5", params={"liked_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda i: {
                    "id": videos[i].id,
                    "title": videos[i].title,
                    "thumbnail": videos[i].thumbnail,
                    "categoryId": category.id,
                    "description": videos[i].description,
                    "publishedAt": videos[i]
                    .published_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": likes[i]
                    .created_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "queued": None,
                    "watched": None,
                },
                range(len(videos)),
            )
        ),
    }
