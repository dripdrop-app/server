import asyncio
import os
from starlette import middleware
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import FileResponse
from starlette.requests import Request
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware import Middleware
from server.api import music, auth
from server.api.auth.auth_backend import AuthBackend
from server.db import database
from server.utils.enums import RequestMethods
from server.worker import Worker
from server.request_client import client


async def index(request: Request):
    path = request.path_params.get('path')

    if path == '':
        path = 'index.html'

    filepath = os.path.join(os.path.dirname(__file__), f'../app/build/{path}')

    if os.path.exists(filepath):
        return FileResponse(filepath)

    return FileResponse(os.path.join(os.path.dirname(__file__), f'../app/build/index.html'))

routes = [
    *music.routes,
    *auth.routes,
    Route('/{path:path}', endpoint=index, methods=[RequestMethods.GET.value])
]

middleware = [
    Middleware(AuthenticationMiddleware, backend=AuthBackend())
]

worker_task = asyncio.create_task(Worker.work())

app = Starlette(routes=routes, middleware=middleware, on_startup=[
    database.connect], on_shutdown=[database.disconnect, worker_task.cancel, client.close])
