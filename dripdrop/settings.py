from pydantic import BaseSettings


class Settings(BaseSettings):
    aws_endpoint_url: str
    aws_region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_artwork_bucket: str
    aws_s3_music_bucket: str
    env: str
    google_client_id: str
    google_client_secret: str
    google_api_key: str
    postgres_db: str
    postgres_host: str
    postgres_password: str
    postgres_user: str
    redis_url: str
    secret_key: str

    class Config:
        env_file = ".env"


settings = Settings()
