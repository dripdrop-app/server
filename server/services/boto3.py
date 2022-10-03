import boto3
from server.config import config


class Boto3Service:
    AWS_ENDPOINT_URL = config.aws_endpoint_url
    AWS_REGION_NAME = config.aws_region_name
    AWS_ACCESS_KEY_ID = config.aws_access_key_id
    S3_ARTWORK_BUCKET = config.aws_s3_artwork_bucket
    S3_MUSIC_BUCKET = config.aws_s3_music_bucket

    def __init__(self) -> None:
        self.session = boto3.Session()
        self.client = self.session.client(
            "s3",
            endpoint_url=Boto3Service.AWS_ENDPOINT_URL,
            region_name=Boto3Service.AWS_REGION_NAME,
            aws_access_key_id=Boto3Service.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.aws_secret_access_key,
        )

    def upload_file(
        self,
        bucket: str = ...,
        filename: str = ...,
        body: bytes = ...,
        content_type: str = ...,
        acl="public-read",
    ):
        self.client.put_object(
            Bucket=bucket, Key=filename, Body=body, ACL=acl, ContentType=content_type
        )

    def delete_file(self, bucket: str = ..., filename: str = ...):
        self.client.delete_object(Bucket=bucket, Key=filename)

    def resolve_artwork_url(self, filename: str = ...):
        return f"{Boto3Service.AWS_ENDPOINT_URL}/{Boto3Service.S3_ARTWORK_BUCKET}/{filename}"

    def resolve_music_url(self, filename: str = ...):
        return (
            f"{Boto3Service.AWS_ENDPOINT_URL}/{Boto3Service.S3_MUSIC_BUCKET}/{filename}"
        )


boto3_service = Boto3Service()
