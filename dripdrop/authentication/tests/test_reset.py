from fastapi import status
from unittest.mock import patch, AsyncMock

from dripdrop.authentication.tests.test_base import AuthenticationBaseTest

RESET_URL = "/api/auth/reset"
SEND_RESET_URL = "/api/auth/sendreset"


class ResetTestCase(AuthenticationBaseTest):
    @patch("dripdrop.services.sendgrid_client.send_password_reset_email")
    async def test_reset_with_invalid_code(self, mock_send_reset: AsyncMock):
        user = await self.create_user(email="user@gmail.com", password="password")
        response = await self.client.post(SEND_RESET_URL, json={"email": user.email})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        args, kwargs = mock_send_reset.call_args
        response = await self.client.post(
            RESET_URL,
            json={
                "token": "tests",
                "password": "newpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user = await self.get_user(email=user.email)

    @patch("dripdrop.services.sendgrid_client.send_password_reset_email")
    async def test_reset(self, mock_send_reset: AsyncMock):
        user = await self.create_user(email="user@gmail.com", password="password")
        response = await self.client.post(SEND_RESET_URL, json={"email": user.email})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        args, kwargs = mock_send_reset.call_args
        response = await self.client.post(
            RESET_URL,
            json={
                "token": kwargs["token"],
                "password": "newpassword",
            },
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.content
        )
        user = await self.get_user(email=user.email)
