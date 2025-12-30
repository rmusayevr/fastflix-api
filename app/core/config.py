from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastFlix API"
    ENVIRONMENT: Literal["dev", "test", "prod"] = "dev"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def DATABASE_URL(self) -> str:
        """
        Builds the async connection string.
        Only enforces SSL in production environments.
        """
        base_url = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

        if self.ENVIRONMENT == "prod":
            return f"{base_url}?ssl=require"

        return base_url

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
