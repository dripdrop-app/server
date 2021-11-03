import os
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import FileResponse
from starlette.requests import Request
from server.music_downloader import deleteJob, getGrouping, download, processJob, getArtwork, listenJobs, downloadJob, getTags
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
    Route('/getArtwork', endpoint=getArtwork, methods=['GET']),
    Route('/processJob', endpoint=processJob, methods=['GET']),
    Route('/grouping', endpoint=getGrouping, methods=['GET']),
    Route('/getTags', endpoint=getTags, methods=['POST']),
    Route('/download', endpoint=download, methods=['POST']),
    Route('/deleteJob', endpoint=deleteJob, methods=['GET']),
    Route('/downloadJob', endpoint=downloadJob, methods=['GET']),
    Mount('/ws', routes=[
        WebSocketRoute('/listenJobs', endpoint=listenJobs),
    ]),
    Route('/{path:path}', endpoint=index, methods=['GET'])
]

app = Starlette(routes=routes, on_startup=[
                database.connect], on_shutdown=[database.disconnect])
