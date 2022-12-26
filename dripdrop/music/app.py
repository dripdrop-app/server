import traceback
from .jobs import jobs_api
from .models import youtube_regex
from .responses import (
    GroupingResponse,
    ArtworkUrlResponse,
    TagsResponse,
    GroupingErrorResponse,
    ArtworkErrorResponse,
)
from .utils import async_read_tags
from dripdrop.dependencies import get_authenticated_user
from dripdrop.logging import logger
from dripdrop.services.image_downloader import image_downloader_service
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
    responses={status.HTTP_400_BAD_REQUEST: {"description": GroupingErrorResponse}},
)
async def get_grouping(youtube_url: str = Query(..., regex=youtube_regex)):
    try:
        uploader = await youtuber_downloader_service.async_extract_info(
            link=youtube_url
        )
        return GroupingResponse(grouping=uploader).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=GroupingErrorResponse
        )


@app.get(
    "/artwork",
    response_model=ArtworkUrlResponse,
    responses={status.HTTP_400_BAD_REQUEST: {"description": ArtworkErrorResponse}},
)
async def get_artwork(artwork_url: str = Query(...)):
    try:
        artwork_url = await image_downloader_service.async_resolve_artwork(
            artwork=artwork_url
        )
        return ArtworkUrlResponse(artwork_url=artwork_url).dict(by_alias=True)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ArtworkErrorResponse
        )


@app.post("/tags", response_model=TagsResponse)
async def get_tags(file: UploadFile = File(...)):
    tags = await async_read_tags(file=await file.read(), filename=file.filename)
    return TagsResponse(**tags.dict(by_alias=False))
