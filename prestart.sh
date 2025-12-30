#!/bin/bash
set -e

echo "--- STARTING PRESTART SCRIPT ---"

# 1. Debug: Check if env vars are present
if [ -z "$POSTGRES_SERVER" ]; then
    echo "ERROR: POSTGRES_SERVER is not set!"
    exit 1
fi

echo "Running migrations against $POSTGRES_SERVER..."

# 2. Run migrations
# We use 'PYTHONPATH=.' to make sure alembic finds your 'app' folder
export PYTHONPATH=$PYTHONPATH:.
alembic upgrade head

echo "--- MIGRATIONS FINISHED SUCCESSFULLY ---"

echo "Starting Gunicorn..."
exec "$@"