import asyncio
import base64
import json
from cryptography.fernet import Fernet
from fastapi import Request, HTTPException, WebSocket
from fastapi.param_functions import Depends
from server.config import config
from server.database import Session, User, users, db, sessions
from server.models import SessionUser


class SessionHandler:
    _signer = Fernet(key=base64.b64encode(config.secret_key.encode('utf-8')))
    cookie_name = 'session'

    async def encrypt(session: dict):
        loop = asyncio.get_event_loop()
        serialized_session = await loop.run_in_executor(None, json.dumps, session)
        return SessionHandler._signer.encrypt(serialized_session.encode('utf-8')).decode('utf-8')

    async def decrypt(cookies: dict):
        try:
            loop = asyncio.get_event_loop()
            decrypted_cookie = await loop.run_in_executor(None, SessionHandler._signer.decrypt, cookies.get(SessionHandler.cookie_name).encode('utf-8'))
            json_bytes = decrypted_cookie.decode('utf-8')
            return await loop.run_in_executor(None, json.loads, json_bytes)
        except:
            return dict()


class GetUser:
    def __init__(self, is_admin: bool = False, is_authenticated: bool = False):
        self.is_admin = is_admin
        self.is_authenticated = is_authenticated

    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        connection = request if request else websocket
        session = await SessionHandler.decrypt(connection.cookies)
        session_id = session.get('id')
        if session_id:
            query = sessions.select().where(sessions.c.id == session_id)
            session = await db.fetch_one(query)
            if session:
                session = Session.parse_obj(session)
                email = session.user_email
                query = users.select().where(users.c.email == email)
                account = await db.fetch_one(query)
                if account:
                    account = User.parse_obj(account)
                    return SessionUser(email=email, admin=account.admin, authenticated=True)
        return SessionUser(email='', admin=False, authenticated=False)


get_user = GetUser()


def get_authenticated_user(user: SessionUser = Depends(get_user)):
    if user.authenticated:
        return user
    raise HTTPException(401)


def get_admin_user(user: SessionUser = Depends(get_user)):
    if user.admin:
        return user
    raise HTTPException(401)
