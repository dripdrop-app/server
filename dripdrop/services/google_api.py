from dripdrop.services.http_client import http_client
from dripdrop.settings import settings
from dripdrop.logging import logger


YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


async def get_video_categories():
    params = {
        "key": settings.google_api_key,
        "part": "snippet",
        "regionCode": "US",
    }
    response = await http_client.get(
        f"{YOUTUBE_API_URL}/videoCategories", params=params
    )
    if response.is_success:
        json = response.json()
        return json.get("items", [])
    logger.warning(response.text)
    raise Exception("Failed to get video categories")


async def get_channel_info(channel_id: str = ...):
    params = {
        "part": "snippet",
        "maxResults": 1,
        "pageToken": "",
        "id": channel_id,
        "key": settings.google_api_key,
    }
    response = await http_client.get(f"{YOUTUBE_API_URL}/channels", params=params)
    if response.is_success:
        json = response.json()
        return json.get("items")[0]
    else:
        logger.warning(response.text)
        raise Exception("Failed to get channel information")


async def get_channel_subscriptions(channel_id: str = ...):
    params = {
        "part": "snippet",
        "maxResults": 50,
        "pageToken": "",
        "channelId": channel_id,
        "key": settings.google_api_key,
    }
    while params.get("pageToken") is not None:
        response = await http_client.get(
            f"{YOUTUBE_API_URL}/subscriptions", params=params
        )
        if response.is_success:
            json = response.json()
            yield json.get("items")
            params["pageToken"] = json.get("nextPageToken", None)
        else:
            logger.warning(response.text)
            raise Exception("Failed to get user subscriptions")
