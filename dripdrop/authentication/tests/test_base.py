from sqlalchemy import select

from dripdrop.authentication.models import User
from dripdrop.base.test import BaseTest


class AuthenticationBaseTest(BaseTest):
    async def get_user(self, email: str):
        query = select(User).where(User.email == email)
        results = await self.session.scalars(query)
        user = results.first()
        self.assertIsNotNone(user)
        return user
