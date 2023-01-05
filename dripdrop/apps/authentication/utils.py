import jwt
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from dripdrop.dependencies import ALGORITHM
from dripdrop.models.database import AsyncSession
from dripdrop.settings import settings

from .models import User


async def find_user_by_email(email: str = ..., session: AsyncSession = ...):
    query = select(User).where(User.email == email)
    results = await session.scalars(query)
    user: User | None = results.first()
    return user


def create_jwt(email: str = ...):
    return jwt.encode(
        payload={
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
