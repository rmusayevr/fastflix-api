import multiprocessing
import os

bind = os.getenv("BIND", "0.0.0.0:8000")

workers_str = os.getenv("WEB_CONCURRENCY", None)

if workers_str:
    workers = int(workers_str)
else:
    cores = multiprocessing.cpu_count()
    workers_per_core = float(os.getenv("WORKERS_PER_CORE", "1"))
    default_workers = int(workers_per_core * cores)

    workers = min(default_workers, 4)

if workers < 2:
    workers = 2

worker_class = "uvicorn.workers.UvicornWorker"

max_requests = 1000
max_requests_jitter = 50

timeout = 120
keepalive = 5

loglevel = os.getenv("LOG_LEVEL", "info")
errorlog = "-"
accesslog = "-"
