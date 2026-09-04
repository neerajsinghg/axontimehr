# Local Docker Development Guide

## Overview
Run AxonTimeHR locally using Docker Compose with live hot-reloading for both backend (Uvicorn) and frontend (Vite).

## Commands

```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Start local development stack
docker compose -f docker-compose.dev.yml up -d

# 3. View container logs
docker compose -f docker-compose.dev.yml logs -f

# 4. Stop local development stack
docker compose -f docker-compose.dev.yml down
```
