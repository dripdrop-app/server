import jwt
import traceback
from fastapi import HTTPException, status, Request, WebSocket, Depends
from sqlalchemy import select
from typing import Union

import dripdrop.utils as dripdrop_utils
from dripdrop.apps.authentication.models import User
from dripdrop.services import database
from dripdrop.services.database import AsyncSession

from .logger import logger
from .settings import settings

ALGORITHM = "HS256"
COOKIE_NAME = "token"


async def create_database_session():
    async with database.create_session() as session:
        yield session


async def get_user_from_token(token: str, session: AsyncSession):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        expires = payload.get("exp", None)
        if expires is None:
            return None
        if expires < dripdrop_utils.get_current_time().timestamp():
            pass
        email = payload.get("email", None)
        if email:
            query = select(User).where(User.email == email)
            results = await session.scalars(query)
            user: Union[User, None] = results.first()
            return user
    except jwt.PyJWTError:
        logger.exception(traceback.format_exc())
        return None


async def get_user(
    request: Request = None,
    websocket: WebSocket = None,
    session: AsyncSession = Depends(create_database_session),
):
    connection = request if request else websocket
    if connection:
        cookies = connection.cookies
        headers = connection.headers
        token = cookies.get(COOKIE_NAME, headers.get("Authorization", None))
        if token:
            return await get_user_from_token(token=token, session=session)
    return None


async def get_authenticated_user(user: Union[None, User] = Depends(get_user)):
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
