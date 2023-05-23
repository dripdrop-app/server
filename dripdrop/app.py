from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dripdrop.admin.app import app as admin_app
from dripdrop.authentication.app import app as auth_app
from dripdrop.music import tasks as music_tasks
from dripdrop.music.app import app as music_app
from dripdrop.services import rq_client
from dripdrop.services.scheduler import scheduler
from dripdrop.services.websocket_channel import WebsocketChannel
from dripdrop.settings import settings, ENV
from dripdrop.youtube import tasks as youtube_tasks
from dripdrop.youtube.app import app as youtube_app


api_router = APIRouter(prefix="/api")


def register_router(prefix: str, app: FastAPI):
    api_router.include_router(prefix=prefix, router=app.router, tags=app.openapi_tags)


register_router(prefix="/admin", app=admin_app)
register_router(prefix="/auth", app=auth_app)
register_router(prefix="/music", app=music_app)
register_router(prefix="/youtube", app=youtube_app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.env == ENV.PRODUCTION:
        scheduler.start()
        scheduler.add_job(
            rq_client.high.enqueue,
            trigger=CronTrigger.from_crontab("0 * * * *"),
            args=(youtube_tasks.update_channel_videos),
        )
        scheduler.add_job(
            rq_client.high.enqueue,
            trigger=CronTrigger.from_crontab("0 0 * * *"),
            args=(music_tasks.delete_old_music_jobs),
        )
        scheduler.add_job(
            rq_client.high.enqueue,
            trigger=CronTrigger.from_crontab("30 12 * * *"),
            args=(youtube_tasks.update_subscriptions),
        )
    yield
    if settings.env == ENV.PRODUCTION:
        scheduler.shutdown()
        scheduler.remove_all_jobs()
    WebsocketChannel.close()


app = FastAPI(
    title="dripdrop",
    lifespan=lifespan,
    routes=api_router.routes,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        location = error.get("loc")
        if location:
            location = location[-1]
        message = error.get("msg").replace("this value", location)
        error_messages.append(message)
    return JSONResponse(
        content={"detail": ",".join(error_messages)},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


origins = []
if settings.env == ENV.DEVELOPMENT:
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
async def health_check():
    return Response(None, 200)
