from pydantic import BaseSettings


class Settings(BaseSettings):
    env: str
    database_url: str
    redis_url: str
    port: int
    api_key: str
    secret_key: str
    google_client_id: str
    google_client_secret: str
    google_api_key: str
    server_url: str
    # elasticsearch_url: str

    class Config:
        env_file = '.env'


config = Settings()
