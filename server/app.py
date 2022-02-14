import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import FileResponse
from server.api.auth import app as auth_app
from server.api.music import app as music_app
from server.api.youtube import app as youtube_app
from server.config import config
from server.cron import Cron
from server.dependencies import get_user
from server.models import db
from server.queue import q

cron = Cron()

if config.env == "production":
    cron.add_cron(
        "0 1 * * sun", q.enqueue, args=("server.api.youtube.tasks.channel_cleanup",)
    )
    cron.add_cron(
        "0 2 * * *",
        q.enqueue,
        args=("server.api.youtube.tasks.update_youtube_video_categories", True),
    )
    cron.add_cron(
        "0 5 * * *",
        q.enqueue,
        args=("server.api.youtube.tasks.update_active_channels",),
    )
    cron.add_cron(
        "0 3 * * sun",
        q.enqueue,
        args=("server.api.youtube.tasks.update_subscriptions",),
    )

app = FastAPI(
    title="DripDrop",
    on_startup=[db.connect, cron.run],
    on_shutdown=[cron.end, db.disconnect],
    responses={400: {}},
    dependencies=[Depends(get_user)],
)

app.router.include_router(auth_app.router, prefix="/auth")
app.router.include_router(music_app.router, prefix="/music")
app.router.include_router(youtube_app.router, prefix="/youtube")


@app.get("/{path:path}")
async def index(request: Request):
    path = request.path_params.get("path")

    if path == "":
        path = "index.html"

    filepath = os.path.join(os.path.dirname(__file__), f"../build/{path}")

    if os.path.exists(filepath):
        return FileResponse(filepath)

    return FileResponse(os.path.join(os.path.dirname(__file__), "../build/index.html"))
