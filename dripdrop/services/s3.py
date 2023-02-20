import asyncio
import boto3

from dripdrop.settings import settings


class S3:
    AWS_ENDPOINT_URL = settings.aws_endpoint_url
    AWS_REGION_NAME = settings.aws_region_name
    AWS_ACCESS_KEY_ID = settings.aws_access_key_id
    BUCKET = settings.aws_s3_bucket
    ARTWORK_FOLDER = settings.aws_s3_artwork_folder
    MUSIC_FOLDER = settings.aws_s3_music_folder

    @staticmethod
    def resolve_url(filename: str = ...):
        url = f"{S3.BUCKET}.{S3.AWS_REGION_NAME}.digitaloceanspaces.com"
        return f"https://{url}/{filename}"

    def __init__(self) -> None:
        self._session = boto3.Session()
        self._client = self._session.client(
            "s3",
            endpoint_url=S3.AWS_ENDPOINT_URL,
            region_name=S3.AWS_REGION_NAME,
            aws_access_key_id=S3.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    async def upload_file(
        self,
        filename: str = ...,
        body: bytes = ...,
        content_type: str = ...,
        acl="public-read",
    ):
        return await asyncio.to_thread(
            self._client.put_object,
            Bucket=S3.BUCKET,
            Key=filename,
            Body=body,
            ACL=acl,
            ContentType=content_type,
        )

    async def delete_file(self, filename: str = ...):
        return await asyncio.to_thread(
            self._client.delete_object, Bucket=S3.BUCKET, Key=filename
        )

    async def list_objects(self):
        continuation_token = ""
        while True:
            params = {"Bucket": S3.BUCKET}
            if continuation_token:
                params["ContinuationToken"] = continuation_token
            response = await asyncio.to_thread(self._client.list_objects_v2, **params)
            objects = map(lambda object: object["Key"], response["Contents"])
            yield objects
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken", "")


s3 = S3()
