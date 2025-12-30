#!/bin/bash
set -e

echo "--- 🔍 DATABASE SYNC START ---"
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Waiting for database connection..."
python -c "import asyncio; from app.core.config import settings; from sqlalchemy.ext.asyncio import create_async_engine; async def check(): engine = create_async_engine(settings.DATABASE_URL); async with engine.connect() as conn: await conn.execute('SELECT 1'); print('Connection successful!'); await engine.dispose(); asyncio.run(check())"

echo "Current Alembic Revision:"
alembic current || echo "No revision found."

echo "--- 🚀 RUNNING UPGRADE ---"
alembic upgrade head

echo "--- ✅ SYNC COMPLETE ---"
echo "--- 🎬 STARTING GUNICORN ---"
exec "$@"