from dripdrop.services.http_client import create_http_client
from dripdrop.settings import settings
from dripdrop.logging import logger


YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


async def get_video_categories():
    params = {
        "key": settings.google_api_key,
        "part": "snippet",
        "regionCode": "US",
    }
    async with create_http_client() as http_client:
        response = await http_client.get(
            f"{YOUTUBE_API_URL}/videoCategories", params=params
        )
    if response.is_success:
        json = response.json()
        return json.get("items", [])
    logger.warning(response.text)
    raise Exception("Failed to get video categories")
