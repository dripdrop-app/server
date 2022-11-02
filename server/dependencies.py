import base64
import json
from asgiref.sync import sync_to_async
from cryptography.fernet import Fernet
from fastapi import Request, HTTPException, WebSocket
from fastapi.param_functions import Depends
from server.config import config
from server.models import create_session, DBSession
from server.models.api import GoogleAccount, User, SessionUser
from server.models.orm import GoogleAccounts, Sessions
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class SessionHandler:
    _signer = Fernet(key=base64.b64encode(config.secret_key.encode("utf-8")))
    cookie_name = "session"

    async def encrypt(session: dict = ...):
        json_dumps = sync_to_async(json.dumps)
        serialized_session = await json_dumps(session)
        return SessionHandler._signer.encrypt(
            serialized_session.encode("utf-8")
        ).decode("utf-8")

    async def decrypt(cookies: dict = ...):
        try:
            decrypted_cookie = SessionHandler._signer.decrypt(
                cookies.get(SessionHandler.cookie_name).encode("utf-8")
            )
            json_bytes = decrypted_cookie.decode("utf-8")
            json_loads = sync_to_async(json.loads)
            return await json_loads(json_bytes)
        except Exception:
            return dict()


async def create_db_session():
    async with create_session() as db:
        yield db


async def get_user(
    request: Request = None,
    websocket: WebSocket = None,
    db: DBSession = Depends(create_db_session),
):
    connection = request if request else websocket
    if connection:
        session = await SessionHandler.decrypt(cookies=connection.cookies)
        session_id = session.get("id")
        if session_id:
            query = (
                select(Sessions)
                .where(Sessions.id == session_id)
                .options(selectinload(Sessions.user))
            )
            results = await db.scalars(query)
            session = results.first()
            if session:
                user = session.user
                if user:
                    return User.from_orm(user)
    return None


def get_authenticated_user(user: SessionUser = Depends(get_user)):
    if user:
        return user
    raise HTTPException(401)


def get_admin_user(user: SessionUser = Depends(get_user)):
    if user and user.admin:
        return user
    raise HTTPException(403)


async def get_google_user(
    user: User = Depends(get_authenticated_user),
    db: DBSession = Depends(create_db_session),
):
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == user.email)
    results = await db.scalars(query)
    google_account = results.first()
    if google_account:
        return GoogleAccount.from_orm(google_account)
    raise HTTPException(403)
