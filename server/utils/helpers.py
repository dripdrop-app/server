import traceback
import datetime
from inspect import iscoroutinefunction
from starlette.requests import Request
from starlette.responses import Response
from server.db import database, sessions, users


def endpointHandler():
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


def authenticatedEndpoint(admin=False):
    def decorator(function):
        async def wrapper(request: Request):
            sessionID = request.session.get('id')
            if sessionID:
                query = sessions.select().where(sessions.c.id == sessionID)
                session = await database.fetch_one(query)
                query = users.select().where(users.c.username == session.get('username'))
                account = await database.execute(query)
                if session and account:
                    if not admin or account.get('admin'):
                        request.session.update(
                            {'user': session.get('username')})
                        return await function(request)
            return Response(None, 401)
        return wrapper
    return decorator


def convertDBJob(job):
    return {
        key: value.__str__() if isinstance(value, datetime.datetime) else value
        for key, value in job.items()
    }
