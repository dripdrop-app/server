from contextlib import asynccontextmanager
from fake_useragent import UserAgent
from httpx import AsyncClient

user_agent = UserAgent()


@asynccontextmanager
async def create_http_client():
    client = AsyncClient(
        follow_redirects=True, headers={"User-Agent": user_agent.random}
    )
    try:
        yield client
    except Exception as e:
        raise e
    finally:
        await client.aclose()
