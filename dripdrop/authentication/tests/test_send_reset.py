from fastapi import status
from unittest.mock import patch

from dripdrop.authentication.tests.test_base import AuthenticationBaseTest

SEND_RESET_URL = "/api/auth/sendreset"


class SendResetTestCase(AuthenticationBaseTest):
    async def test_send_reset_with_nonexistent_user(self):
        response = await self.client.post(
            SEND_RESET_URL, json={"email": "random@gmail.com"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_send_reset_with_unverifed_user(self):
        user = await self.create_user(
            email="user@gmail.com", password="password", verified=False
        )
        response = await self.client.post(SEND_RESET_URL, json={"email": user.email})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.sendgrid_client.send_password_reset_email")
    async def test_send_reset(self, _):
        user = await self.create_user(email="user@gmail.com", password="password")
        response = await self.client.post(SEND_RESET_URL, json={"email": user.email})
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.content
        )
