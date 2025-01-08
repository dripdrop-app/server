from unittest.mock import patch

from fastapi import status

from dripdrop.base.test import BaseTest

CREATE_URL = "/api/auth/create"
LOGIN_URL = "/api/auth/login"
SESSION_URL = "/api/auth/session"


class GetSessionTestCase(BaseTest):
    async def test_session_when_not_logged_in(self):
        response = await self.client.get(SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("dripdrop.services.sendgrid_client.send_verification_email")
    async def test_session_after_creating_account(self, _):
        TEST_EMAIL = "user@gmail.com"
        response = await self.client.post(
            CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = await self.client.get(SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_session_after_login(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.get(SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json, {"email": user.email, "admin": False})
