#! /usr/bin/env bash

export PATH=$PATH:/home/appuser/.local/bin

sleep 10;

echo "--- 🔍 DATABASE SYNC START ---"
echo "--- 🚀 RUNNING ALEMBIC UPGRADE ---"

python -m alembic upgrade head

echo "--- ✅ SYNC COMPLETE ---"
echo "--- 🎬 STARTING APPLICATION ---"

exec "$@"