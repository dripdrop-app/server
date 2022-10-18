import requests
from bs4 import BeautifulSoup


class ImageDownloaderService:
    def download_image(self, artwork: str = ...):
        data = requests.get(artwork)
        if data.headers["Content-Type"].split("/")[0] == "image":
            return data.content

    def resolve_artwork(self, artwork: str = ...):
        img_links = self._get_images(artwork)
        for img_link in img_links:
            if "artworks" in img_link and "500x500" in img_link:
                return img_link

    def valid_image_url(self, artwork: str = ...):
        data = requests.get(artwork)
        return data.headers["Content-Type"].split("/")[0] == "image"

    def _get_images(self, url: str = ...) -> list:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        image_extensions = (".jpg", ".ico", "png", ".jpeg")
        image_tags = soup.select("img[src]")
        valid_tags = list(
            filter(
                lambda tag: tag.__dict__["attrs"]["src"].endswith(image_extensions),
                image_tags,
            )
        )
        links = list(map(lambda tag: tag.__dict__["attrs"]["src"], valid_tags))
        return links


image_downloader_service = ImageDownloaderService()

if __name__ == "__main__":
    print(
        image_downloader_service.download_image(
            "https://soundcloud.com/nba-youngboy/youngboy-never-broke-again-put"
        )
    )
