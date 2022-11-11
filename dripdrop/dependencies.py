import jwt
import traceback
from .settings import settings
from .logging import logger
from .models import create_session, AsyncSession, User, Users
from fastapi import HTTPException, status, WebSocket
from fastapi.param_functions import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from typing import Union

ALGORITHM = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_db_session():
    async with create_session() as db:
        yield db


async def get_user_from_token(token: str = ..., db: AsyncSession = ...):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email = payload.get("email", None)
        if email:
            query = select(Users).where(Users.email == email)
            results = await db.scalars(query)
            user = results.first()
            return User.from_orm(user)
    except jwt.PyJWTError:
        logger.exception(traceback.format_exc())
    finally:
        return None


async def get_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(create_db_session),
):
    return await get_user_from_token(token=token, db=db)


async def get_websocket_user(
    websocket: WebSocket = None,
    db: AsyncSession = Depends(create_db_session),
):
    token = websocket.query_params.get("token", None)
    return await get_user_from_token(token=token, db=db)


async def get_authenticated_user(user: Union[None, User] = Depends(get_user)):
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def get_authenticated_websocket_user(
    user: Union[None, User] = Depends(get_websocket_user)
):
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
