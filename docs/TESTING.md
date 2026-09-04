# AxonTime HR — Testing Documentation

This document explains the test strategy, structure, and execution steps for **AxonTime HR**.

---

## 1. Test Architecture

### Backend Testing (`backend/tests/`)
- Framework: `pytest` with `pytest-asyncio` and `httpx.AsyncClient`.
- Tests run against the FastAPI application in memory using `ASGITransport`.

### Frontend Testing (`frontend/src/tests/`)
- Framework: `vitest` with `@testing-library/react` and `jsdom`.

---

## 2. Running Backend Tests

```bash
cd backend
python -m pytest -v
```

Expected output:
```text
tests/test_config.py::test_settings_load_defaults PASSED
tests/test_health.py::test_health_endpoint PASSED
```

---

## 3. Running Frontend Tests

```bash
cd frontend
npm run test
```

Expected output:
```text
✓ src/tests/App.test.tsx (1)
  ✓ AxonTime HR App Shell > renders application brand title
```
