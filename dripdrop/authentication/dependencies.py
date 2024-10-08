from fastapi import HTTPException, status, Request, WebSocket, Depends
from sqlalchemy import select
from typing import Union, Annotated

from dripdrop.authentication import utils
from dripdrop.authentication.models import User
from dripdrop.base.dependencies import DatabaseSession, AsyncSession


COOKIE_NAME = "token"


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
