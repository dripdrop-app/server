import os
from fake_useragent import UserAgent
from httpx import Response
from urllib import parse

from dripdrop.services.http_client import create_http_client


IMAGE_EXTENSIONS = [".jpg", ".ico", "png", ".jpeg"]

user_agent = UserAgent()


def is_image_link(response: Response = ...):
    content_type = response.headers.get("Content-Type", None)
    if content_type and content_type.split("/")[0] == "image":
        return True
    return None


async def download_image(artwork: str = ...):
    async with create_http_client() as http_client:
        response = await http_client.get(artwork)
    if not is_image_link(response=response):
        raise Exception("Link does not produce an image")
    return response.content


def is_valid_url(url: str = ...) -> bool:
    u = parse.urlparse(url)
    # Check if scheme(http or https) and netloc(domain) are not empty
    return u[0] != "" and u[1] != ""


def _get_images(response: Response = ...) -> list:
    html = response.text
    links = set()
    for element in html.split('"'):
        if "/" in element:
            for img in IMAGE_EXTENSIONS:
                if element.endswith(img):
                    link = element.replace("\\", "")
                    if "http" != link[:4]:
                        link = os.path.join(response.url, link)
                    if is_valid_url(url=link):
                        links.add(element.replace("\\", ""))
    return links


async def resolve_artwork(artwork: str = ...):
    async with create_http_client() as http_client:
        response = await http_client.get(
            artwork,
            headers={
                "User-Agent": (
                    "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101"
                    "Firefox/12.0"
                )
            },
        )
    if response.is_success:
        if is_image_link(response=response):
            return artwork
        img_links = _get_images(response=response)
        for img_link in img_links:
            if "artworks" in img_link and "500x500" in img_link:
                return img_link
    raise Exception("Cannot resolve artwork")
