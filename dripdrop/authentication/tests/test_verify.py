import urllib.parse
import uuid
from unittest.mock import AsyncMock, patch

from fastapi import status

from dripdrop.authentication.tests.test_base import AuthenticationBaseTest

CREATE_URL = "/api/auth/create"
VERIFY_URL = "/api/auth/verify"


class VerifyTestCase(AuthenticationBaseTest):
    @patch("dripdrop.services.sendgrid_client.send_verification_email")
    async def test_verify_account_with_invalid_code(self, _):
        TEST_EMAIL = "user@gmail.com"
        response = await self.client.post(
            CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = await self.client.get(VERIFY_URL, params={"token": uuid.uuid4()})
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, response.content
        )

    @patch("dripdrop.services.sendgrid_client.send_verification_email")
    async def test_verify_account(self, mock_send_verification_email: AsyncMock):
        TEST_EMAIL = "user@gmail.com"
        response = await self.client.post(
            CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        args, kwargs = mock_send_verification_email.call_args
        parsed = urllib.parse.urlparse(kwargs["link"])
        query = urllib.parse.parse_qs(parsed.query)
        response = await self.client.get(VERIFY_URL, params=query)
        self.assertEqual(
            response.status_code, status.HTTP_307_TEMPORARY_REDIRECT, response.content
        )
        user = await self.get_user(email=TEST_EMAIL)
        self.assertTrue(user.verified)
