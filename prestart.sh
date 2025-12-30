#!/bin/bash
set -e

echo "--- 🔍 DATABASE SYNC START ---"
export PYTHONPATH=$PYTHONPATH:$(pwd)


echo "--- 🚀 RUNNING ALEMBIC UPGRADE ---"
alembic upgrade head

echo "--- ✅ SYNC COMPLETE ---"
echo "--- 🎬 STARTING GUNICORN ---"
exec "$@"