import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.api.dependencies import get_current_admin
from app.tasks.export_tasks import export_movies_task

router = APIRouter()


async def log_generator() -> AsyncGenerator[str, None]:
    """
    Simulates a long-running process (like a backup or import).
    Yields data chunk by chunk.
    """
    steps = [
        "Initializing backup process...",
        "Connecting to database...",
        "Dumping table: users...",
        "Dumping table: movies...",
        "Compressing archives...",
        "Uploading to S3...",
        "Verifying integrity...",
        "Backup completed successfully! ✅",
    ]

    for step in steps:
        await asyncio.sleep(1)
        yield f"data: {step}\n\n"


@router.get("/stream-logs")
async def stream_logs(current_admin=Depends(get_current_admin)):
    """
    Server-Sent Event (SSE) endpoint.
    Client keeps connection open and receives updates.
    """
    return StreamingResponse(log_generator(), media_type="text/event-stream")


@router.post("/export-movies")
async def trigger_export(current_admin=Depends(get_current_admin)):
    """
    Trigger the background export task.
    """
    export_movies_task.delay(current_admin.id)

    return {"message": "Export started! We will notify you when it is ready."}
