from datetime import datetime, timedelta
from fastapi import status
from httpx import AsyncClient
from pytest import MonkeyPatch

from dripdrop.settings import settings

CHANNELS_URL = "/api/youtube/channels"


async def test_get_channels_when_not_logged_in(client: AsyncClient):
    response = await client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_channels_with_non_existent_channel(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_channels(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
):
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    response = await client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
        "subscriptionId": None,
    }


async def test_get_channels_with_subscription(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    subscription = await create_subscription(
        id="1", channel_id=channel.id, email=user.email
    )
    response = await client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
        "subscriptionId": subscription.id,
    }


async def test_get_channels_with_deleted_subscription(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(
        id="1",
        channel_id=channel.id,
        email=user.email,
        deleted_at=datetime.now(settings.timezone),
    )
    response = await client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
        "subscriptionId": None,
    }


async def test_get_user_youtube_channel_when_not_logged_in(client: AsyncClient):
    response = await client.get(f"{CHANNELS_URL}/user")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_user_youtube_channel_with_non_existent_channel(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(f"{CHANNELS_URL}/user")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_user_youtube_channel(
    client: AsyncClient, create_and_login_user, create_user_channel
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    await create_user_channel(id="1", email=user.email)
    response = await client.get(f"{CHANNELS_URL}/user")
    assert response.json() == {"id": "1"}


async def test_update_user_channel_when_not_logged_in(client: AsyncClient):
    response = await client.post(f"{CHANNELS_URL}/user", json={"channel_id": "2"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_user_channel_with_no_channel(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.post(f"{CHANNELS_URL}/user", json={"channel_id": "2"})
    assert response.status_code == status.HTTP_200_OK


async def test_update_user_channel_with_existing_channel_within_day(
    client: AsyncClient,
    create_and_login_user,
    create_user_channel,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    await create_user_channel(id="1", email=user.email)
    response = await client.post(f"{CHANNELS_URL}/user", json={"channel_id": "2"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_update_user_channel_with_existing_channel(
    monkeypatch: MonkeyPatch,
    client: AsyncClient,
    create_and_login_user,
    create_user_channel,
    get_user_channel,
    mock_async,
):
    monkeypatch.setattr("dripdrop.rq.enqueue", mock_async)
    user = await create_and_login_user(email="user@gmail.com", password="password")
    await create_user_channel(
        id="1",
        email=user.email,
        modified_at=datetime.now(settings.timezone) - timedelta(days=2),
    )
    response = await client.post(f"{CHANNELS_URL}/user", json={"channel_id": "2"})
    assert response.status_code == status.HTTP_200_OK
    user_channel = await get_user_channel(email=user.email)
    assert user_channel.id == "2"
