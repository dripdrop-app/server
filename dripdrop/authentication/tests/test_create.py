from fastapi import status
from unittest.mock import patch

from dripdrop.authentication.tests.test_base import AuthenticationBaseTest

CREATE_URL = "/api/auth/create"


class CreateTestCase(AuthenticationBaseTest):
    async def test_create_duplicate_user(self):
        user = await self.create_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            CREATE_URL, json={"email": user.email, "password": "otherpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.sendgrid_client.send_verification_email")
    async def test_create_user(self, _):
        TEST_EMAIL = "user@gmail.com"
        response = await self.client.post(
            CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user = await self.get_user(email=TEST_EMAIL)
        self.assertFalse(user.verified)
