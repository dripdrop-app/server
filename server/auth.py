import bcrypt
import uuid
import base64
import json
from cryptography.fernet import Fernet
from sqlalchemy.sql.expression import true
from starlette.authentication import AuthCredentials, SimpleUser, UnauthenticatedUser, requires
from starlette.middleware import sessions
from starlette.requests import HTTPConnection, Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.authentication import AuthenticationBackend
from server.utils.wrappers import endpoint_handler
from server.db import users, database, sessions
from server.config import SECRET_KEY, API_KEY, ENVIRONMENT
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


async def create_new_account(username: str, password: str):
    if not username or not password:
        raise ValueError('Username or Password not supplied.')

    if len(password) < 8:
        raise ValueError('Password length is too short')

    query = users.select().where(users.c.username == username)
    account = await database.fetch_one(query)

    if account:
        raise ValueError(f'Account with username `{username}` exists.')

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = users.insert().values(
        username=username,
        password=hashed_pw.decode('utf-8'),
        admin=False,
        approved=False
    )
    await database.execute(query)


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
async def check_session(request: Request):
    username = request.user.display_name
    admin = AuthScopes.ADMIN in request.auth.scopes
    return JSONResponse({
        'username': username,
        'admin': admin,
    }, 200)


@endpoint_handler()
async def login(request: Request):
    form = await request.json()
    username = form.get('username')
    password = form.get('password')

    query = users.select().where(users.c.username == username)
    account = await database.fetch_one(query)

    if not account:
        return JSONResponse({'error': 'Account not found.'}, 400)

    if not bcrypt.checkpw(password.encode('utf-8'), account.get('password').encode('utf-8')):
        return JSONResponse({'error': 'Username or Password is incorrect.'}, 400)

    if not account.get('approved'):
        return JSONResponse({'error': 'User has not been approved.'}, 401)

    session_id = str(uuid.uuid4())
    query = sessions.insert().values(id=session_id, username=username)
    await database.execute(query)

    response = JSONResponse({
        'username': username,
        'admin': account.get('admin'),
    })

    TWO_WEEKS_EXPIRATION = 14*24*60*60

    response.set_cookie(
        'session',
        SessionHandler.encrypt({'id': session_id}),
        max_age=TWO_WEEKS_EXPIRATION,
        expires=TWO_WEEKS_EXPIRATION,
        httponly=true,
        secure=ENVIRONMENT == 'production'
    )

    return response


@requires([AuthScopes.AUTHENTICATED])
@endpoint_handler()
@database.transaction()
async def logout(request: Request):
    response = Response(None, 200)
    response.set_cookie('session', max_age=-1, expires=-1)
    return response


@endpoint_handler()
@database.transaction()
async def create_account(request: Request):
    form = await request.json()
    username = form.get('username')
    password = form.get('password')

    try:
        await create_new_account(username, password)
    except ValueError as e:
        return JSONResponse({'error': e.__str__()}, 400)

    return JSONResponse({'username': username, 'admin': False}, 201)


@requires([AuthScopes.ADMIN])
@endpoint_handler()
@database.transaction()
async def admin_create_account(request: Request):
    form = await request.json()
    username = form.get('username')
    password = form.get('password')

    try:
        await create_new_account(username, password)
    except ValueError as e:
        return JSONResponse({'error': e.message}, 400)

    return Response({'username': username, 'admin': False}, 201)
