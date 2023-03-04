from fastapi import status
from httpx import AsyncClient

WATCH = "/api/youtube/videos/watch"


async def test_add_video_watch_when_not_logged_in(client: AsyncClient):
    response = await client.put(WATCH, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_add_video_watch_with_non_existent_video(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.put(WATCH, params={"video_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_video_watch(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    get_video_watch,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(id="1", channel_id=channel.id, email=user.email)
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.put(WATCH, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert await get_video_watch(email=user.email, video_id=video.id) is not None


async def test_add_video_watch_with_the_same_video(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(id="1", channel_id=channel.id, email=user.email)
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.put(WATCH, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = await client.put(WATCH, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
