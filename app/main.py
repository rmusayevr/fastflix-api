import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter

from app.core.config import settings
from app.core.redis import redis_client
from app.api.v1.router import api_router
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException
from fastapi.middleware.cors import CORSMiddleware


os.makedirs("static/exports", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await FastAPILimiter.init(redis_client)
    yield
    await redis_client.close()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "environment": settings.ENVIRONMENT,
        "status": "online",
    }


@app.exception_handler(MovieNotFoundException)
async def movie_not_found_handler(request: Request, exc: MovieNotFoundException):
    return JSONResponse(
        status_code=404, content={"error": "Not Found", "detail": exc.message}
    )


@app.exception_handler(NotAuthorizedException)
async def not_authorized_handler(request: Request, exc: NotAuthorizedException):
    return JSONResponse(
        status_code=403, content={"error": "Forbidden", "detail": exc.message}
    )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "env": settings.ENVIRONMENT,
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
