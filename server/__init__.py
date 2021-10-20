import os
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import FileResponse
from starlette.requests import Request
from server.music_downloader import getGrouping, download, completeJob
from server.db import database


async def index(request: Request):
    path = request.path_params.get('path')
    if path == '':
        path = 'index.html'
    return FileResponse(os.path.join(os.path.dirname(__file__), f'../app/build/{path}'))

routes = [
    Route('/completeJob', endpoint=completeJob, methods=['POST']),
    Route('/grouping', endpoint=getGrouping, methods=['POST']),
    Route('/download', endpoint=download, methods=['POST']),
    Route('/{path:path}', endpoint=index, methods=['GET'])
]

app = Starlette(routes=routes, on_startup=[
                database.connect], on_shutdown=[database.disconnect])
