import traceback
from .jobs import jobs_api
from .models import youtube_regex
from .responses import GroupingResponse, ArtworkUrlResponse, TagsResponse
from asgiref.sync import sync_to_async
from dripdrop.dependencies import get_authenticated_user
from dripdrop.logging import logger
from dripdrop.services.image_downloader import image_downloader_service
from dripdrop.services.tag_extractor import tag_extractor_service
from dripdrop.services.youtube_downloader import youtuber_downloader_service
from fastapi import FastAPI, Query, UploadFile, Depends, File, HTTPException, status


app = FastAPI(
    openapi_tags=["Music"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
app.include_router(router=jobs_api)


@app.get(
    "/grouping",
    response_model=GroupingResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Unable to get grouping"}},
)
async def get_grouping(youtube_url: str = Query(..., regex=youtube_regex)):
    try:
        extract_info = sync_to_async(youtuber_downloader_service.extract_info)
        uploader = await extract_info(link=youtube_url)
        return GroupingResponse(grouping=uploader).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to get grouping"
        )


@app.get(
    "/artwork",
    response_model=ArtworkUrlResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": "Unable to get artwork"}},
)
async def get_artwork(artwork_url: str = Query(...)):
    try:
        resolve_artwork = sync_to_async(image_downloader_service.resolve_artwork)
        artwork_url = await resolve_artwork(artwork=artwork_url)
        return ArtworkUrlResponse(artwork_url=artwork_url).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to get artwork"
        )


@app.post("/tags", response_model=TagsResponse)
async def get_tags(file: UploadFile = File(...)):
    read_tags = sync_to_async(tag_extractor_service.read_tags)
    tags = await read_tags(file=await file.read(), filename=file.filename)
    return TagsResponse(**tags.dict(by_alias=False))
