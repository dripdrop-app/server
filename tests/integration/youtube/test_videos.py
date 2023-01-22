import time
from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.settings import settings

VIDEOS_URL = "/api/youtube/videos"


def test_videos_when_not_logged_in(client: TestClient):
    response = client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_videos_with_no_google_account(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_videos_with_no_videos(
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
    response = client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {"totalPages": 0, "videos": []}


def test_videos_with_no_subscriptions(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_video_category,
    create_video,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    create_google_account(
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
    create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {"totalPages": 0, "videos": []}


def test_videos_with_out_of_range_page(
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
    response = client.get(f"{VIDEOS_URL}/2/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_videos_with_single_result(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_user.email)
    category = create_video_category(id=1, name="category")
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {
        "totalPages": 1,
        "videos": [
            {
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "categoryId": category.id,
                "publishedAt": video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": None,
            }
        ],
    }


def test_videos_with_multiple_videos(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_user.email)
    category = create_video_category(id=1, name="category")
    videos = list(
        map(
            lambda i: create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
            ),
            range(5),
        )
    )
    response = client.get(f"{VIDEOS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda video: {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                videos[::-1],
            )
        ),
    }


def test_videos_with_multiple_pages(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_user.email)
    category = create_video_category(id=1, name="category")
    videos = list(
        map(
            lambda i: create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
            ),
            range(5),
        )
    )
    response = client.get(f"{VIDEOS_URL}/1/2")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {
        "totalPages": 3,
        "videos": list(
            map(
                lambda video: {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                videos[4:2:-1],
            )
        ),
    }


def test_videos_in_descending_order_by_published_date(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
):
    user = create_and_login_user(email="user@gmail.com", password="password")
    google_user = create_google_account(
        email="google@gmail.com",
        user_email=user.email,
        access_token="access",
        refresh_token="refresh",
        expires=1000,
    )
    channel = create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id=channel.id, email=google_user.email)
    category = create_video_category(id=1, name="category")
    videos = []
    for i in range(5):
        videos.append(
            create_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
            )
        )
        time.sleep(1)
    response = client.get(f"{VIDEOS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda video: {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                videos[::-1],
            )
        ),
    }
