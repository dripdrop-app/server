import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from server.api.auth.main import app as auth_app
from server.api.music.main import app as music_app
from server.api.youtube.main import app as youtube_app
from server.cron import cron_start, cron_end
from server.dependencies import get_user
from server.models.main import db


app = FastAPI(
    title="DripDrop",
    on_startup=[db.connect, cron_start],
    on_shutdown=[cron_end, db.disconnect],
    responses={400: {}},
    dependencies=[Depends(get_user)],
)

app.router.include_router(auth_app.router, prefix="/auth")
app.router.include_router(music_app.router, prefix="/music")
app.router.include_router(youtube_app.router, prefix="/youtube")


app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(os.path.dirname(__file__), "../build/static"),
        check_dir=False,
    ),
    name="static",
)


@app.get("/{path:path}")
async def index(request: Request):
    path = request.path_params.get("path")
    if path == "":
        path = "index.html"
    filepath = os.path.join(os.path.dirname(__file__), f"../build/{path}")
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return FileResponse(os.path.join(os.path.dirname(__file__), "../build/index.html"))
