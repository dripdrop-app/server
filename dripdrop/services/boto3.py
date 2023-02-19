import boto3
from asgiref.sync import sync_to_async

from dripdrop.settings import settings


class Boto3Service:
    AWS_ENDPOINT_URL = settings.aws_endpoint_url
    AWS_REGION_NAME = settings.aws_region_name
    AWS_ACCESS_KEY_ID = settings.aws_access_key_id
    S3_BUCKET = settings.aws_s3_bucket
    S3_ARTWORK_FOLDER = settings.aws_s3_artwork_folder
    S3_MUSIC_FOLDER = settings.aws_s3_music_folder

    @staticmethod
    def resolve_url(filename: str = ...):
        url = f"{Boto3Service.S3_BUCKET}.{Boto3Service.AWS_REGION_NAME}.digitaloceanspaces.com"
        return f"https://{url}/{filename}"

    def __init__(self) -> None:
        self._session = boto3.Session()
        self._client = self._session.client(
            "s3",
            endpoint_url=Boto3Service.AWS_ENDPOINT_URL,
            region_name=Boto3Service.AWS_REGION_NAME,
            aws_access_key_id=Boto3Service.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    async def upload_file(
        self,
        filename: str = ...,
        body: bytes = ...,
        content_type: str = ...,
        acl="public-read",
    ) -> None:
        def _upload_file():
            self._client.put_object(
                Bucket=Boto3Service.S3_BUCKET,
                Key=filename,
                Body=body,
                ACL=acl,
                ContentType=content_type,
            )

        return await sync_to_async(_upload_file)()

    async def delete_file(self, filename: str = ...) -> str:
        def _delete_file():
            self._client.delete_object(Bucket=Boto3Service.S3_BUCKET, Key=filename)

        return await sync_to_async(_delete_file)()

    async def list_objects(self):
        continuation_token = ""
        while True:
            params = {"Bucket": Boto3Service.S3_BUCKET}
            if continuation_token:
                params["ContinuationToken"] = continuation_token
            response = await sync_to_async(self._client.list_objects_v2)(**params)
            objects = map(lambda object: object["Key"], response["Contents"])
            yield objects
            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken", "")


boto3_service = Boto3Service()
