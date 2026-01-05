import time
from app.core.celery_app import celery_app


@celery_app.task(name="daily_report")
def daily_report_task():
    """
    Simulates generating a daily report.
    """
    print("📈 STARTING DAILY REPORT GENERATION...")
    time.sleep(3)
    print("✅ DAILY REPORT SENT!")
    return "Report Generated Successfully"
