from fastapi import status
from httpx import AsyncClient

CHANNELS_URL = "/api/youtube/channels"


async def test_channels_when_not_logged_in(client: AsyncClient):
    response = await client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_channels_with_no_google_account(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_channels_with_non_existent_channel(
    client: AsyncClient, create_and_login_user, create_google_account
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    response = await client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_channels(
    client: AsyncClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    google_account = await create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    channel = await create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    await create_subscription(id="1", channel_id=channel.id, email=google_account.email)
    response = await client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
    }
