import time
import random
from app.core.celery_app import celery_app


@celery_app.task(
    name="daily_report",
    bind=True,
    autoretry_for=(ConnectionError,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def daily_report_task(self):
    """
    Simulates a flaky task that fails randomly.
    """
    print(f"📉 Attempt {self.request.retries}: Starting Daily Report...")

    if random.choice([True, False]):
        print("❌ Network Glitch! Raising ConnectionError...")
        raise ConnectionError("Database is unreachable!")

    time.sleep(3)
    print("✅ SUCCESS: Daily Report Generated!")
    return "Report Generated"
