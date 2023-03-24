from datetime import timedelta
from sqlalchemy import select, delete, nulls_first

from dripdrop.services.database import AsyncSession
from dripdrop.services.http_client import create_http_client
from dripdrop.utils import get_current_time

from .models import Proxy

PROXY_LIST_URL = "https://proxylist.geonode.com/api/proxy-list"


async def get_proxy(session: AsyncSession = ...):
    async def _get_proxy():
        query = select(Proxy).order_by(nulls_first(Proxy.last_used.asc()))
        results = await session.scalars(query)
        return results.first()

    proxy = await _get_proxy()
    if proxy:
        current_time = get_current_time()
        limit = current_time - timedelta(hours=1)
        if proxy.created_at > limit:
            return proxy

    async with create_http_client() as http_client:
        response = await http_client.get(
            PROXY_LIST_URL,
            params={
                "limit": 30,
                "page": 1,
                "sort_by": "lastChecked",
                "sort_type": "desc",
                "country": "US",
                "google": True,
                "speed": "fast",
            },
        )
    response.raise_for_status()
    json = response.json()
    query = delete(Proxy)
    await session.execute(query)
    await session.commit()
    new_proxies = [
        Proxy(ip_address=proxy["ip"], port=int(proxy["port"])) for proxy in json["data"]
    ]
    session.add_all(new_proxies)
    await session.commit()
    return await _get_proxy()
