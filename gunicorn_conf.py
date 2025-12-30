import os

port = os.getenv("PORT", "8080")
bind = f"0.0.0.0:{port}"

workers = 2
worker_class = "uvicorn.workers.UvicornWorker"

timeout = 120
loglevel = "info"
