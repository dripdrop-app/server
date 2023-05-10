from contextlib import asynccontextmanager
from fake_useragent import UserAgent
from httpx import AsyncClient, AsyncHTTPTransport

user_agent = UserAgent()


@asynccontextmanager
async def create_client():
    transport = AsyncHTTPTransport(retries=3)
    client = AsyncClient(
        follow_redirects=True,
        headers={"User-Agent": user_agent.random},
        transport=transport,
    )
    try:
        yield client
    except Exception as e:
        raise e
    finally:
        await client.aclose()
