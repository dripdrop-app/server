from sqlalchemy import select, func

from dripdrop.services.database import AsyncSession
from dripdrop.services.http_client import create_http_client
from dripdrop.tasks import worker_task

from .models import Proxy

PROXY_LIST_URL = "https://proxylist.geonode.com/api/proxy-list"


@worker_task
async def update_proxies(cron: bool = ..., session: AsyncSession = ...):
    if not cron:
        query = select(func.count(Proxy.ip_address))
        count = await session.scalar(query)
        if count > 0:
            return
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
    for proxy in json["data"]:
        session.add(Proxy(ip_address=proxy["ip"], port=int(proxy["port"])))
        await session.commit()
