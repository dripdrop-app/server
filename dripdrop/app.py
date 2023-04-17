from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dripdrop.services.websocket_channel import WebsocketChannel
from dripdrop.settings import settings, ENV

from .apps.admin.app import app as admin_app
from .apps.authentication.app import app as auth_app
from .apps.music.app import app as music_app
from .apps.youtube.app import app as youtube_app


api_router = APIRouter(prefix="/api")


def register_router(prefix: str = ..., app: FastAPI = ...):
    api_router.include_router(prefix=prefix, router=app.router, tags=app.openapi_tags)


register_router(prefix="/admin", app=admin_app)
register_router(prefix="/auth", app=auth_app)
register_router(prefix="/music", app=music_app)
register_router(prefix="/youtube", app=youtube_app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    WebsocketChannel.close()


app = FastAPI(
    title="DripDrop",
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
