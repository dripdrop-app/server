from fastapi import status
from fastapi.testclient import TestClient

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
    create_subscription(id="1", channel_id=channel.id, email=google_user.email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {"channelTitle": channel.title, "channelThumbnail": channel.thumbnail}
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
                id=i,
                title=f"channel_{i}",
                thumbnail="thumbnail",
                upload_playlist_id="1",
            ),
            range(3),
        )
    )
    for i, channel in enumerate(channels):
        create_subscription(id=i, channel_id=channel.id, email=google_user.email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {"channelTitle": channels[0].title, "channelThumbnail": channels[0].thumbnail}
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
    channels = list(
        map(
            lambda i: create_channel(
                id=i,
                title=f"channel_{i}",
                thumbnail="thumbnail",
                upload_playlist_id="1",
            ),
            range(2),
        )
    )
    create_subscription(id=2, channel_id=channels[1].id, email=other_google_user.email)
    create_subscription(id=1, channel_id=channels[0].id, email=google_user.email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/2")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {
            "channelTitle": channels[0].title,
            "channelThumbnail": channels[0].thumbnail,
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
                id=i,
                title=f"channel_{i}",
                thumbnail="thumbnail",
                upload_playlist_id="1",
            ),
            range(3),
        )
    )
    for i, channel in enumerate(channels):
        create_subscription(id=i, channel_id=channel.id, email=google_user.email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/3")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == list(
        map(
            lambda channel: {
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
            },
            channels,
        )
    )
    assert json.get("totalPages") == 1
