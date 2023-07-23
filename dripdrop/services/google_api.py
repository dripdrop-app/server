import asyncio
import traceback
from bs4 import BeautifulSoup
from dataclasses import dataclass

from dripdrop.logger import logger
from dripdrop.services import http_client
from dripdrop.settings import settings


@dataclass
class YoutubeChannelInfo:
    id: str
    title: str
    thumbnail: str


YOUTUBE_API = "https://youtube.googleapis.com/youtube/v3"


async def get_channel_subscriptions(channel_id: str):
    params = {"part": "snippet", "channelId": channel_id}
    async with http_client.create_client() as client:
        params = {"part": "snippet", "channelId": channel_id}
        while True:
            response = await client.get(
                f"{YOUTUBE_API}/subscriptions",
                params=params,
                headers={"Authorization": f"Bearer {settings.google_api_key}"},
            )
            response.raise_for_status()
            json = response.json()
            channels = []
            for item in json.get("items", []):
                snippet = item.get("snippet")
                resource_id = snippet.get("resourceId")
                channel_id = resource_id.get("channelId")
                channel_title = snippet.get("title")
                thumbnails = snippet.get("thumbnails")
                channel_thumbnail = thumbnails.get("high", {}).get("url")
                try:
                    channels.append(
                        YoutubeChannelInfo(
                            id=channel_id,
                            title=channel_title,
                            thumbnail=channel_thumbnail,
                        )
                    )
                except TypeError:
                    logger.exception(traceback.format_exc())
            params["pageToken"] = json.get("nextPageToken")
            if params.get("pageToken", None) is None:
                break
            await asyncio.sleep(1)


async def get_channel_info(channel_id: str):
    url = "https://www.youtube.com/"
    if channel_id.startswith("@"):
        url += channel_id
    else:
        url += f"channel/{channel_id}"
    async with http_client.create_client() as client:
        response = await client.get(url=url)
        if response.is_error:
            return None
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        channel_id_tag = soup.find("meta", itemprop="identifier")
        if not channel_id_tag:
            channel_id_tag = soup.find("meta", itemprop="channelId")
        name_tag = soup.find("meta", itemprop="name")
        thumbnail_tag = soup.find("link", itemprop="thumbnailUrl")
        try:
            return YoutubeChannelInfo(
                id=channel_id_tag["content"],
                title=name_tag["content"],
                thumbnail=thumbnail_tag["href"],
            )
        except TypeError:
            return None
