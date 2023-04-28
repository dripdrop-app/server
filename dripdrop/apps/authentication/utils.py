import jwt
from datetime import timedelta
from sqlalchemy import select

import dripdrop.utils as dripdrop_utils
from dripdrop.services.database import AsyncSession
from dripdrop.settings import settings

from .dependencies import ALGORITHM
from .models import User


async def find_user_by_email(email: str, session: AsyncSession):
    query = select(User).where(User.email == email)
    results = await session.scalars(query)
    user = results.first()
    return user


def create_jwt(email: str):
    return jwt.encode(
        payload={
            "email": email,
            "exp": dripdrop_utils.get_current_time() + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
