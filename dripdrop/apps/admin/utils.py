from datetime import timedelta
from sqlalchemy import select, delete, nulls_first

from dripdrop.apps.admin.models import Proxy
from dripdrop.services import http_client
from dripdrop.services.database import AsyncSession
from dripdrop.utils import get_current_time

PROXY_LIST_URL = "https://proxylist.geonode.com/api/proxy-list"


async def _get_proxy(session: AsyncSession):
    query = select(Proxy).order_by(nulls_first(Proxy.last_used.asc()))
    results = await session.scalars(query)
    return results.first()


async def get_proxy(session: AsyncSession):
    proxy = await _get_proxy(session=session)
    if proxy:
        current_time = get_current_time()
        limit = current_time - timedelta(hours=1)
        if proxy.created_at > limit:
            return proxy
    async with http_client.create_client() as client:
        response = await client.get(
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
        if response.status_code == 200:
            json = response.json()
            query = delete(Proxy)
            await session.execute(query)
            await session.commit()
            for proxy in json["data"]:
                query = select(Proxy).where(Proxy.ip_address == proxy["ip"])
                results = await session.scalars(query)
                existing_proxy = results.first()
                if not existing_proxy:
                    session.add(Proxy(ip_address=proxy["ip"], port=int(proxy["port"])))
                    await session.commit()
    return await _get_proxy(session=session)
