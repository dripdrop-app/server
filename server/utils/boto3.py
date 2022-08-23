import boto3
from server.config import config


AWS_ENDPOINT_URL = config.aws_endpoint_url
AWS_REGION_NAME = config.aws_region_name
AWS_ACCESS_KEY_ID = config.aws_access_key_id
S3_ARTWORK_BUCKET = config.aws_s3_artwork_bucket
S3_MUSIC_BUCKET = config.aws_s3_music_bucket


session = boto3.Session()
client = session.client(
    "s3",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION_NAME,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.aws_secret_access_key,
)


def upload_file(
    bucket: str, filename: str, body: bytes, content_type: str, acl="public-read"
):
    client.put_object(
        Bucket=bucket, Key=filename, Body=body, ACL=acl, ContentType=content_type
    )


def delete_file(bucket: str, filename: str):
    client.delete_object(Bucket=bucket, Key=filename)


def resolve_artwork_url(filename: str):
    return f"{AWS_ENDPOINT_URL}/{S3_ARTWORK_BUCKET}/{filename}"


def resolve_music_url(filename: str):
    return f"{AWS_ENDPOINT_URL}/{S3_MUSIC_BUCKET}/{filename}"
