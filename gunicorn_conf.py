import multiprocessing
import os

port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"

workers = int(os.getenv("WEB_CONCURRENCY", "3"))

worker_class = "uvicorn.workers.UvicornWorker"

keepalive = 120
timeout = 120
errorlog = "-"
accesslog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

graceful_timeout = 120
