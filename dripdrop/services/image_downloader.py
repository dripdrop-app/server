import os
import requests
from urllib import parse


class ImageDownloaderService:
    def __init__(self):
        self.image_extensions = [".jpg", ".ico", "png", ".jpeg"]

    def download_image(self, artwork: str = ...):
        data = requests.get(artwork)
        content_type = data.headers.get("Content-Type", None)
        if content_type:
            if content_type.split("/")[0] == "image":
                return data.content

    def resolve_artwork(self, artwork: str = ...):
        if artwork.endswith(tuple(self.image_extensions)):
            return artwork
        img_links = self._get_images(artwork)
        for img_link in img_links:
            if "artworks" in img_link and "500x500" in img_link:
                return img_link

    def is_valid_url(self, url: str = ...) -> bool:
        u = parse.urlparse(url)
        # Check if scheme(http or https) and netloc(domain) are not empty
        return u[0] != "" and u[1] != ""

    def _get_images(self, url: str = ...) -> list:
        response = requests.get(
            url,
            headers={
                "User-Agent": (
                    "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101"
                    "Firefox/12.0"
                )
            },
        )
        html = response.text
        links = set()
        for element in html.split('"'):
            if "/" in element:
                for img in self.image_extensions:
                    if element.endswith(img):
                        link = element.replace("\\", "")
                        if "http" != link[:4]:
                            link = os.path.join(url, link)
                        if self.is_valid_url(url=link):
                            links.add(element.replace("\\", ""))
        return links


image_downloader_service = ImageDownloaderService()
