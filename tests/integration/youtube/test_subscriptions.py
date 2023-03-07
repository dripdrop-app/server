from datetime import datetime
from fastapi import status
from httpx import AsyncClient
from pytest import MonkeyPatch

from dripdrop.settings import settings

SUBSCRIPTIONS_URL = "/api/youtube/subscriptions"


async def test_get_subscriptions_when_not_logged_in(client: AsyncClient):
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_subscriptions_with_no_results(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"totalPages": 0, "subscriptions": []}


async def test_get_subscriptions_out_of_range_page(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    await create_subscription(id="1", channel_id=channel.id, email=user.email)
    response = await client.get(f"{SUBSCRIPTIONS_URL}/2/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_subscriptions_with_single_result(
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
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "subscriptions": [
            {
                "id": subscription.id,
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "publishedAt": subscription.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


async def test_get_subscriptions_with_deleted_subscription(
    client: AsyncClient, create_and_login_user, create_channel, create_subscription
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(id="1", title="channel", thumbnail="thumbnail")
    other_channel = await create_channel(
        id="2", title="channel_2", thumbnail="thumbnail"
    )
    subscription = await create_subscription(
        id="1", channel_id=channel.id, email=user.email
    )
    await create_subscription(
        id="2",
        channel_id=other_channel.id,
        email=user.email,
        deleted_at=datetime.now(settings.timezone),
    )
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "subscriptions": [
            {
                "id": subscription.id,
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "publishedAt": subscription.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


async def test_get_subscriptions_with_multiple_pages(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channels = []
    for i in range(3):
        channels.append(
            await create_channel(
                id=str(i),
                title=f"channel_{i}",
                thumbnail="thumbnail",
            )
        )
    subscriptions = []
    for i, channel in enumerate(channels):
        subscriptions.append(
            await create_subscription(
                id=str(i), channel_id=channel.id, email=user.email
            )
        )
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 3,
        "subscriptions": [
            {
                "id": subscriptions[0].id,
                "channelId": channels[0].id,
                "channelTitle": channels[0].title,
                "channelThumbnail": channels[0].thumbnail,
                "publishedAt": subscriptions[0]
                .published_at.replace(tzinfo=settings.timezone)
                .isoformat(),
            }
        ],
    }


async def test_get_subscriptions_for_logged_in_account(
    client: AsyncClient,
    create_and_login_user,
    create_user,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    other_user = await create_user(email="otheruser@gmail.com", password="password")
    channel = await create_channel(
        id="1",
        title="channel_1",
        thumbnail="thumbnail",
    )
    other_channel = await create_channel(
        id="2",
        title="channel_2",
        thumbnail="thumbnail",
    )
    await create_subscription(
        id="1", channel_id=other_channel.id, email=other_user.email
    )
    subscription = await create_subscription(
        id="2", channel_id=channel.id, email=user.email
    )
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "subscriptions": [
            {
                "id": subscription.id,
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "publishedAt": subscription.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
            }
        ],
    }


async def test_get_subscriptions_are_in_descending_order_by_title(
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channels = []
    for i in range(3):
        channels.append(
            await create_channel(
                id=str(i),
                title=f"channel_{i}",
                thumbnail="thumbnail",
            )
        )
    subscriptions = []
    for i, channel in enumerate(channels):
        subscriptions.append(
            await create_subscription(
                id=str(i), channel_id=channel.id, email=user.email
            )
        )
    channels.sort(key=lambda channel: channel.title)
    subscriptions = list(
        map(
            lambda channel: next(
                filter(
                    lambda subscription: channel.id == subscription.channel_id,
                    subscriptions,
                )
            ),
            channels,
        )
    )
    response = await client.get(f"{SUBSCRIPTIONS_URL}/1/3")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "subscriptions": list(
            map(
                lambda i: {
                    "id": subscriptions[i].id,
                    "channelId": channels[i].id,
                    "channelTitle": channels[i].title,
                    "channelThumbnail": channels[i].thumbnail,
                    "publishedAt": subscriptions[i]
                    .published_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                },
                range(len(subscriptions)),
            )
        ),
    }


async def test_add_user_subscription_when_not_logged_in(client: AsyncClient):
    response = await client.put(f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_add_user_subscription_with_non_existent_channel_in_database(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.put(f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_user_subscription_with_channel_in_database(
    monkeypatch: MonkeyPatch,
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    mock_async,
):
    monkeypatch.setattr("dripdrop.rq.enqueue", mock_async)
    await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(
        id="1",
        title="channel_1",
        thumbnail="thumbnail",
    )
    response = await client.put(
        f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
    )
    assert response.status_code == status.HTTP_200_OK
    subscription = response.json()
    assert subscription["id"] is not None
    assert subscription["channelId"] == channel.id
    assert subscription["channelTitle"] == channel.title
    assert subscription["channelThumbnail"] == channel.thumbnail
    assert subscription["publishedAt"] is not None


async def test_add_user_subscription_with_nonexistent_channel_on_youtube(
    monkeypatch: MonkeyPatch, client: AsyncClient, create_and_login_user
):
    async def fake_channel(channel_id: str = ...):
        raise Exception("Not Found")

    monkeypatch.setattr(
        "dripdrop.services.google_api.google_api.get_channel_info", fake_channel
    )
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.put(f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_user_subscription_with_channel_on_youtube(
    monkeypatch: MonkeyPatch, client: AsyncClient, create_and_login_user
):
    async def nothing():
        return None

    async def fake_channel(channel_id: str = ...):
        return {
            "id": channel_id,
            "snippet": {
                "title": "channel",
                "thumbnails": {"high": {"url": "thumbnail"}},
            },
        }

    monkeypatch.setattr("dripdrop.rq.enqueue", nothing)
    monkeypatch.setattr(
        "dripdrop.services.google_api.google_api.get_channel_info", fake_channel
    )
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.put(f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    subscription = response.json()
    assert subscription["id"] is not None
    assert subscription["channelId"] == "1"
    assert subscription["channelTitle"] == "channel"
    assert subscription["channelThumbnail"] == "thumbnail"
    assert subscription["publishedAt"] is not None


async def test_add_user_subscription_when_subscription_exists(
    client: AsyncClient, create_and_login_user, create_channel, create_subscription
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(
        id="1",
        title="channel_1",
        thumbnail="thumbnail",
    )
    await create_subscription(id="1", channel_id=channel.id, email=user.email)
    response = await client.put(
        f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_add_user_subscription_with_deleted_subscription(
    monkeypatch: MonkeyPatch,
    client: AsyncClient,
    create_and_login_user,
    create_channel,
    create_subscription,
    mock_async,
):
    monkeypatch.setattr("dripdrop.rq.enqueue", mock_async)
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(
        id="1",
        title="channel_1",
        thumbnail="thumbnail",
    )
    await create_subscription(
        id="1",
        channel_id=channel.id,
        email=user.email,
        deleted_at=datetime.now(settings.timezone),
    )
    response = await client.put(
        f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
    )
    assert response.status_code == status.HTTP_200_OK
    subscription = response.json()
    assert subscription["id"] is not None
    assert subscription["channelId"] == channel.id
    assert subscription["channelTitle"] == channel.title
    assert subscription["channelThumbnail"] == channel.thumbnail
    assert subscription["publishedAt"] is not None


async def test_delete_user_subscription_when_not_logged_in(client: AsyncClient):
    response = await client.delete(
        f"{SUBSCRIPTIONS_URL}/user", params={"subscription_id": "1"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_user_subscription_with_nonexistent_subscription(
    client: AsyncClient, create_and_login_user
):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.delete(
        f"{SUBSCRIPTIONS_URL}/user", params={"subscription_id": "1"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_user_subscription(
    client: AsyncClient, create_and_login_user, create_channel, create_subscription
):
    user = await create_and_login_user(email="user@gmail.com", password="password")
    channel = await create_channel(
        id="1",
        title="channel_1",
        thumbnail="thumbnail",
    )
    subscription = await create_subscription(
        id="1", channel_id=channel.id, email=user.email
    )
    response = await client.delete(
        f"{SUBSCRIPTIONS_URL}/user", params={"subscription_id": subscription.id}
    )
    assert response.status_code == status.HTTP_200_OK
