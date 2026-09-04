# DevOps Troubleshooting & Diagnostics Guide

## Common Issues & Resolutions

### 1. PostgreSQL Database Connection Error
- **Symptom**: `asyncpg.exceptions.CannotConnectNowError` or `Connection refused`.
- **Fix**: Verify `axontimehr-postgres` health status via `docker compose ps`. Ensure `DATABASE_URL` matches PostgreSQL container credentials.

### 2. Alembic Migration Lock / Error
- **Fix**: Run `docker exec -it axontimehr-backend python -m alembic current` to verify migration version. Run `python -m alembic upgrade head`.

### 3. Frontend Proxy 502 Bad Gateway
- **Fix**: Check `axontimehr-backend` container logs: `docker logs axontimehr-backend`. Ensure backend port 8000 is listening.
