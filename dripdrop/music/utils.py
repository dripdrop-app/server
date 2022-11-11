import base64
import re
from asgiref.sync import sync_to_async
from dripdrop.services.boto3 import Boto3Service, boto3_service
from typing import Optional


async def handle_artwork_url(job_id: str = ..., artwork_url: Optional[str] = ...):
    if artwork_url:
        is_base64 = re.search("^data:image/", artwork_url)
        if is_base64:
            extension = artwork_url.split(";")[0].split("/")[1]
            dataString = ",".join(artwork_url.split(",")[1:])
            data = dataString.encode()
            data_bytes = base64.b64decode(data)
            artwork_filename = f"{job_id}/artwork.{extension}"
            upload_file = sync_to_async(boto3_service.upload_file)
            await upload_file(
                bucket=Boto3Service.S3_ARTWORK_BUCKET,
                filename=artwork_filename,
                body=data_bytes,
                content_type=f"image/{extension}",
            )
            artwork_url = f"artwork.{extension}"
    return artwork_url
