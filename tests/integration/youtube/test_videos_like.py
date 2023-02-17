from fastapi import status
from fastapi.testclient import TestClient

LIKE = "/api/youtube/videos/like"


def test_add_video_like_when_not_logged_in(client: TestClient):
    response = client.put(LIKE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_video_like_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.put(LIKE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_video_like_with_non_existent_video(
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
    response = client.put(LIKE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_video_like(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    get_video_like,
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
    response = client.put(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert get_video_like(email=google_account.email, video_id=video.id) is not None


def test_add_video_like_with_the_same_video(
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
    response = client.put(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = client.put(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_video_like_when_not_logged_in(client: TestClient):
    response = client.delete(LIKE, params={"video_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_video_like_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.delete(LIKE, params={"video_id": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_video_like_with_non_existent_video_like(
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
    response = client.delete(LIKE, params={"video_id": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_video_like(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_like,
    get_video_like,
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
    category = create_video_category(id=1, name="category")
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video_like(email=google_account.email, video_id=video.id)
    response = client.delete(LIKE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert get_video_like(email=google_account.email, video_id=video.id) is None
