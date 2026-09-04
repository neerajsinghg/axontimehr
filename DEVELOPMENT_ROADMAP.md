# AxonTime HR — Development Roadmap

This document outlines the multi-phase roadmap for building **AxonTime HR** into a production-ready, commercial multi-tenant Attendance & HRMS SaaS Platform.

---

## Roadmap Overview

```text
PHASE 1  [CURRENT] ──► Foundation Stack (FastAPI, React, Postgres, Redis, Celery, Docker)
PHASE 2  ────────────► Authentication (JWT, Refresh Tokens, Password Reset)
PHASE 3  ────────────► Multi-tenancy & Granular RBAC
PHASE 4  ────────────► Employee & Organizational Unit Management
PHASE 5  ────────────► Core Attendance Punch Engine
PHASE 6  ────────────► Shifts, GPS Attendance & Geofencing
PHASE 7  ────────────► Leave Management & Holiday Calendars
PHASE 8  ────────────► Attendance Regularization & Overtime Engine
PHASE 9  ────────────► Async Reporting & Export System
PHASE 10 ────────────► Notification Service (In-App, Email, Push)
PHASE 11 ────────────► Mobile Companion Application
PHASE 12 ────────────► Payroll Preparation Engine
PHASE 13 ────────────► External APIs & Webhooks Integration
PHASE 14 ────────────► Advanced HR Analytics & Insights
PHASE 15 ────────────► AI HR Assistant & Anomaly Detection
```

---

## Phase Breakdown

### Phase 1: Foundation (Authorized & In Progress)
- Multi-container Docker Compose setup.
- FastAPI backend with Pydantic v2 settings, structured logging, Request ID middleware, error handlers.
- Database foundation (PostgreSQL + Async SQLAlchemy 2.0 + Alembic).
- Redis service connection & Celery background worker setup.
- React 18 + TypeScript + Vite + Tailwind CSS frontend shell with responsive SaaS layout and foundation dashboard.
- Pytest and Vitest test suites.

### Phase 2: Authentication
- Secure user password hashing (Argon2 / Bcrypt).
- Access Token (short-lived) + Refresh Token (sliding window) flow.
- Password reset token creation & email workflow.

### Phase 3: Multi-Tenancy & RBAC
- Tenant discriminator enforcement (`organization_id`).
- Role definitions (Super Admin, Company Admin, HR Admin, Manager, Employee).
- Granular permissions model (`employee.view`, `attendance.approve`, etc.).

### Phase 4: Employee Management
- Organizational hierarchy (Departments, Designations, Branches, Locations).
- Employee CRUD, profile management, and document metadata.

### Phase 5: Attendance Engine
- Check-In / Check-Out punch engine with timestamp precision.
- Daily attendance status calculation (Present, Late, Early Out, Half Day, Absent).

### Phase 6: Shifts, GPS & Geofencing
- Fixed, rotational, flexible, and overnight shift calculation engines.
- GPS coordinate validation against location geofences.

### Phase 7: Leave & Holiday Management
- Leave balances, leave application, approval workflow, and holiday calendars.

### Phase 8: Regularization & Overtime
- Attendance correction requests, approval workflow, and overtime calculation rules.

### Phase 9: Reporting System
- Async report generation (Excel, CSV, PDF) via Celery.

### Phase 10: Notifications
- Multichannel notification engine (In-App, Email, Push).

### Phase 11: Mobile Application
- React Native / Mobile client integration for employee self-service.

### Phase 12: Payroll Preparation
- Attendance summary rollup to payable days, LOP deductions, and overtime hours.

### Phase 13: APIs & Webhooks
- API Keys management, rate limiting, and outbound event webhooks.

### Phase 14: Advanced Analytics
- Attendance trends, department heatmaps, and absenteeism metrics.

### Phase 15: AI HR Features
- Attendance anomaly detection, automated HR Q&A, and predictive turnover insights.
