from pydantic import BaseSettings


class Settings(BaseSettings):
    env: str
    database_url: str
    migration_database_url: str
    redis_url: str
    api_key: str
    secret_key: str
    google_client_id: str
    google_client_secret: str
    google_api_key: str
    aws_endpoint_url: str
    aws_region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_artwork_bucket: str
    aws_s3_music_bucket: str

    class Config:
        env_file = ".env"


settings = Settings()
