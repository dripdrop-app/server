import traceback
from .jobs import music_jobs_api
from asgiref.sync import sync_to_async
from fastapi import (
    APIRouter,
    Query,
    UploadFile,
    Depends,
    File,
    HTTPException,
)
from server.dependencies import get_authenticated_user
from server.logging import logger
from server.models.api import (
    MusicResponses,
    youtube_regex,
)
from server.services.image_downloader import image_downloader_service
from server.services.tag_extractor import tag_extractor_service
from server.services.youtube_downloader import youtuber_downloader_service


music_api = APIRouter(
    prefix="/music",
    tags=["Music"],
    dependencies=[Depends(get_authenticated_user)],
    responses={401: {}},
)
music_api.include_router(router=music_jobs_api)


@music_api.get(
    "/grouping",
    response_model=MusicResponses.Grouping,
    responses={400: {}},
)
async def get_grouping(youtube_url: str = Query(..., regex=youtube_regex)):
    try:
        extract_info = sync_to_async(youtuber_downloader_service.extract_info)
        uploader = await extract_info(link=youtube_url)
        return MusicResponses.Grouping(grouping=uploader).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(400)


@music_api.get(
    "/artwork",
    response_model=MusicResponses.ArtworkURL,
    responses={400: {}},
)
async def get_artwork(artwork_url: str = Query(...)):
    try:
        resolve_artwork = sync_to_async(image_downloader_service.resolve_artwork)
        artwork_url = await resolve_artwork(artwork=artwork_url)
        return MusicResponses.ArtworkURL(artwork_url=artwork_url).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(400)


@music_api.post("/tags", response_model=MusicResponses.Tags)
async def get_tags(file: UploadFile = File(...)):
    read_tags = sync_to_async(tag_extractor_service.read_tags)
    tags = await read_tags(file=await file.read(), filename=file.filename)
    return tags.dict(by_alias=True)
