import pytest
from fastapi import status
from fastapi.testclient import TestClient

SUBSCRIPTIONS_URL = "/api/youtube/subscriptions"


@pytest.mark.noauth
def test_subscriptions_when_not_logged_in(client: TestClient):
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.nogoogleauth
def test_subscriptions_with_no_google_account(client: TestClient):
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_subscriptions_with_no_results(client: TestClient):
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_subscriptions_out_of_range_page(
    client: TestClient, create_channel, create_subscription, test_email
):
    create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id="1", email=test_email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/2/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_subscriptions_with_single_result(
    client: TestClient, create_channel, create_subscription, test_email
):
    create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id="1", email=test_email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {"channelTitle": "channel", "channelThumbnail": "thumbnail"}
    ]
    assert json.get("totalPages") == 1


def test_subscriptions_with_multiple_pages(
    client: TestClient, create_channel, create_subscription, test_email
):
    create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id="1", email=test_email)
    create_subscription(id="2", channel_id="1", email=test_email)
    create_subscription(id="3", channel_id="1", email=test_email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/1")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {"channelTitle": "channel", "channelThumbnail": "thumbnail"}
    ]
    assert json.get("totalPages") == 3


def test_subscriptions_for_logged_in_google_account(
    client: TestClient, create_user, create_channel, create_subscription, test_email
):
    OTHER_USER_EMAIL = "otheruser@gmail.com"
    create_user(email=OTHER_USER_EMAIL, password="testpassword")
    create_channel(
        id="1", title="channel1", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id="1", email=test_email)
    create_channel(
        id="2", title="channel2", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="2", channel_id="2", email=OTHER_USER_EMAIL)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/2")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {"channelTitle": "channel1", "channelThumbnail": "thumbnail"}
    ]
    assert json.get("totalPages") == 1


def test_subscriptions_are_in_descending_order_by_title(
    client: TestClient, create_channel, create_subscription, test_email
):
    create_channel(
        id="1", title="channel1", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="1", channel_id="1", email=test_email)
    create_channel(
        id="2", title="channel2", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="2", channel_id="2", email=test_email)
    create_channel(
        id="3", title="channel3", thumbnail="thumbnail", upload_playlist_id="1"
    )
    create_subscription(id="3", channel_id="3", email=test_email)
    response = client.get(f"{SUBSCRIPTIONS_URL}/1/3")
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("subscriptions") == [
        {"channelTitle": "channel1", "channelThumbnail": "thumbnail"},
        {"channelTitle": "channel2", "channelThumbnail": "thumbnail"},
        {"channelTitle": "channel3", "channelThumbnail": "thumbnail"},
    ]
    assert json.get("totalPages") == 1
