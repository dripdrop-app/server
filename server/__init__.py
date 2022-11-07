import os
from asgiref.sync import sync_to_async
from fastapi import APIRouter, FastAPI, Depends, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from server.api.auth import auth_api
from server.api.music import music_api
from server.api.youtube import youtube_api
from server.dependencies import get_admin_user, get_user
from server.services.cron import cron_service

api_router = APIRouter(prefix="/api", tags=["API"])
api_router.include_router(router=auth_api)
api_router.include_router(router=music_api)
api_router.include_router(router=youtube_api)

app = FastAPI(
    title="DripDrop",
    on_startup=[cron_service.start_cron_jobs],
    on_shutdown=[cron_service.end_cron_jobs],
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


@app.get(
    "/cron/run",
    dependencies=[Depends(get_admin_user)],
    responses={403: {"description": "Not an admin user"}},
    tags=["Cron"],
)
async def run_cronjobs():
    run_cron_jobs = sync_to_async(cron_service.run_cron_jobs)
    await run_cron_jobs()
    return Response(None, 200)


@app.get("/{path:path}", tags=["Index"])
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
