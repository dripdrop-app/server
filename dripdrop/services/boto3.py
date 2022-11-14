import boto3
from dripdrop.settings import settings


class Boto3Service:
    AWS_ENDPOINT_URL = settings.aws_endpoint_url
    AWS_REGION_NAME = settings.aws_region_name
    AWS_ACCESS_KEY_ID = settings.aws_access_key_id
    S3_ARTWORK_BUCKET = settings.aws_s3_artwork_bucket
    S3_MUSIC_BUCKET = settings.aws_s3_music_bucket

    def __init__(self) -> None:
        self._session = boto3.Session()
        self._client = self._session.client(
            "s3",
            endpoint_url=Boto3Service.AWS_ENDPOINT_URL,
            region_name=Boto3Service.AWS_REGION_NAME,
            aws_access_key_id=Boto3Service.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

    def upload_file(
        self,
        bucket: str = ...,
        filename: str = ...,
        body: bytes = ...,
        content_type: str = ...,
        acl="public-read",
    ):
        self._client.put_object(
            Bucket=bucket,
            Key=filename,
            Body=body,
            ACL=acl,
            ContentType=content_type,
        )

    def delete_file(self, bucket: str = ..., filename: str = ...):
        self._client.delete_object(Bucket=bucket, Key=filename)

    def delete_folder(self, bucket: str = ..., folder: str = ...):
        response = self._client.list_objects_v2(Bucket=bucket, Prefix=folder)
        for object in response["Contents"]:
            self.delete_file(bucket=bucket, filename=object["key"])

    def resolve_artwork_url(self, filename: str = ...):
        return f"{Boto3Service.AWS_ENDPOINT_URL}/{Boto3Service.S3_ARTWORK_BUCKET}/{filename}"

    def resolve_music_url(self, filename: str = ...):
        return (
            f"{Boto3Service.AWS_ENDPOINT_URL}/{Boto3Service.S3_MUSIC_BUCKET}/{filename}"
        )


boto3_service = Boto3Service()
