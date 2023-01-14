import pytest
from fastapi import status
from fastapi.testclient import TestClient

CHANNELS_URL = "/api/youtube/channels"


@pytest.mark.noauth
def test_channels_when_not_logged_in(client: TestClient):
    response = client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.nogoogleauth
def test_channels_with_no_google_account(client: TestClient):
    response = client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_channels_with_non_existent_channel(client: TestClient):
    response = client.get(CHANNELS_URL, params={"channel_id": "test"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_channels_with_existing_channel(client: TestClient, create_channel):
    create_channel(
        id="1", title="channel", thumbnail="thumbnail", upload_playlist_id="1"
    )
    response = client.get(CHANNELS_URL, params={"channel_id": "1"})
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json.get("title") == "channel"
    assert json.get("thumbnail") == "thumbnail"
