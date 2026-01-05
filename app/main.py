import asyncio
import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException
from app.core.redis import (
    get_redis_client,
)
from app.core.websockets import manager

os.makedirs("static/exports", exist_ok=True)


async def subscribe_to_notifications():
    """
    Background Task:
    Listens to the Redis 'notifications' channel (published by Celery workers)
    and forwards the message to the local WebSocket manager to push to users.
    """
    redis = get_redis_client()
    pubsub = redis.pubsub()
    await pubsub.subscribe("notifications")

    print("🎧 Redis Pub/Sub Listener Started")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    user_id = data.get("user_id")
                    msg_text = data.get("message")

                    if user_id and msg_text:
                        await manager.send_personal_message(msg_text, user_id)

                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON received in Redis: {message['data']}")
                except Exception as e:
                    print(f"⚠️ Error processing Redis message: {e}")

    except asyncio.CancelledError:
        print("🛑 Redis Listener Stopping...")
    finally:
        await pubsub.unsubscribe("notifications")
        await pubsub.close()
        await redis.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_limiter = get_redis_client()
    await FastAPILimiter.init(redis_limiter)

    task = asyncio.create_task(subscribe_to_notifications())

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    await redis_limiter.close()


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

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "env": settings.ENVIRONMENT,
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
