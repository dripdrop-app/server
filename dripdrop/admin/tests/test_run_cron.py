from fastapi import status
from unittest.mock import AsyncMock

from dripdrop.base.test import BaseTest

CRON_URL = "api/admin/cron/run"


class GetCronRunTestCase(BaseTest):
    async def test_run_cron_when_not_logged_in(self):
        response = await self.client.get(CRON_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_run_cron_as_regular_user(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(CRON_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    async def test_run_cron_as_admin_user(self, mock_run_cron_jobs: AsyncMock):
        await self.create_and_login_user(
            email="user@gmail.com", password="password", admin=True
        )
        response = await self.client.get(CRON_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_run_cron_jobs.assert_awaited_once()
