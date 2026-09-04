# AxonTimeHR Release Changelog

## [14.0.0] - 2026-09-02
### Added
- Multi-stage Docker containerization (`backend/Dockerfile`, `frontend/Dockerfile`).
- Docker Compose orchestration (`docker-compose.yml`, `docker-compose.dev.yml`).
- Nginx Reverse Proxy with TLS/HTTPS proxying & same-origin API routing.
- Alembic database migration entrypoint & CLI demo seeder (`seed_demo.py`).
- Automated pg_dump database backup & restore scripts (`backup_db.sh`, `restore_db.sh`).
- GitHub Actions CI/CD workflows (`.github/workflows/ci.yml`).
- Open-Source deployment documentation under `docs/deployment/`.

## [13.0.0] - 2026-09-02
### Added
- AxonTime AI Copilot & Conversational Decision Support.
- Centralized Metric Catalog & Aggregation Engine.
- Anomaly Detection Center (Attendance, Payroll, Expense).
- Predictive Attrition Forecaster & 12-Month Forecasting.
- "What-If" Scenario Analysis Tool & Custom BI Dashboard Builder.
