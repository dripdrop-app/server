from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.requests import Request

async def index(request: Request):
    path = request.path_params.get('path')
    if path == '':
        path = 'index.html'
    return FileResponse(f'app/build/{path}')

routes = [
    Mount('/static', app=StaticFiles(directory='app/build/static'), name="static"),
    Route('/{path:path}', endpoint=index, methods=['GET'])
]

app = Starlette(routes=routes)