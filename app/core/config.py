from pydantic_settings import BaseSettings
from typing import Literal, Optional, List
from pydantic import field_validator, ValidationInfo, AnyHttpUrl


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
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    REDIS_URL: Optional[str] = None

    TMDB_API_KEY: str | None = None
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    MINIO_ROOT_USER: str | None = None
    MINIO_ROOT_PASSWORD: str | None = None

    S3_BUCKET_NAME: str = "fastflix-media"
    S3_ENDPOINT_URL: str | None = None

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"

    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str = "info@fastflix.com"
    EMAILS_FROM_NAME: str = "FastFlix"

    FLOWER_ADMIN: str | None = None
    FLOWER_PASSWORD: str | None = None

    SENTRY_DSN: str | None = None

    GF_SECURITY_ADMIN_PASSWORD: str | None = None

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    DOMAIN: str = "http://localhost:3000"

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    @property
    def CELERY_BROKER_URL(self) -> str:
        """Construct the Redis URL for Celery Broker"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Construct the Redis URL for Celery Results"""
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def DATABASE_URL(self) -> str:
        base_url = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        if self.ENVIRONMENT == "prod":
            return f"{base_url}?ssl=require"
        return base_url

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str) and v.strip():
            return v

        host = info.data.get("REDIS_HOST", "localhost")
        port = info.data.get("REDIS_PORT", 6379)
        db = info.data.get("REDIS_DB", 0)

        return f"redis://{host}:{port}/{db}"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
