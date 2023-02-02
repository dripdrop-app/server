from fastapi import status
from fastapi.testclient import TestClient

from dripdrop.settings import settings

ADD_QUEUE = "/api/youtube/videos/queue"


def test_add_video_queue_when_not_logged_in(client: TestClient):
    response = client.put(ADD_QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_video_queue_with_no_google_account(
    client: TestClient, create_and_login_user
):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.put(ADD_QUEUE, params={"video_id": "1"})
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
    response = client.put(ADD_QUEUE, params={"video_id": "1"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_video_queue(
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
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = client.put(ADD_QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK


def test_add_video_queue_with_the_same_video(
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
    video = create_video(
        id="1",
        title="title",
        thumbnail="thumbnail",
        channel_id=channel.id,
        category_id=category.id,
    )
    response = client.put(ADD_QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_200_OK
    response = client.put(ADD_QUEUE, params={"video_id": video.id})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
