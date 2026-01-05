import csv
import os
import uuid
import time
from asgiref.sync import async_to_sync
from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.notification_service import NotificationService
from app.models.movie import Movie
from app.models.user import UserModel
from app.models.rating import RatingModel
from app.models.watchlist import WatchlistModel
from sqlalchemy import select

EXPORT_DIR = "static/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


async def _export_movies_logic(user_id: int):
    """
    The actual async logic to query DB and write CSV.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Movie))
        movies = result.scalars().all()

        filename = f"movies_export_{uuid.uuid4().hex}.csv"
        filepath = os.path.join(EXPORT_DIR, filename)

        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Title", "Release Year", "Rating", "Slug"])
            for movie in movies:
                writer.writerow(
                    [
                        movie.id,
                        movie.title,
                        movie.release_year,
                        movie.average_rating,
                        movie.slug,
                    ]
                )

        download_url = f"/static/exports/{filename}"
        message = f"✅ Your Movie Export is ready! <a href='{download_url}' target='_blank'>Download CSV</a>"

        await NotificationService.send_notification(user_id, message, db)


@celery_app.task(name="fetch_movies_data")
def fetch_movies_data_task(user_id: int):
    """Step 1: Get the data (Simulated returning a list of IDs)"""
    print(f"Fetching data for User {user_id}...")
    return {"user_id": user_id, "movie_count": 100, "filename": "movies_export.csv"}


@celery_app.task(name="write_csv_file")
def write_csv_file_task(data: dict):
    """Step 2: Do the heavy CPU work"""
    user_id = data["user_id"]
    print(f"Writing CSV for User {user_id}...")

    time.sleep(2)

    data["file_path"] = f"/static/exports/{data['filename']}"
    return data


@celery_app.task(name="notify_export_completion")
def notify_export_completion_task(data: dict):
    """Step 3: Notify the user"""
    user_id = data["user_id"]
    file_path = data["file_path"]

    print(f"Notifying User {user_id}...")

    print(f"✅ DONE! Download at: {file_path}")
    return "Export Workflow Complete"


@celery_app.task(name="export_movies")
def export_movies_task(user_id: int):
    """
    The Sync Wrapper for Celery.
    """
    async_to_sync(_export_movies_logic)(user_id)
    return f"Export generated for User {user_id}"
