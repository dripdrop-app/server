from dripdrop.http_client import http_client
from dripdrop.settings import settings
from dripdrop.logging import logger


class GoogleAPI:
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.base_headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/51.0.2704.103 Safari/537.36"
            )
        }

    async def get_video_categories(self):
        params = {
            "key": settings.google_api_key,
            "part": "snippet",
            "regionCode": "US",
        }
        response = await http_client.get(
            f"{GoogleAPI.YOUTUBE_API_URL}/videoCategories",
            params=params,
            headers=self.base_headers,
        )
        if response.is_success:
            json = response.json()
            return json.get("items", [])
        logger.warning(response.text)
        raise Exception("Failed to get video categories")

    async def get_channel_subscriptions(self, channel_id: str = ...):
        params = {
            "part": "snippet",
            "mine": True,
            "maxResults": 50,
            "pageToken": "",
            "channelId": channel_id,
            "key": settings.google_api_key,
        }
        while params.get("pageToken") is not None:
            response = await http_client.get(
                f"{GoogleAPI.YOUTUBE_API_URL}/subscriptions",
                params=params,
                headers=self.base_headers,
            )
            if response.is_success:
                json = response.json()
                yield json.get("items")
                params["pageToken"] = json.get("nextPageToken", None)
            else:
                logger.warning(response.text)
                raise Exception("Failed to get user subscriptions")


google_api = GoogleAPI()
