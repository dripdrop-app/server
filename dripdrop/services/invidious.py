from dataclasses import dataclass, field
from urllib.parse import urljoin

from dripdrop.services import http_client


@dataclass
class ChannelVideosResponse:
    videos: list[dict]
    continuation: str | None = field(default=None)


async def get_instance_url():
    async with http_client.create_client() as client:
        response = await client.get(
            "https://api.invidious.io/instances.json", params={"sort_by": "type,users"}
        )
        if response.is_error:
            raise Exception("Unable to retrieve instance")
        instances = response.json()
        return f"https://{instances[0][0]}"


async def get_youtube_channel_videos(channel_id: str, continuation_token: str = None):
    instance_url = await get_instance_url()
    params = {}
    if continuation_token:
        params["continuation"] = continuation_token
    async with http_client.create_client() as client:
        response = await client.get(
            urljoin(instance_url, f"/api/v1/channels/{channel_id}/videos"),
            params=params,
        )
        if response.is_error:
            raise Exception("Failed to retrieve videos")
        return ChannelVideosResponse(**response.json())
