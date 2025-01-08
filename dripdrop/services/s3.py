import asyncio

import boto3

from dripdrop.settings import settings

AWS_ENDPOINT_URL = settings.aws_endpoint_url
AWS_REGION_NAME = settings.aws_region_name
AWS_ACCESS_KEY_ID = settings.aws_access_key_id
BUCKET = settings.aws_s3_bucket
ARTWORK_FOLDER = settings.aws_s3_artwork_folder
MUSIC_FOLDER = settings.aws_s3_music_folder


def resolve_url(filename: str = ...):
    return f"{AWS_ENDPOINT_URL}/{BUCKET}/{filename}"


_client = boto3.client(
    "s3",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION_NAME,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.aws_secret_access_key,
)


async def upload_file(
    filename: str,
    body: bytes,
    content_type: str,
    acl="public-read",
):
    return await asyncio.to_thread(
        _client.put_object,
        Bucket=BUCKET,
        Key=filename,
        Body=body,
        ACL=acl,
        ContentType=content_type,
    )


async def delete_file(filename: str):
    return await asyncio.to_thread(_client.delete_object, Bucket=BUCKET, Key=filename)


async def list_objects():
    continuation_token = ""
    while True:
        params = {"Bucket": BUCKET}
        if continuation_token:
            params["ContinuationToken"] = continuation_token
        response = await asyncio.to_thread(_client.list_objects_v2, **params)
        objects = map(lambda object: object["Key"], response.get("Contents", []))
        yield objects
        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken", "")
