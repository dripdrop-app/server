from .admin import app as admin_app
from .authentication import app as auth_app
from .music import app as music_app
from .youtube import app as youtube_app
from dripdrop.settings import settings
from dripdrop.dependencies import get_user
from dripdrop.services.cron import cron_service
from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware


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
    on_startup=[cron_service.start_cron_jobs],
    on_shutdown=[cron_service.end_cron_jobs],
    dependencies=[Depends(get_user)],
    routes=api_router.routes,
)

origins = []
if settings.env != "production":
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
