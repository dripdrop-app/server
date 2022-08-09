import boto3
from server.config import config


AWS_ENDPOINT_URL = "https://dripdrop-space.nyc3.digitaloceanspaces.com"
AWS_REGION_NAME = "nyc3"
AWS_ACCESS_KEY_ID = "DO00QBYAFGTD3EDXDRVH"


session = boto3.Session()
client = session.client(
    "s3",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION_NAME,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.aws_secret_access_key,
)

S3_ARTWORK_BUCKET = "artwork"
S3_MUSIC_BUCKET = "music"


def upload_file(bucket: str, filename: str, body: bytes, acl="public-read"):
    client.put_object(Bucket=bucket, Key=filename, Body=body, ACL=acl)


def delete_file(bucket: str, filename: str):
    client.delete_object(Bucket=bucket, Key=filename)


def resolve_artwork_url(filename: str):
    return f"{AWS_ENDPOINT_URL}/{S3_ARTWORK_BUCKET}/{filename}"


def resolve_music_url(filename: str):
    return f"{AWS_ENDPOINT_URL}/{S3_MUSIC_BUCKET}/{filename}"
