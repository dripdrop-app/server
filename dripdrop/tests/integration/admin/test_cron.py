from fastapi import status
from httpx import AsyncClient

CRON_URL = "api/admin/cron/run"


async def test_run_cron_when_not_logged_in(client: AsyncClient):
    response = await client.get(CRON_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_run_cron_as_regular_user(client: AsyncClient, create_and_login_user):
    await create_and_login_user(email="user@gmail.com", password="password")
    response = await client.get(CRON_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_run_cron_as_admin_user(
    client: AsyncClient, create_and_login_user, mock_enqueue
):
    await mock_enqueue()
    await create_and_login_user(email="user@gmail.com", password="password", admin=True)
    response = await client.get(CRON_URL)
    assert response.status_code == status.HTTP_200_OK
