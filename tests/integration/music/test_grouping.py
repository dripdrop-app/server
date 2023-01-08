import pytest
from fastapi import status
from fastapi.testclient import TestClient

GROUPING_URL = "/api/music/grouping"


@pytest.mark.noauth
def test_grouping_when_not_logged_in(client: TestClient):
    response = client.get(
        GROUPING_URL,
        params={"youtube_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_grouping_with_invalid_url(client: TestClient):
    response = client.get(GROUPING_URL, params={"youtube_url": "https://invalidurl"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_grouping_with_invalid_youtube_url(client: TestClient):
    response = client.get(
        GROUPING_URL,
        params={"youtube_url": "https://www.youtube.com/watch?v=fooddip"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_grouping_with_valid_youtube_url(client: TestClient):
    response = client.get(
        GROUPING_URL,
        params={"youtube_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["grouping"] == "Food Dip"
