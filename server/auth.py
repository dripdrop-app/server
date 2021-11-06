import bcrypt
import uuid
from starlette.middleware import sessions
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from server.middleware import endpoint_handler, authenticated_endpoint
from server.db import users, database, sessions


async def create_new_account(username: str, password: str):
    if not username or not password:
        raise ValueError('Username or Password not supplied.')

    if len(password) < 8:
        raise ValueError('Password length is too short')

    query = users.select().where(users.c.username == username)
    account = await database.fetch_one(query)

    if account:
        raise ValueError(f'Account with username `{username}` exists.')

    hashed_pw = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())
    query = users.insert().values(
        username=username,
        password=hashed_pw.decode('utf-8'),
        admin=False,
        approved=False
    )
    await database.execute(query)


@endpoint_handler()
@authenticated_endpoint()
async def check_session(request: Request):
    username = request.session.get('username')
    admin = request.session.get('admin')
    return JSONResponse({
        'username': username,
        'admin': admin,
    }, 200)


@endpoint_handler()
@database.transaction()
async def login(request: Request):
    form = await request.json()
    username = form.get('username')
    password = form.get('password')

    query = users.select().where(users.c.username == username)
    account = await database.fetch_one(query)

    if not account:
        return JSONResponse({'error': 'Account not found.'}, 400)

    if not bcrypt.checkpw(bytes(password, 'utf-8'), bytes(account.get('password'), 'utf-8')):
        return JSONResponse({'error': 'Username or Password is incorrect.'}, 400)

    if not account.get('approved'):
        return JSONResponse({'error': 'User has not been approved.'}, 401)

    session_id = str(uuid.uuid4())
    query = sessions.insert().values(id=session_id, username=username)
    await database.execute(query)

    request.session.update({
        'id': session_id,
        'username': username,
        'admin': account.get('admin')
    })

    return JSONResponse({
        'username': username,
        'admin': account.get('admin'),
    })


@endpoint_handler()
@authenticated_endpoint()
@database.transaction()
async def logout(request: Request):
    request.session.clear()
    return Response(None, 200)


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


@endpoint_handler()
@authenticated_endpoint(admin=True)
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
