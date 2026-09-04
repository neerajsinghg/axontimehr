# AxonTime HR — Database Architecture Blueprint

This document details the database schema vision, entity relationships, migration rules, and multi-tenant data architecture for **AxonTime HR**.

---

## 1. Overview

- **Database System**: PostgreSQL 16
- **ORM & Driver**: SQLAlchemy 2.0 with `asyncpg` async driver
- **Migrations**: Alembic with versioned Python migration scripts
- **Naming Conventions**: `snake_case` for tables and columns; singular/plural standards (e.g. `companies`, `users`, `employees`).

---

## 2. Multi-Tenant Schema Strategy

Every tenant-owned entity includes:
- `organization_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE`
- Composite index on `(organization_id, id)`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

---

## 3. Database Entity Blueprint (Full SaaS Vision)

```text
                                 ┌──────────────────┐
                                 │    companies     │ (Tenants)
                                 └────────┬─────────┘
                                          │
        ┌───────────────────┬─────────────┼─────────────┬────────────────────┐
        ▼                   ▼             ▼             ▼                    ▼
┌──────────────┐   ┌────────────────┐ ┌───────┐ ┌───────────────┐ ┌───────────────────┐
│ departments  │   │  designations  │ │users  │ │   branches    │ │   subscription    │
└───────┬──────┘   └───────┬────────┘ └───┬───┘ └───────┬───────┘ └───────────────────┘
        │                  │              │             │
        └──────────────────┼──────────────┴─────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │    employees     │
                  └────────┬─────────┘
                           │
        ┌──────────────────┼──────────────────┬──────────────────┐
        ▼                  ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  shifts      │   │  attendance  │   │ leave_types  │   │   payroll    │
└──────────────┘   └───────┬──────┘   └───────┬──────┘   └──────────────┘
                           │                  │
                           ▼                  ▼
                   ┌──────────────┐   ┌──────────────┐
                   │ attendance_  │   │    leave_    │
                   │   punches    │   │   requests   │
                   └──────────────┘   └──────────────┘
```

---

## 4. Phase 1 Database Scope

In Phase 1, the database layer establishes:
1. Alembic configuration (`alembic.ini`, `alembic/env.py`) reading `DATABASE_URL` dynamically from settings.
2. Base declarative model with audit timestamp columns.
3. Database health check query verification (`SELECT 1`).
4. Migration pipeline capable of applying schema changes seamlessly (`alembic upgrade head`).

Business tables (`companies`, `users`, `employees`, `attendance`, etc.) will be created via Alembic migrations starting in Phase 2.
