from fastapi import status

from dripdrop.authentication.dependencies import COOKIE_NAME
from dripdrop.base.test import BaseTest

LOGIN_URL = "/api/auth/login"
LOGOUT_URL = "/api/auth/logout"
SESSION_URL = "/api/auth/session"


class LogoutTestCase(BaseTest):
    async def test_logout_when_not_logged_in(self):
        response = await self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_logout_when_logged_in(self):
        TEST_PASSWORD = "password"
        user = await self.create_user(email="user@gmail.com", password=TEST_PASSWORD)
        response = await self.client.post(
            LOGIN_URL, json={"email": user.email, "password": TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = await self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.cookies.get(COOKIE_NAME))
        response = await self.client.get(SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
