import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from server.api import auth, music, youtube
from server.database import db
from server.dependencies import get_user
from server.queue import q


def boot_tasks():
    # q.enqueue('server.api.youtube.tasks.update_youtube_video_categories')
    return


app = FastAPI(title='DripDrop', on_startup=[db.connect, boot_tasks],
              on_shutdown=[db.disconnect], responses={400: {}}, dependencies=[Depends(get_user)])


app.router.include_router(auth.app.router, prefix='/auth')
app.router.include_router(music.app.router, prefix='/music')
app.router.include_router(youtube.app.router, prefix='/youtube')


@app.get('/{path:path}')
async def index(request: Request):
    path = request.path_params.get('path')

    if path == '':
        path = 'index.html'

    filepath = os.path.join(os.path.dirname(__file__), f'../app/build/{path}')

    if os.path.exists(filepath):
        return FileResponse(filepath)

    return FileResponse(os.path.join(os.path.dirname(__file__), f'../app/build/index.html'))
