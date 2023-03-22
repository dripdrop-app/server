import asyncio
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from dripdrop.services.http_client import http_client
from dripdrop.settings import settings


@dataclass
class ScrapedSubscriptions:
    handles: list[str]
    ids: list[str]


@dataclass
class YoutubeChannelInfo:
    id: str
    title: str
    thumbnail: str


async def get_channel_subscriptions(channel_id: str = ...):
    def _get_channel_subscriptions(channel_id: str = ...):
        driver = webdriver.Remote(
            command_executor=settings.selenium_webdriver_url,
            options=webdriver.ChromeOptions(),
        )
        scraped_subscriptions = ScrapedSubscriptions(handles=[], ids=[])
        try:
            driver.get(f"https://youtube.com/channel/{channel_id}/channels")
            subscription_header = next(
                (
                    header
                    for header in driver.find_elements(
                        by=By.ID, value="header-container"
                    )
                    if header.text == "Subscriptions"
                ),
                None,
            )
            assert subscription_header is not None
            contents_element: WebElement | None = driver.execute_script(
                "return arguments[0].nextElementSibling;", subscription_header
            )
            assert contents_element.get_dom_attribute("id") == "contents"
            channels = []
            while True:
                selected_channels = contents_element.find_elements(
                    by=By.ID, value="channel-info"
                )
                if len(selected_channels) == len(channels):
                    break
                channels = selected_channels
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", channels[-1]
                )
                time.sleep(5)

            for channel in channels:
                channel_link = channel.get_attribute("href")
                if channel_link:
                    channel_id = channel_link.split("/")[-1]
                    if channel_id.startswith("@"):
                        scraped_subscriptions.handles.append(channel_id)
                    else:
                        scraped_subscriptions.ids.append(channel_id)
        finally:
            driver.quit()
        return scraped_subscriptions

    return await asyncio.to_thread(_get_channel_subscriptions, channel_id=channel_id)


async def get_channel_info(channel_id: str = ...):
    url = "https://youtube.com/"
    if channel_id.startswith("@"):
        url += channel_id
    else:
        url += f"channel/{channel_id}"
    response = await http_client.get(url=url)
    if response.is_error:
        return None
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    channel_id_tag = soup.find("meta", itemprop="channelId")
    name_tag = soup.find("meta", itemprop="name")
    thumbnail_tag = soup.find("link", itemprop="thumbnailUrl")
    if not (channel_id_tag or name_tag or thumbnail_tag):
        return None
    return YoutubeChannelInfo(
        id=channel_id_tag["content"],
        title=name_tag["content"],
        thumbnail=thumbnail_tag["href"],
    )


if __name__ == "__main__":
    print(get_channel_subscriptions(channel_id="UCDNmtdocWQHo_mwse8kaOCQ"))
