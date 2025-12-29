from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastFlix API"
    ENVIRONMENT: Literal["dev", "test", "prod"] = "dev"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
