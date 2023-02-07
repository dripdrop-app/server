import jwt
from datetime import datetime, timedelta
from sqlalchemy import select

from dripdrop.database import AsyncSession
from dripdrop.dependencies import ALGORITHM
from dripdrop.settings import settings

from .models import User


async def find_user_by_email(email: str = ..., session: AsyncSession = ...):
    query = select(User).where(User.email == email)
    results = await session.scalars(query)
    user = results.first()
    return user


def create_jwt(email: str = ...):
    return jwt.encode(
        payload={
            "email": email,
            "exp": datetime.now(tz=settings.timezone) + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
