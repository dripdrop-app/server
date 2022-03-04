import os
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(os.path.join(os.path.dirname(__file__), "../build/index.html"))
