from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.exceptions import MovieNotFoundException, NotAuthorizedException


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
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
