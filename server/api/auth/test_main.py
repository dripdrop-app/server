from fastapi.testclient import TestClient
import pytest
from server.app import app
from server.dependencies import SessionHandler

client = TestClient(app)


@pytest.mark.asyncio
async def test_read_unauthenticated_session():
    TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60
    client.cookies.set_cookie(
        SessionHandler.cookie_name,
        await SessionHandler.encrypt({"id": "testsession"}),
        max_age=TWO_WEEKS_EXPIRATION,
        expires=TWO_WEEKS_EXPIRATION,
        httponly=True,
        secure=False,
    )
    response = client.get("/api/auth/session")
    assert response.status_code == 401
