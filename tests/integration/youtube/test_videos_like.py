from fastapi import status
from httpx import AsyncClient

LIKE = "/api/youtube/videos/like"


async def test_add_video_like_when_not_logged_in(client: AsyncClient):
    response = await client.put(LIKE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_add_video_like_with_no_google_account(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.put(LIKE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_add_video_like_with_non_existent_video(
    client: AsyncClient, create_and_login_user, create_google_account
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    response = await client.put(LIKE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_video_like(
    client: AsyncClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    get_video_like,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    google_account = await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(id="1", channel_id=channel.id, email=google_account.email)
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.put(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert (
        await get_video_like(email=google_account.email, video_id=video.id) is not None
    )


async def test_add_video_like_with_the_same_video(
    client: AsyncClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    google_account = await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(id="1", channel_id=channel.id, email=google_account.email)
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = await client.put(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = await client.put(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_delete_video_like_when_not_logged_in(client: AsyncClient):
    response = await client.delete(LIKE, params={"video_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_video_like_with_no_google_account(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.delete(LIKE, params={"video_id": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_delete_video_like_with_non_existent_video_like(
    client: AsyncClient, create_and_login_user, create_google_account
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    response = await client.delete(LIKE, params={"video_id": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_video_like(
    client: AsyncClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_like,
    get_video_like,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    google_account = await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    category = await create_video_category(id=1, name="category")
    video = await create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    await create_video_like(email=google_account.email, video_id=video.id)
    response = await client.delete(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert await get_video_like(email=google_account.email, video_id=video.id) is None
