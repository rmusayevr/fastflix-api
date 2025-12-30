#!/bin/bash
set -e

echo "--- 🔍 DEPLOYMENT DEBUG START ---"
echo "Current Directory: $(pwd)"
echo "Listing files in /app:"
ls -F

export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "--- 🚀 RUNNING ALEMBIC UPGRADE ---"
alembic upgrade head
echo "--- ✅ ALEMBIC SUCCESSFUL ---"
echo "--- 🎬 STARTING GUNICORN ---"
exec "$@"