from pydantic import BaseSettings


class Settings(BaseSettings):
    async_database_url: str
    aws_access_key_id: str
    aws_endpoint_url: str
    aws_region_name: str
    aws_secret_access_key: str
    aws_s3_artwork_bucket: str
    aws_s3_music_bucket: str
    database_url: str
    env: str
    google_client_id: str
    google_client_secret: str
    google_api_key: str
    redis_url: str
    secret_key: str
    test_async_database_url = "sqlite+aiosqlite:///test.sqlite"
    test_database_url = "sqlite:///test.sqlite"

    class Config:
        env_file = ".env"


settings = Settings()
