import multiprocessing
import os

bind = os.getenv("BIND", "0.0.0.0:8000")

workers_per_core = float(os.getenv("WORKERS_PER_CORE", "1"))
default_web_concurrency = workers_per_core * multiprocessing.cpu_count() + 1
workers = int(os.getenv("WEB_CONCURRENCY", default_web_concurrency))

worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
errorlog = "-"
accesslog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

graceful_timeout = 120
timeout = 120
