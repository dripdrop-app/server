from datetime import timezone as tz
from enum import Enum
from pydantic import BaseSettings


class ENV(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


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
    domain: str | None = None
    env: ENV = ENV.DEVELOPMENT
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
    timezone: tz | None = tz.utc

    class Config:
        env_file = ".env"


settings = Settings()


if settings.env == ENV.TESTING or settings.env == ENV.DEVELOPMENT:
    settings.aws_access_key_id = settings.test_aws_access_key_id
    settings.aws_secret_access_key = settings.test_aws_secret_access_key
    settings.aws_s3_bucket = settings.test_aws_s3_bucket

if settings.env == ENV.TESTING:
    settings.async_database_url = settings.test_async_database_url
    settings.database_url = settings.test_database_url
    settings.redis_url = settings.test_redis_url

if settings.database_url.startswith("sqlite"):
    settings.timezone = None
