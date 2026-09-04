# AxonTime HR — API Specification & Architecture

This document defines the RESTful API standards, versioning rules, error responses, health endpoints, and response formats for **AxonTime HR**.

---

## 1. API Versioning Principle

All business and core application APIs MUST be versioned under `/api/v1/`.

```text
Correct:   /api/v1/health
Correct:   /api/v1/employees
Incorrect: /api/employee
Incorrect: /health
```

---

## 2. Global Response Standard

All API responses follow a structured, predictable JSON envelope.

### Successful Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "request_id": "8f3b2a1c-9d4e-4f5a-8b1c-2d3e4f5a6b7c"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid query parameters provided",
    "details": [
      {
        "field": "limit",
        "issue": "Value must be greater than 0"
      }
    ]
  },
  "request_id": "8f3b2a1c-9d4e-4f5a-8b1c-2d3e4f5a6b7c"
}
```

---

## 3. Phase 1 Health Endpoint

### `GET /api/v1/health`

Returns operational status of the FastAPI backend and connected infrastructure services (PostgreSQL, Redis, Celery).

#### Example Response (200 OK):
```json
{
  "success": true,
  "message": "AxonTime HR API is healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 1.25
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 0.85
    }
  },
  "timestamp": "2026-09-01T10:53:47Z"
}
```

---

## 4. HTTP Status Code Conventions

- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Validation failure or client-side malformed payload.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Authenticated user lacks permission / tenant access violation.
- `404 Not Found`: Resource does not exist.
- `422 Unprocessable Entity`: Data schema validation error.
- `500 Internal Server Error`: Unhandled backend exception (sanitized in production).
