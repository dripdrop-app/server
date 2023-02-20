import traceback
from fastapi import FastAPI, Query, UploadFile, Depends, File, HTTPException, status
from pydantic import HttpUrl

from dripdrop.services.ytdlp import ytdlp
from dripdrop.dependencies import get_authenticated_user
from dripdrop.logging import logger
from dripdrop.services.image_downloader import image_downloader

from .jobs import jobs_api
from .responses import (
    GroupingResponse,
    ArtworkUrlResponse,
    TagsResponse,
    ErrorMessages,
)
from .utils import read_tags


app = FastAPI(
    openapi_tags=["Music"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
app.include_router(router=jobs_api)


@app.get(
    "/grouping",
    response_model=GroupingResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": ErrorMessages.GROUPING_ERROR}
    },
)
async def get_grouping(video_url: HttpUrl = Query(...)):
    try:
        videos_info = await ytdlp.extract_videos_info(url=video_url)
        if not videos_info:
            raise Exception()
        video_info = videos_info[0]
        uploader = video_info.get("uploader")
        return GroupingResponse(grouping=uploader)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.GROUPING_ERROR
        )


@app.get(
    "/artwork",
    response_model=ArtworkUrlResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": ErrorMessages.ARTWORK_ERROR}
    },
)
async def get_artwork(artwork_url: HttpUrl = Query(...)):
    try:
        artwork_url = await image_downloader.resolve_artwork(artwork=artwork_url)
        return ArtworkUrlResponse(artwork_url=artwork_url)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.ARTWORK_ERROR
        )


@app.post("/tags", response_model=TagsResponse)
async def get_tags(file: UploadFile = File(...)):
    tags = await read_tags(file=await file.read(), filename=file.filename)
    return tags
