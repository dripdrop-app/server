from fastapi import status
from fastapi.testclient import TestClient

WATCH = "/api/youtube/videos/watch"


def test_add_video_watch_when_not_logged_in(client: TestClient):
    response = client.put(WATCH, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_video_watch_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.put(WATCH, params={"video_id": "1"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_video_watch_with_non_existent_video(
    client: TestClient, create_and_login_user, create_google_account
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    response = client.put(WATCH, params={"video_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_video_watch(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    get_video_watch,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_account = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_account.email)
    category = create_video_category(id=1, name="category")
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = client.put(WATCH, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert get_video_watch(email=google_account.email, video_id=video.id) is not None


def test_add_video_watch_with_the_same_video(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_account = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_account.email)
    category = create_video_category(id=1, name="category")
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = client.put(WATCH, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = client.put(WATCH, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
