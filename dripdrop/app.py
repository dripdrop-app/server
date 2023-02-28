from fastapi import APIRouter, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dripdrop.services.cron import cron
from dripdrop.services.websocket_handler import websocket_handler
from dripdrop.settings import settings, ENV

from .apps.admin.app import app as admin_app
from .apps.authentication.app import app as auth_app
from .apps.music.app import app as music_app
from .apps.youtube.app import app as youtube_app
from .http_client import http_client
from .redis import redis

api_router = APIRouter(prefix="/api")
api_router.include_router(
    prefix="/admin", router=admin_app.router, tags=admin_app.openapi_tags
)
api_router.include_router(
    prefix="/auth", router=auth_app.router, tags=auth_app.openapi_tags
)
api_router.include_router(
    prefix="/music", router=music_app.router, tags=music_app.openapi_tags
)
api_router.include_router(
    prefix="/youtube", router=youtube_app.router, tags=youtube_app.openapi_tags
)

app = FastAPI(
    title="DripDrop",
    on_startup=[cron.start_cron_jobs],
    on_shutdown=[
        cron.end_cron_jobs,
        http_client.aclose,
        redis.close,
        websocket_handler.close,
    ],
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
