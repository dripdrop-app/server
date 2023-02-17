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
    assert response.json() == {"totalPages": 0, "videos": []}


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
    assert response.json() == {"totalPages": 0, "videos": []}


def test_videos_with_channel_id(
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
    other_channel = create_channel(
        id="2", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    category = create_video_category(id=1, name="category")
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video(
        id="2",
        title="title",
        thumbnail="thumbnail",
        channel_id=other_channel.id,
        category_id=category.id,
    )
    response = client.get(f"{VIDEOS_URL}/1/10", params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": None,
            }
        ],
    }


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
    response = client.get(f"{VIDEOS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
                "channelId": channel.id,
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
    videos.sort(key=lambda video: video.published_at, reverse=True)
    response = client.get(f"{VIDEOS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                videos,
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
    videos.sort(key=lambda video: video.published_at, reverse=True)
    response = client.get(f"{VIDEOS_URL}/2/2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                videos[2:4],
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
    videos.sort(key=lambda video: video.published_at, reverse=True)
    response = client.get(f"{VIDEOS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                videos,
            )
        ),
    }


def test_videos_with_specific_video_category(
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
    other_category = create_video_category(id=2, name="other category")
    video_in_category = create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=other_category.id,
    )
    response = client.get(
        f"{VIDEOS_URL}/1/5", params={"video_categories": str(category.id)}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": video_in_category.id,
                "title": video_in_category.title,
                "thumbnail": video_in_category.thumbnail,
                "categoryId": category.id,
                "publishedAt": video_in_category.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": None,
                "watched": None,
            }
        ],
    }


def test_videos_with_queued_only(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
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
    create_subscription(id="1", channel_id=channel.id, email=google_account.email)
    category = create_video_category(id=1, name="category")
    queued_video = create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    queue = create_video_queue(email=google_account.email, video_id=queued_video.id)
    response = client.get(f"{VIDEOS_URL}/1/5", params={"queued_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": queued_video.id,
                "title": queued_video.title,
                "thumbnail": queued_video.thumbnail,
                "categoryId": category.id,
                "publishedAt": queued_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": None,
                "queued": queue.created_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "watched": None,
            }
        ],
    }


def test_videos_with_queued_only_in_ascending_order_by_created_date(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
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
    create_subscription(id="1", channel_id=channel.id, email=google_account.email)
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
    queues = list(
        map(
            lambda video: create_video_queue(
                email=google_account.email, video_id=video.id
            ),
            videos,
        )
    )
    queues.sort(key=lambda queue: queue.created_at)
    videos = list(
        map(
            lambda queue: next(
                filter(lambda video: video.id == queue.video_id, videos)
            ),
            queues,
        )
    )
    response = client.get(f"{VIDEOS_URL}/1/5", params={"queued_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda i: {
                    "id": videos[i].id,
                    "title": videos[i].title,
                    "thumbnail": videos[i].thumbnail,
                    "categoryId": category.id,
                    "publishedAt": videos[i]
                    .published_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": queues[i]
                    .created_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "watched": None,
                },
                range(len(videos)),
            )
        ),
    }


def test_videos_with_liked_only(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    create_video_like,
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
    liked_video = create_video(
        id="1",
        title="title_1",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    create_video(
        id="2",
        title="title_2",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    like = create_video_like(email=google_account.email, video_id=liked_video.id)
    response = client.get(f"{VIDEOS_URL}/1/5", params={"liked_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": [
            {
                "id": liked_video.id,
                "title": liked_video.title,
                "thumbnail": liked_video.thumbnail,
                "categoryId": category.id,
                "publishedAt": liked_video.published_at.replace(
                    tzinfo=settings.timezone
                ).isoformat(),
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
                "liked": like.created_at.replace(tzinfo=settings.timezone).isoformat(),
                "queued": None,
                "watched": None,
            }
        ],
    }


def test_videos_with_liked_only_in_descending_order_by_created_date(
    client: TestClient,
    create_and_login_user,
    create_google_account,
    create_channel,
    create_subscription,
    create_video_category,
    create_video,
    create_video_like,
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
    likes = list(
        map(
            lambda video: create_video_like(
                email=google_account.email, video_id=video.id
            ),
            videos,
        )
    )
    likes.sort(key=lambda like: like.created_at, reverse=True)
    videos = list(
        map(
            lambda like: next(
                filter(lambda video: video.id == like.video_id, videos), videos
            ),
            likes,
        )
    )
    response = client.get(f"{VIDEOS_URL}/1/5", params={"liked_only": True})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "totalPages": 1,
        "videos": list(
            map(
                lambda i: {
                    "id": videos[i].id,
                    "title": videos[i].title,
                    "thumbnail": videos[i].thumbnail,
                    "categoryId": category.id,
                    "publishedAt": videos[i]
                    .published_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": likes[i]
                    .created_at.replace(tzinfo=settings.timezone)
                    .isoformat(),
                    "queued": None,
                    "watched": None,
                },
                range(len(videos)),
            )
        ),
    }
