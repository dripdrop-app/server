from fastapi import status
from fastapi.testclient import TestClient

CHANNELS_URL = "/api/youtube/channels"


def test_channels_when_not_logged_in(client: TestClient):
    response = client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_channels_with_no_google_account(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_channels_with_non_existent_channel(
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
    response = client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_channels_with_unsubscribed_channel(
    client: TestClient, create_and_login_user, create_google_account, create_channel
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="",
        refresh_token="",
        expires=1000,
    )
    create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    response = client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_channels_with_subscribed_channel(
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
    response = client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": channel.id,
        "title": channel.title,
        "thumbnail": channel.thumbnail,
    }
