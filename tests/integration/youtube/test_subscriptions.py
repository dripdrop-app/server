from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.settings import settings

SUBSCRIPTIONS_URL = "/api/youtube/subscriptions"


def test_subscriptions_when_not_logged_in(client: TestClient):
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_subscriptions_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_subscriptions_with_no_results(
    client: TestClient, create_and_login_user, create_google_account
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_subscriptions_out_of_range_page(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_user.email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/2/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_subscriptions_with_single_result(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    subscription = create_subscription(
        id="1", channel_id=channel.id, email=google_user.email
    )
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "publishedAt": subscription.published_at.replace(
                tzinfo=settings.test_timezone
            ).isoformat(),
        }
    ]
    assert json.get("totalPages") == 1


def test_subscriptions_with_multiple_pages(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    channels = list(
        map(
            lambda i: create_channel(
                id=str(i),
                title=f"channel_{i}",
                thumbnail="thumbnail",
                upload_playlist_id="1",
            ),
            range(3),
        )
    )
    subscriptions = [
        create_subscription(id=str(i), channel_id=channel.id, email=google_user.email)
        for i, channel in enumerate(channels)
    ]
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {
            "channelId": channels[0].id,
            "channelTitle": channels[0].title,
            "channelThumbnail": channels[0].thumbnail,
            "publishedAt": subscriptions[0]
            .published_at.replace(tzinfo=settings.test_timezone)
            .isoformat(),
        }
    ]
    assert json.get("totalPages") == 3


def test_subscriptions_for_logged_in_google_account(
    client: TestClient,
    create_and_login_user,
    create_user,
    create_google_account,
    create_channel,
    create_subscription,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    other_user = create_user(email="otheruser@gmail.com", password="password")
    other_google_user = create_google_account(
        email="othergoogle@gmail.com",
        user_email=other_user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel_1", thumbnail="thumbnail", upload_playlist_id="1"
    )
    other_channel = create_channel(
        id="2", title="channel_2", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(
        id="1", channel_id=other_channel.id, email=other_google_user.email
    )
    subscription = create_subscription(
        id="2", channel_id=channel.id, email=google_user.email
    )
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/2")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "publishedAt": subscription.published_at.replace(
                tzinfo=settings.test_timezone
            ).isoformat(),
        }
    ]
    assert json.get("totalPages") == 1


def test_subscriptions_are_in_descending_order_by_title(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    channels = list(
        map(
            lambda i: create_channel(
                id=str(i),
                title=f"channel_{i}",
                thumbnail="thumbnail",
                upload_playlist_id="1",
            ),
            range(3),
        )
    )
    subscriptions = [
        create_subscription(id=str(i), channel_id=channel.id, email=google_user.email)
        for i, channel in enumerate(channels)
    ]
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/3")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == list(
        map(
            lambda i: {
                "channelId": channels[i].id,
                "channelTitle": channels[i].title,
                "channelThumbnail": channels[i].thumbnail,
                "publishedAt": subscriptions[i]
                .published_at.replace(tzinfo=settings.test_timezone)
                .isoformat(),
            },
            range(len(channels)),
        )
    )
    assert json.get("totalPages") == 1
