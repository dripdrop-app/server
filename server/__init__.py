import os
from starlette import middleware
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import FileResponse
from starlette.requests import Request
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware import Middleware
from server.music_downloader import delete_job, get_grouping, download, process_job, get_artwork, listen_jobs, download_job, get_tags
from server.auth import login, create_account, admin_create_account, check_session, logout, AuthBackend
from server.db import database


async def index(request: Request):
    path = request.path_params.get('path')
    if path == '':
        path = 'index.html'
    filepath = os.path.join(os.path.dirname(__file__), f'../app/build/{path}')
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return FileResponse(os.path.join(os.path.dirname(__file__), f'../app/build/index.html'))

routes = [
    Mount('/music', routes=[
        Route('/getArtwork', endpoint=get_artwork, methods=['GET']),
        Route('/processJob', endpoint=process_job, methods=['GET']),
        Route('/grouping', endpoint=get_grouping, methods=['GET']),
        Route('/getTags', endpoint=get_tags, methods=['POST']),
        Route('/download', endpoint=download, methods=['POST']),
        Route('/deleteJob', endpoint=delete_job, methods=['GET']),
        Route('/downloadJob', endpoint=download_job, methods=['GET']),
        WebSocketRoute('/listenJobs', endpoint=listen_jobs),
    ]),
    Mount('/auth', routes=[
        Route('/create', endpoint=create_account, methods=['POST']),
        Route('/admin/create',
          endpoint=admin_create_account, methods=['POST']),
        Route('/checkSession', endpoint=check_session, methods=['GET']),
        Route('/logout', endpoint=logout, methods=['GET']),
        Route('/login', endpoint=login, methods=['POST']),
    ]),
    Route('/{path:path}', endpoint=index, methods=['GET'])
]


middleware = [
    Middleware(AuthenticationMiddleware, backend=AuthBackend())
]

app = Starlette(routes=routes, middleware=middleware, on_startup=[
    database.connect], on_shutdown=[database.disconnect])
