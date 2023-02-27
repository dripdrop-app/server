import os
from httpx import Response
from urllib import parse

from dripdrop.http_client import http_client


class ImageDownloader:
    def __init__(self):
        self.image_extensions = [".jpg", ".ico", "png", ".jpeg"]

    def _is_image_link(self, response: Response = ...):
        content_type = response.headers.get("Content-Type", None)
        if content_type and content_type.split("/")[0] == "image":
            return True
        return None

    async def download_image(self, artwork: str = ...):
        response = await http_client.get(artwork)
        if not self._is_image_link(response=response):
            raise Exception("Link does not produce an image")
        return response.content

    def is_valid_url(self, url: str = ...) -> bool:
        u = parse.urlparse(url)
        # Check if scheme(http or https) and netloc(domain) are not empty
        return u[0] != "" and u[1] != ""

    def _get_images(self, response: Response = ...) -> list:
        html = response.text
        links = set()
        for element in html.split('"'):
            if "/" in element:
                for img in self.image_extensions:
                    if element.endswith(img):
                        link = element.replace("\\", "")
                        if "http" != link[:4]:
                            link = os.path.join(response.url, link)
                        if self.is_valid_url(url=link):
                            links.add(element.replace("\\", ""))
        return links

    async def resolve_artwork(self, artwork: str = ...):
        response = await http_client.get(
            artwork,
            headers={
                "User-Agent": (
                    "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101"
                    "Firefox/12.0"
                )
            },
        )
        if self._is_image_link(response=response):
            return artwork
        img_links = self._get_images(response=response)
        for img_link in img_links:
            if "artworks" in img_link and "500x500" in img_link:
                return img_link
        raise Exception("Cannot resolve artwork")


image_downloader = ImageDownloader()
