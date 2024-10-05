from sqlalchemy import select

from dripdrop.authentication.models import User
from dripdrop.base.test import BaseTest


class AuthenticationBaseTest(BaseTest):
    async def get_user(self, email: str):
        query = select(User).where(User.email == email)
        user = await self.session.scalar(query)
        self.assertIsNotNone(user)
        return user
