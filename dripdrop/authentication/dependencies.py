import jwt
import traceback
from fastapi import HTTPException, status, Request, WebSocket, Depends
from sqlalchemy import select
from typing import Union, Annotated

import dripdrop.utils as dripdrop_utils
from dripdrop.authentication.models import User
from dripdrop.base.dependencies import DatabaseSession, AsyncSession
from dripdrop.logger import logger
from dripdrop.settings import settings


ALGORITHM = "HS256"
COOKIE_NAME = "token"


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
    session: DatabaseSession,
    request: Request = None,
    websocket: WebSocket = None,
):
    connection = request if request else websocket
    if connection:
        cookies = connection.cookies
        headers = connection.headers
        token = cookies.get(COOKIE_NAME, headers.get("Authorization", None))
        if token:
            return await get_user_from_token(token=token, session=session)
    return None


SessionUser = Annotated[Union[None, User], Depends(get_user)]


async def get_authenticated_user(user: Union[None, User] = Depends(get_user)):
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


AuthenticatedUser = Annotated[User, Depends(get_authenticated_user)]


async def get_admin_user(user: User = Depends(get_authenticated_user)):
    if user.admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


AdminUser = Annotated[User, Depends(get_admin_user)]
