#!/bin/bash
set -e

echo "--- 🔍 DATABASE SYNC START ---"
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Checking Alembic Current Revision:"
alembic current || echo "No version table found."

echo "Checking Alembic Head Revision (Goal):"
alembic heads

echo "--- 🚀 RUNNING UPGRADE ---"
alembic upgrade head

echo "--- ✅ SYNC COMPLETE ---"
echo "--- 🎬 STARTING GUNICORN ---"
exec "$@"