from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "prod" else None,
    )
    
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "env": settings.ENVIRONMENT,
    }
