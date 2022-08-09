import os
from asgiref.sync import sync_to_async
from fastapi import APIRouter, FastAPI, Depends, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from server.api.auth.main import app as auth_app
from server.api.music.main import app as music_app
from server.api.youtube.main import app as youtube_app
from server.cron import cron_start, cron_end, run_crons
from server.dependencies import get_admin_user, get_user
from server.models.main import db


api_router = APIRouter(prefix="/api")
api_router.include_router(auth_app.router, prefix="/auth")
api_router.include_router(music_app.router, prefix="/music")
api_router.include_router(youtube_app.router, prefix="/youtube")

app = FastAPI(
    title="DripDrop",
    on_startup=[db.connect, cron_start],
    on_shutdown=[cron_end, db.disconnect],
    responses={400: {}},
    dependencies=[Depends(get_user)],
    routes=api_router.routes,
)


app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(os.path.dirname(__file__), "../build/static"),
        check_dir=False,
    ),
    name="static",
)


@app.get("/cron/run", dependencies=[Depends(get_admin_user)], responses={403: {}})
async def run_cronjobs():
    run_crons_async = sync_to_async(run_crons)
    await run_crons_async()
    return Response(None, 200)


@app.get("/{path:path}")
async def index(request: Request):
    path = request.path_params.get("path")
    if path == "":
        path = "index.html"
    filepath = os.path.join(os.path.dirname(__file__), f"../build/{path}")
    if os.path.exists(filepath):
        return FileResponse(filepath)
    index_page = os.path.join(os.path.dirname(__file__), "../build/index.html")
    if os.path.exists(index_page):
        return FileResponse(index_page)
    return Response(None, 500)
