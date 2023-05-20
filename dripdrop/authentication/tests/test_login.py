from fastapi import status

from dripdrop.authentication.dependencies import COOKIE_NAME
from dripdrop.authentication.tests.test_base import AuthenticationBaseTest

LOGIN_URL = "/api/auth/login"


class LoginTestCase(AuthenticationBaseTest):
    async def test_login_with_incorrect_password(self):
        user = await self.create_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            LOGIN_URL, json={"email": user.email, "password": "incorrectpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_login_with_nonexistent_email(self):
        response = await self.client.post(
            LOGIN_URL, json={"email": "user@gmail.com", "password": "password"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_login_unverified_user(self):
        TEST_PASSWORD = "password"
        user = await self.create_user(
            email="user@gmail.com", password=TEST_PASSWORD, verified=False
        )
        response = await self.client.post(
            LOGIN_URL, json={"email": user.email, "password": TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_login_user(self):
        TEST_PASSWORD = "password"
        user = await self.create_user(
            email="user@gmail.com", password=TEST_PASSWORD, verified=True
        )
        response = await self.client.post(
            LOGIN_URL, json={"email": user.email, "password": TEST_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get(COOKIE_NAME))
        json = response.json()
        self.assertIsNotNone(json.get("accessToken"))
        self.assertIsNotNone(json.get("tokenType"))
        self.assertEqual(json.get("user"), {"email": user.email, "admin": False})
