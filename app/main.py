import asyncio
import json
import os
import sentry_sdk
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from fastapi import HTTPException, status, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException
from app.core.redis import get_redis_client
from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.core.middleware import SecurityHeadersMiddleware
from app.core.websockets import manager
from app.db.session import AsyncSessionLocal

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

                    if user_id == "ALL":
                        print(f"📢 Broadcasting to all users: {msg_text}")
                        await manager.broadcast(msg_text)
                    elif user_id:
                        await manager.send_personal_message(msg_text, user_id)

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
    setup_logging()

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


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )


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

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    application.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"]
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(SecurityHeadersMiddleware)

    application.mount("/static", StaticFiles(directory="static"), name="static")

    return application


app = create_application()

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[
        ".*admin.*",
        "/metrics",
    ],
)

instrumentator.instrument(app).expose(app)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "environment": settings.ENVIRONMENT,
        "status": "online",
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Checks the health of the application and its dependencies.
    """
    health_status = {"status": "online", "database": "unknown", "redis": "unknown"}

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            health_status["database"] = "online"
    except Exception as e:
        health_status["database"] = "offline"
        health_status["status"] = "offline"
        print(f"❌ Health Check DB Error: {e}")

    try:
        redis = get_redis_client()
        if await redis.ping():
            health_status["redis"] = "online"
        else:
            health_status["redis"] = "offline"
        await redis.close()
    except Exception as e:
        health_status["redis"] = "offline"
        health_status["status"] = "offline"
        print(f"❌ Health Check Redis Error: {e}")

    if health_status["status"] == "offline":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
        )

    return health_status


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


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
