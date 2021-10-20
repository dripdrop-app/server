import os
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import FileResponse, Response
from starlette.requests import Request
from server.music_downloader import getGrouping, download, completeJob, getArtwork
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
    Route('/completeJob', endpoint=completeJob, methods=['GET']),
    Route('/grouping', endpoint=getGrouping, methods=['GET']),
    Route('/download', endpoint=download, methods=['POST']),
    Route('/{path:path}', endpoint=index, methods=['GET'])
]

app = Starlette(routes=routes, on_startup=[
                database.connect], on_shutdown=[database.disconnect])
