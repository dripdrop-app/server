import dateutil.parser
import jwt
import traceback
from .settings import settings
from .logging import logger
from .models import create_session, AsyncSession, User, Users
from datetime import datetime
from fastapi import HTTPException, status, Request, WebSocket, Depends
from passlib.context import CryptContext
from sqlalchemy import select
from typing import Union

ALGORITHM = "HS256"
TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60
COOKIE_NAME = "token"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_db_session():
    async with create_session() as db:
        yield db


async def get_user_from_token(token: str = ..., db: AsyncSession = ...):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        expires = payload.get("exp", None)
        if not expires:
            return None
        if dateutil.parser.parse(expires) < datetime.utcnow():
            pass
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
    request: Request = None,
    websocket: WebSocket = None,
    db: AsyncSession = Depends(create_db_session),
):
    connection = request if request else websocket
    if connection:
        cookies = connection.cookies
        headers = connection.headers
        token = cookies.get(COOKIE_NAME, headers.get("Authorization", None))
        if token:
            return await get_user_from_token(token=token, db=db)
    return None


async def get_authenticated_user(user: Union[None, User] = Depends(get_user)):
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
