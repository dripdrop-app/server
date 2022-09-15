import requests
import os
from urllib import parse


def download_image(artwork, return_content=True):
    if not is_valid_url(artwork):
        raise ValueError
    data = requests.get(artwork)
    if data.headers["Content-Type"].split("/")[0] == "image":
        if return_content:
            return data.content
        return artwork
    img_links = get_images(artwork)
    for img_link in img_links:
        if "artworks" in img_link and "500x500" in img_link:
            if return_content:
                return requests.get(img_link).content
            return img_link
    return None


def is_valid_url(url: str) -> bool:
    u = parse.urlparse(url)
    # Check if scheme(http or https) and netloc(domain) are not empty
    return u[0] != "" and u[1] != ""


def get_images(url: str) -> list:
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
    image_extensions = [".jpg", ".ico", "png", ".jpeg"]
    links = set()
    for element in html.split('"'):
        if "/" in element:
            for img in image_extensions:
                if element.endswith(img):
                    link = element.replace("\\", "")
                    if "http" != link[:4]:
                        link = os.path.join(url, link)
                    if is_valid_url(link):
                        links.add(element.replace("\\", ""))
    return links


if __name__ == "__main__":
    print(download_image("https://soundcloud.com/9v9v/get-low"))
