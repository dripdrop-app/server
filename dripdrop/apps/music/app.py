import traceback
from fastapi import FastAPI, Query, UploadFile, Depends, File, HTTPException, status
from pydantic import HttpUrl

from dripdrop.dependencies import get_authenticated_user
from dripdrop.logging import logger
from dripdrop.services import image_downloader, ytdlp

from . import utils
from .jobs import jobs_api
from .responses import (
    GroupingResponse,
    ResolvedArtworkUrlResponse,
    TagsResponse,
    ErrorMessages,
)


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
        video_info = await ytdlp.extract_video_info(url=video_url)
        if not video_info:
            raise Exception()
        uploader = video_info.get("uploader")
        return GroupingResponse(grouping=uploader)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.GROUPING_ERROR
        )


@app.get(
    "/artwork",
    response_model=ResolvedArtworkUrlResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": ErrorMessages.ARTWORK_ERROR}
    },
)
async def get_artwork(artwork_url: HttpUrl = Query(...)):
    try:
        resolved_artwork_url = await image_downloader.resolve_artwork(
            artwork=artwork_url
        )
        return ResolvedArtworkUrlResponse(resolved_artwork_url=resolved_artwork_url)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.ARTWORK_ERROR
        )


@app.post("/tags", response_model=TagsResponse)
async def get_tags(file: UploadFile = File(...)):
    tags = await utils.read_tags(file=await file.read(), filename=file.filename)
    return tags
