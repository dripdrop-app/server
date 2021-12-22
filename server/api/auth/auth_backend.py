import base64
import json
from cryptography.fernet import Fernet
from starlette.authentication import AuthCredentials, SimpleUser, UnauthenticatedUser
from starlette.requests import HTTPConnection
from starlette.middleware.authentication import AuthenticationBackend
from server.config import SECRET_KEY, API_KEY
from server.db import users, database, sessions
from server.utils.enums import AuthScopes


class SessionHandler:
    _signer = Fernet(key=base64.b64encode(SECRET_KEY.encode('utf-8')))

    def encrypt(session={}):
        serialized_session = json.dumps(session)
        return SessionHandler._signer.encrypt(serialized_session.encode('utf-8')).decode('utf-8')

    def decrypt(cookie=''):
        try:
            return json.loads(SessionHandler._signer.decrypt(cookie.encode('utf-8')).decode('utf-8'))
        except:
            return dict()


class AuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        cookies = conn.cookies
        session = SessionHandler.decrypt(cookies.get('session'))
        session_id = session.get('id')
        api_key = conn.query_params.get('api_key')

        if session_id:
            query = sessions.select().where(sessions.c.id == session_id)
            session = await database.fetch_one(query)

            if session:
                username = session.get('username')
                query = users.select().where(users.c.username == username)
                account = await database.fetch_one(query)

                if account:
                    scopes = [AuthScopes.AUTHENTICATED]

                    if account.get('admin'):
                        scopes.append(AuthScopes.ADMIN)
                    return AuthCredentials(scopes), SimpleUser(username)

        if api_key == API_KEY:
            return AuthCredentials([AuthScopes.API_KEY]), SimpleUser('api')

        return AuthCredentials([]), UnauthenticatedUser()
