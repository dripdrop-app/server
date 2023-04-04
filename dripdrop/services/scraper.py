import asyncio
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.webelement import WebElement

import dripdrop.utils as dripdrop_utils
from dripdrop.services.http_client import create_http_client
from dripdrop.settings import settings

user_agent = UserAgent()


@dataclass
class YoutubeChannelInfo:
    id: str
    title: str
    thumbnail: str


async def get_channel_subscriptions(channel_id: str = ..., proxy: str | None = ...):
    def _get_channel_subscriptions(channel_id: str = ..., proxy: str | None = ...):
        webdriver_proxy = None
        if proxy:
            webdriver_proxy = Proxy()
            webdriver_proxy.proxy_type = ProxyType.MANUAL
            webdriver_proxy.http_proxy = proxy
            webdriver_proxy.socks_proxy = proxy
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={user_agent.random}")
        driver = webdriver.Remote(
            command_executor=settings.selenium_webdriver_url,
            proxy=webdriver_proxy,
            options=options,
        )
        try:
            driver.get(f"https://youtube.com/channel/{channel_id}/channels")
            time.sleep(5)
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
            channel_links = [
                channel.get_attribute("href").split("/")[-1]
                for channel in channels
                if channel.get_attribute("href")
            ]
            return channel_links
        except Exception as e:
            raise e
        finally:
            driver.quit()

    subscribed_channel_ids = await asyncio.to_thread(
        _get_channel_subscriptions, channel_id=channel_id, proxy=proxy
    )
    subscribed_channels = await dripdrop_utils.gather_with_limit(
        *[
            get_channel_info(channel_id=subscribed_channel_id)
            for subscribed_channel_id in subscribed_channel_ids
        ],
        limit=5,
    )
    return [
        subscribed_channel
        for subscribed_channel in subscribed_channels
        if subscribed_channel
    ]


async def get_channel_info(channel_id: str = ...):
    url = "https://youtube.com/"
    if channel_id.startswith("@"):
        url += channel_id
    else:
        url += f"channel/{channel_id}"
    async with create_http_client() as http_client:
        response = await http_client.get(url=url)
    if response.is_error:
        return None
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
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


if __name__ == "__main__":
    print(get_channel_subscriptions(channel_id="UCDNmtdocWQHo_mwse8kaOCQ"))
