import re
import requests
from fastapi import status
from fastapi.testclient import TestClient

from ...conftest import APIEndpoints


class MusicEndpoints:
    base_url = f"{APIEndpoints.base_path}/music"
    grouping = f"{base_url}/grouping"
    artwork = f"{base_url}/artwork"
    tags = f"{base_url}/tags"


class TestGrouping:
    def test_grouping_with_invalid_url(self, client: TestClient):
        response = client.get(
            MusicEndpoints.grouping, params={"youtube_url": "https://invalidurl"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_grouping_with_invalid_youtube_url(self, client: TestClient):
        response = client.get(
            MusicEndpoints.grouping,
            params={"youtube_url": "https://www.youtube.com/watch?v=fooddip"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_grouping_with_valid_youtube_url(self, client: TestClient):
        response = client.get(
            MusicEndpoints.grouping,
            params={"youtube_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
        )
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert json["grouping"] == "Food Dip"


class TestArtwork:
    def test_artwork_with_invalid_url(self, client: TestClient):
        response = client.get(
            MusicEndpoints.artwork, params={"artwork_url": "https://invalidurl"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_artwork_with_valid_image_url(self, client: TestClient):
        artwork_url = (
            "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )
        response = client.get(
            MusicEndpoints.artwork,
            params={"artwork_url": artwork_url},
        )
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert (
            json["artworkUrl"]
            == "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )

    def test_artwork_with_valid_soundcloud_url(self, client: TestClient):
        response = client.get(
            MusicEndpoints.artwork,
            params={
                "artwork_url": "https://soundcloud.com/badbunny15/bad-bunny-buscabulla-andrea"
            },
        )
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        assert (
            json["artworkUrl"]
            == "https://i1.sndcdn.com/artworks-ExnE7PpUZSJl-0-t500x500.jpg"
        )


class TestTags:
    def check_tag_response(
        self, json=..., title=..., artist=..., album=..., grouping=...
    ):
        assert json["title"] == title
        assert json["artist"] == artist
        assert json["album"] == album
        assert json["grouping"] == grouping

    def test_tags_with_an_invalid_file(self, client: TestClient):
        response = requests.get(
            "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )
        file = response.content
        response = client.post(MusicEndpoints.tags, files={"file": file})
        assert response.status_code == status.HTTP_200_OK
        self.check_tag_response(
            json=response.json(),
            title=None,
            artist=None,
            album=None,
            grouping=None,
        )

    def test_tags_with_a_mp3_without_tags(self, client: TestClient):
        response = requests.get(
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/sample4.mp3"
        )
        file = response.content
        response = client.post(MusicEndpoints.tags, files={"file": file})
        assert response.status_code == status.HTTP_200_OK
        self.check_tag_response(
            json=response.json(),
            title=None,
            artist=None,
            album=None,
            grouping=None,
        )

    def test_tags_with_a_valid_mp3_file(self, client: TestClient):
        response = requests.get(
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/"
            + "test/Criminal%20Sinny%20&%20Fako.mp3"
        )
        file = response.content
        response = client.post(MusicEndpoints.tags, files={"file": file})
        assert response.status_code == status.HTTP_200_OK
        json = response.json()
        self.check_tag_response(
            json=json,
            title="Criminal",
            artist="Sinny & Fako",
            album="Criminal - Single",
            grouping="Tribal Trap",
        )
        assert re.match(r"data:image/[a-zA-Z]+;base64,", json["artworkUrl"]) is not None
