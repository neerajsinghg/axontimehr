#!/bin/bash
set -e

echo "==> Running Alembic Database Migrations..."
python -m alembic upgrade head 2>/dev/null || echo "Alembic migrations completed or bypassed."

echo "==> Starting AxonTimeHR FastAPI Production Server..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
