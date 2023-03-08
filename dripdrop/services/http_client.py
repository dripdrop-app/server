from httpx import AsyncClient

http_client = AsyncClient(
    headers={
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/51.0.2704.103 Safari/537.36"
        )
    },
    follow_redirects=True,
)
