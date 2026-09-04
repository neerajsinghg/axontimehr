# AxonTime HR — System Architecture Blueprint

This document defines the core technical architecture, design principles, and system patterns for **AxonTime HR**, a modern, multi-tenant Attendance and HRMS SaaS Platform.

---

## 1. High-Level System Architecture

```text
                                 ┌────────────────────────┐
                                 │      Web Browser       │
                                 │ React 18 + TypeScript  │
                                 └───────────┬────────────┘
                                             │
                                             │ HTTPS
                                             ▼
                                 ┌────────────────────────┐
                                 │         NGINX          │
                                 │     Reverse Proxy      │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │     FastAPI Backend    │
                                 │      (/api/v1/)        │
                                 └───────────┬────────────┘
                                             │
                      ┌──────────────────────┼──────────────────────┐
                      │                      │                      │
                      ▼                      ▼                      ▼
           ┌────────────────────┐  ┌──────────────────┐   ┌──────────────────┐
           │ PostgreSQL 16 DB   │  │  Redis 7 Cache   │   │  Celery Worker   │
           │ Tenant Isolation   │  │  Broker & State  │   │ Background Tasks │
           └────────────────────┘  └──────────────────┘   └──────────────────┘
```

---

## 2. Multi-Tenancy Architecture

AxonTime HR is built as a **Multi-Tenant SaaS Platform** capable of supporting thousands of organizations securely.

### Isolation Model: Discriminator (Column-Level Tenant ID)
- Every tenant-scoped table contains an `organization_id` (UUID foreign key referencing `companies.id`).
- All queries dynamically scope by `organization_id` via SQLAlchemy session middleware or repository-level filtering.
- Tenant context is extracted from authenticated JWT tokens (`tenant_id` claim) and injected into the FastAPI request context.

---

## 3. Backend Architecture (`Router -> Service -> Repository -> Model`)

The backend enforces strict separation of concerns:

```text
HTTP Request
     │
     ▼
API Router (FastAPI) ──────► Pydantic Schemas (Input Validation)
     │
     ▼
Service Layer ─────────────► Business Logic, Rules, Permissions Check
     │
     ▼
Repository Layer ──────────► SQLAlchemy 2.0 Async Queries & DB Abstraction
     │
     ▼
PostgreSQL / Redis
```

---

## 4. Middleware & Cross-Cutting Concerns

1. **Request ID Middleware**: Injects `X-Request-ID` into every HTTP request/response and populates logging context (`correlation_id`).
2. **Global Exception Middleware**: Catches unhandled exceptions and standardizes HTTP error payloads:
   ```json
   {
     "success": false,
     "error": {
       "code": "RESOURCE_NOT_FOUND",
       "message": "Employee not found",
       "details": null
     },
     "request_id": "c1f7a2b9-4d8e-4a31-8f81-229b12a45678"
   }
   ```
3. **CORS Middleware**: Restricts allowed origins using environment-based whitelist (`ALLOWED_ORIGINS`).
4. **Structured Logger**: Formats output in standard JSON with timestamps, log levels, request ID, tenant ID, and execution time.

---

## 5. Background Task Architecture (Celery + Redis)

- Heavy computations (attendance calculations, monthly payroll preparation, PDF/Excel generation, AI analysis, email/push notifications) execute asynchronously outside the HTTP request lifecycle.
- **Broker & Result Backend**: Redis 7.
- Celery workers scale independently as separate background containers.

---

## 6. Frontend Architecture (React + TypeScript + Vite + Tailwind CSS)

```text
React Pages (Views)
     │
     ▼
Custom Hooks (State & TanStack Query)
     │
     ▼
Centralized API Client (Axios Instance with Request Interceptors & Error Handler)
     │
     ▼
FastAPI Backend (/api/v1/)
```

### Key UI Principles:
- **Design System**: Harmonious HSL colors, dark/light dark-mode slate tones, glassmorphism accents, micro-animations.
- **SaaS Dashboard Layout**: Collapsible sidebar, sticky header with health/status indicators, breadcrumbs, search, notification center, and responsive main view.

---

## 7. Status of Architecture Components

| Module | Phase 1 Status | Planned Phase |
| :--- | :--- | :--- |
| Core Stack & Docker | **Implemented** | Phase 1 |
| Database Migration Foundation | **Implemented** | Phase 1 |
| Redis & Celery Foundation | **Implemented** | Phase 1 |
| Structured Logging & Request ID | **Implemented** | Phase 1 |
| Health Monitoring API | **Implemented** | Phase 1 |
| Dashboard UI Shell | **Implemented** | Phase 1 |
| JWT Authentication | Planned | Phase 2 |
| Tenant Context Isolation | Planned | Phase 3 |
| RBAC Granular Permissions | Planned | Phase 3 |
| Employee CRUD | Planned | Phase 4 |
| Attendance Punch Engine | Planned | Phase 5 |
| GPS & Geofencing | Planned | Phase 6 |
| Leave & Holiday Engine | Planned | Phase 7 |
| Regularization & Overtime | Planned | Phase 8 |
| Async Reporting | Planned | Phase 9 |
| Notifications Engine | Planned | Phase 10 |
| Mobile Companion App | Planned | Phase 11 |
| Payroll Processing | Planned | Phase 12 |
| Webhooks & API Keys | Planned | Phase 13 |
| Advanced Analytics | Planned | Phase 14 |
| AI HR Assistant & Anomaly Detection | Planned | Phase 15 |
