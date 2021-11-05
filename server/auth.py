import bcrypt
import uuid
from starlette.middleware import sessions
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from server.utils.helpers import endpointHandler, authenticatedEndpoint
from server.db import users, database, sessions


async def createSession(request: Request, username: str):
    sessionID = str(uuid.uuid4())
    query = sessions.insert().values(id=sessionID, username=username)
    await database.execute(query)

    request.session.update({'id': sessionID})


async def createNewAccount(username: str, password: str):
    if not username or not password:
        return ValueError('Username or Password not supplied.')

    if len(password) < 8:
        raise ValueError('Password length is too short')

    query = users.select().where(users.c.username == username)
    account = await database.fetch_one(query)

    if account:
        raise ValueError(f'Account with `{username} exists.`')

    hashedpw = bcrypt.hashpw(bytes(password), bcrypt.gensalt())
    query = users.insert().values(
        username=username,
        password=hashedpw,
        admin=False,
        approved=False
    )
    await database.execute(query)


@endpointHandler()
@database.transaction()
async def login(request: Request):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')

    query = users.select().where(users.c.username == username)
    account = await database.fetch_one(query)

    if not bcrypt.checkpw(bytes(password), account.get('password')):
        return Response(None, 400)

    await createSession(request, username)

    return Response(None)


@endpointHandler()
@database.transaction()
async def createAccount(request: Request):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')

    try:
        await createNewAccount(username, password)
    except ValueError as e:
        return JSONResponse({'error': e.message}, 400)

    await createSession(request, username)

    return Response(None, 201)


@endpointHandler()
@authenticatedEndpoint(admin=True)
@database.transaction()
async def adminCreateAccount(request: Request):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')

    try:
        await createNewAccount(username, password)
    except ValueError as e:
        return JSONResponse({'error': e.message}, 400)

    return Response(None, 201)
