#!/bin/bash
set -e

echo "--- 🔍 DATABASE SYNC START ---"
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 1. Simple DB Connection Check
echo "Checking database connectivity..."
python << END
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def check_connection():
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✅ Database connection successful!")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        exit(1)

asyncio.run(check_connection())
END

# 2. Check Alembic State
echo "Current Alembic Revision:"
alembic current || echo "No revision table found."

echo "--- 🚀 RUNNING UPGRADE ---"
alembic upgrade head

echo "--- ✅ SYNC COMPLETE ---"
echo "--- 🎬 STARTING GUNICORN ---"
exec "$@"