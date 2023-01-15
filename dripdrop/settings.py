from datetime import timezone
from pydantic import BaseSettings


class Settings(BaseSettings):
    async_database_url: str
    aws_access_key_id: str
    aws_endpoint_url: str
    aws_region_name: str
    aws_secret_access_key: str
    aws_s3_artwork_folder: str
    aws_s3_bucket: str
    aws_s3_music_folder: str
    database_url: str
    env: str
    google_client_id: str
    google_client_secret: str
    google_api_key: str
    redis_url: str
    secret_key: str
    test_async_database_url: str
    test_aws_access_key_id: str
    test_aws_s3_bucket: str
    test_aws_secret_access_key: str
    test_database_url: str
    test_redis_url: str
    test_timezone: timezone | None = timezone.utc

    class Config:
        env_file = ".env"


settings = Settings()

if settings.env == "testing" or settings.env == "development":
    settings.aws_access_key_id = settings.test_aws_access_key_id
    settings.aws_secret_access_key = settings.test_aws_secret_access_key
    settings.aws_s3_bucket = settings.test_aws_s3_bucket

if settings.env == "testing":
    settings.async_database_url = settings.test_async_database_url
    settings.database_url = settings.test_database_url
    settings.redis_url = settings.test_redis_url
    settings.test_timezone = (
        None if settings.database_url.startswith("sqlite") else True
    )
