import os
from starlette import middleware
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import FileResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from starlette.config import Config
from server.music_downloader import deleteJob, getGrouping, download, processJob, getArtwork, listenJobs, downloadJob, getTags
from server.auth import login, createAccount, adminCreateAccount
from server.db import database

config = Config('.env')
environment = config.get('ENV', default='None')


async def index(request: Request):
    path = request.path_params.get('path')
    if path == '':
        path = 'index.html'
    filepath = os.path.join(os.path.dirname(__file__), f'../app/build/{path}')
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return FileResponse(os.path.join(os.path.dirname(__file__), f'../app/build/index.html'))

routes = [
    Mount('/auth', routes=[
        Route('/login', endpoint=login, methods=['POST']),
        Route('/create', endpoint=createAccount, methods=['POST']),
        Route('/admin/create', endpoint=adminCreateAccount, methods=['POST'])
    ]),
    Mount('/music', routes=[
        Route('/getArtwork', endpoint=getArtwork, methods=['GET']),
        Route('/processJob', endpoint=processJob, methods=['GET']),
        Route('/grouping', endpoint=getGrouping, methods=['GET']),
        Route('/getTags', endpoint=getTags, methods=['POST']),
        Route('/download', endpoint=download, methods=['POST']),
        Route('/deleteJob', endpoint=deleteJob, methods=['GET']),
        Route('/downloadJob', endpoint=downloadJob, methods=['GET']),
        WebSocketRoute('/listenJobs', endpoint=listenJobs),
    ]),
    Route('/{path:path}', endpoint=index, methods=['GET'])
]

middleware = [
    Middleware(SessionMiddleware, secret_key='driprandomdrop123',
               same_site='strict', https_only=environment == 'production')
]

app = Starlette(routes=routes, middleware=middleware, on_startup=[
                database.connect], on_shutdown=[database.disconnect])
