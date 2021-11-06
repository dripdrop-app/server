import traceback
from inspect import iscoroutinefunction
from starlette.requests import Request
from starlette.responses import Response
from server.db import database, sessions, users, websocket_tokens
from server.config import API_KEY


def endpoint_handler():
    def decorator(function):
        async def wrapper(request: Request):
            try:
                if iscoroutinefunction(function):
                    return await function(request)
                else:
                    return function(request)
            except:
                print(traceback.format_exc())
                return Response(None, 400)
        return wrapper
    return decorator


def authenticated_endpoint(admin=False):
    def decorator(function):
        async def wrapper(request: Request):
            session_id = request.session.get('id')
            username = request.session.get('username')
            if session_id and username:
                query = sessions.select().where(sessions.c.id == session_id,
                                                sessions.c.username == username)
                session = await database.fetch_one(query)
                if session:
                    return await function(request)
            request.session.clear()
            return Response(None, 401)
        return wrapper
    return decorator


def api_key_protected_endpoint():
    def decorator(function):
        async def wrapper(request: Request):
            api_key = request.query_params.get('api_key')
            if not api_key or api_key != API_KEY:
                return Response(None, 401)
            try:
                if iscoroutinefunction(function):
                    return await function(request)
                else:
                    return function(request)
            except:
                print(traceback.format_exc())
                return Response(None, 400)
        return wrapper
    return decorator
