from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.settings import settings

QUEUE = "/api/youtube/videos/queue"


def test_add_video_queue_when_not_logged_in(client: TestClient):
    response = client.put(QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_video_queue_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.put(QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_video_queue_with_non_existent_video(
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
    response = client.put(QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_video_queue(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    get_video_queue,
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
    response = client.put(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert get_video_queue(email=google_account.email, video_id=video.id) is not None


def test_add_video_queue_with_the_same_video(
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
    response = client.put(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = client.put(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_video_queue_when_not_logged_in(client: TestClient):
    response = client.delete(QUEUE, params={"video_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_video_queue_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.delete(QUEUE, params={"video_id": 1})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_video_queue_with_non_existent_video_queue(
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
    response = client.delete(QUEUE, params={"video_id": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_video_queue(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
    get_video_queue,
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
    create_video_queue(email=google_account.email, video_id=video.id)
    response = client.delete(QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    assert get_video_queue(email=google_account.email, video_id=video.id) is None


def test_get_video_queue_with_empty_queue(
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
    response = client.get(QUEUE, params={"index": 1})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_video_queue_with_single_video(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
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
    video_queue = create_video_queue(email=google_account.email, video_id=video.id)
    response = client.get(QUEUE, params={"index": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": False,
        "next": False,
    }


def test_get_video_queue_with_next_video(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
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
    next_video = create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    video_queue = create_video_queue(email=google_account.email, video_id=video.id)
    create_video_queue(email=google_account.email, video_id=next_video.id)
    response = client.get(QUEUE, params={"index": 1})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": False,
        "next": True,
    }


def test_get_video_queue_with_prev_video(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
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
    prev_video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    video = create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video_queue(email=google_account.email, video_id=prev_video.id)
    video_queue = create_video_queue(email=google_account.email, video_id=video.id)
    response = client.get(QUEUE, params={"index": 2})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": True,
        "next": False,
    }


def test_get_video_queue_with_prev_and_next_videos(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
    create_video_queue,
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
    prev_video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    video = create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    next_video = create_video(
        id="3",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video_queue(email=google_account.email, video_id=prev_video.id)
    video_queue = create_video_queue(email=google_account.email, video_id=video.id)
    create_video_queue(email=google_account.email, video_id=next_video.id)
    response = client.get(QUEUE, params={"index": 2})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "currentVideo": {
            "id": video.id,
            "title": video.title,
            "thumbnail": video.thumbnail,
            "categoryId": category.id,
            "publishedAt": video.published_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "channelId": channel.id,
            "channelTitle": channel.title,
            "channelThumbnail": channel.thumbnail,
            "liked": None,
            "queued": video_queue.created_at.replace(
                tzinfo=settings.timezone
            ).isoformat(),
            "watched": None,
        },
        "prev": True,
        "next": True,
    }
