from pydantic_settings import BaseSettings
from typing import Literal, List
from functools import cached_property


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastFlix API"
    ENVIRONMENT: Literal["dev", "test", "prod"] = "dev"
    API_V1_STR: str = "/api/v1"
    DOMAIN: str = "http://localhost:3000"

    # --- DATABASE ---
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # --- SECURITY ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ALLOWED_HOSTS_RAW: str = "localhost,127.0.0.1,web"
    BACKEND_CORS_ORIGINS_RAW: str = ""

    # --- INFRASTRUCTURE ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str | None = None

    # --- EXTERNAL SERVICES ---
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

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str
    EMAILS_FROM_NAME: str

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False

    FLOWER_ADMIN: str | None = None
    FLOWER_PASSWORD: str | None = None
    SENTRY_DSN: str | None = None
    GF_SECURITY_ADMIN_PASSWORD: str | None = None

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    MEILI_HOST: str | None = None
    MEILI_MASTER_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        url = (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )
        if self.ENVIRONMENT == "prod":
            return f"{url}?ssl=require"
        return url

    @property
    def CELERY_BROKER_URL(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.CELERY_BROKER_URL

    @cached_property
    def ALLOWED_HOSTS(self) -> List[str]:
        return [h.strip() for h in self.ALLOWED_HOSTS_RAW.split(",") if h.strip()]

    @cached_property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        return [
            o.strip() for o in self.BACKEND_CORS_ORIGINS_RAW.split(",") if o.strip()
        ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
