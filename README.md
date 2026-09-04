# AxonTimeHR — Enterprise Attendance & HRMS SaaS Platform

**AxonTimeHR** is a modern, commercial-grade, multi-tenant Attendance, HRMS, Payroll, Performance, Workforce Management, Compliance, & AI Intelligence Platform built with **FastAPI, React + TypeScript, PostgreSQL, Redis, Celery, and Docker**.

---

## 🏛️ Architecture & Stack

```text
Reverse Proxy (Nginx/Caddy with TLS)
  ├── React + TypeScript Frontend (Port 80/443)
  └── FastAPI Python Backend (Port 8000)
        ├── PostgreSQL 15 (Persistent Storage)
        ├── Redis 7 (Cache & Task Broker)
        └── Celery Workers & Beat (Scheduled & Asynchronous Processing)
```

---

## 🚀 Quick Start with Docker

```bash
# 1. Clone repository
git clone https://github.com/axontimehr/axontimehr.git
cd axontimehr

# 2. Configure environment
cp .env.example .env

# 3. Start full container stack
docker compose up -d

# 4. Seed demo data (Optional)
docker exec -it axontimehr-backend python app/db/seed_demo.py
```

---

## 🔑 Default Sandbox Credentials

- **URL**: `http://localhost` (or `https://dev.axontimehr.com`)
- **Admin Email**: `admin@axontimehr.com`
- **Password**: `Password123!`

---

## 🧪 Running Automated Tests

```bash
# Backend Pytest Integration Suite
cd backend
python -m pytest -v

# Frontend Vite Build Verification
cd frontend
npm run build
```

---

## 📄 License
Licensed under the [Apache License 2.0](LICENSE).
