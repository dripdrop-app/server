from fastapi import status

from dripdrop.authentication.dependencies import COOKIE_NAME
from dripdrop.base.test import BaseTest

CREATE_URL = "/api/auth/create"


class CreateTestCase(BaseTest):
    async def test_create_duplicate_user(self):
        user = await self.create_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            CREATE_URL, json={"email": user.email, "password": "otherpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_create_user(self):
        TEST_EMAIL = "user@gmail.com"
        response = await self.client.post(
            CREATE_URL, json={"email": TEST_EMAIL, "password": "password"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get(COOKIE_NAME))
        json = response.json()
        self.assertIsNotNone(json.get("accessToken"))
        self.assertIsNotNone(json.get("tokenType"))
        self.assertEqual(json.get("user"), {"email": TEST_EMAIL, "admin": False})
