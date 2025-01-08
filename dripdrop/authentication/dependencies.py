from typing import Annotated, Optional, Union

from fastapi import Cookie, Depends, Header, HTTPException, WebSocket, status
from pydantic import BaseModel
from sqlalchemy import select

from dripdrop.authentication import utils
from dripdrop.authentication.models import User
from dripdrop.base.dependencies import AsyncSession, DatabaseSession

COOKIE_NAME = "token"


class Cookies(BaseModel):
    token: Optional[str] = None


class Headers(BaseModel):
    authorization: Optional[str] = None


async def get_user_from_token(token: str, session: AsyncSession):
    payload = utils.decode_jwt(token=token)
    email = payload.get("email", None)
    if not email:
        return None
    query = select(User).where(User.email == email)
    user = await session.scalar(query)
    return user


async def get_user(
    session: DatabaseSession,
    cookies: Annotated[Cookies, Cookie()],
    headers: Annotated[Headers, Header()],
):
    token = cookies.token if cookies.token else headers.authorization
    if token:
        return await get_user_from_token(token=token, session=session)
    return None


SessionUser = Annotated[Union[None, User], Depends(get_user)]


async def get_authenticated_user(user: SessionUser, websocket: WebSocket = None):
    if user and user.verified:
        return user
    if websocket:
        await websocket.close()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


AuthenticatedUser = Annotated[User, Depends(get_authenticated_user)]


async def get_admin_user(
    user: User = Depends(get_authenticated_user), websocket: WebSocket = None
):
    if user.admin:
        return user
    if websocket:
        await websocket.close()
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


AdminUser = Annotated[User, Depends(get_admin_user)]
