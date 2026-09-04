# AxonTime HR — Developer Setup Guide

This guide describes how to set up, run, and develop **AxonTime HR** locally.

---

## Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- Docker & Docker Compose
- PostgreSQL 16 (if running without Docker)
- Redis 7 (if running without Docker)

---

## 1. Local Native Setup (Without Docker)

### Backend Setup
1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run FastAPI dev server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start Vite development server:
   ```bash
   npm run dev
   ```

---

## 2. Docker Container Stack Execution

To start the full stack including PostgreSQL, Redis, Backend, Celery Worker, and Frontend:

```bash
docker compose up -d --build
```

To stop containers:
```bash
docker compose down
```

To view logs:
```bash
docker compose logs -f backend
```

---

## 3. Database Migration Workflows

Whenever adding or modifying database models:

1. Generate migration script:
   ```bash
   cd backend
   alembic revision --autogenerate -m "describe_change"
   ```
2. Apply migrations:
   ```bash
   alembic upgrade head
   ```
3. Roll back migration (if needed):
   ```bash
   alembic downgrade -1
   ```
