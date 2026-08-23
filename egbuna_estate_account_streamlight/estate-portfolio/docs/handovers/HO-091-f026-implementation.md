---
type: HO
id: HO-091
title: OpenCode → Claude: F-026 Schema/Backend/Frontend Implemented
date: 2026-07-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-091 — F-026 Registrar Requirements Tracker Implementation

## Schema changes (migration `d1e2f3a4b5c6`)

- `company_registrars` join table (many-to-many, replaces single `companies.registrar_id` FK)
- `registrars.jurisdiction` — `VARCHAR(20) NOT NULL DEFAULT 'nigeria'`
- `companies.security_type` — `VARCHAR(20) NOT NULL DEFAULT 'equity'`
- `registrar_requirements.due_date` — `DATE NULL`
- Backfilled 71 `company_registrars` rows from existing `companies.registrar_id`

## Backend endpoints

- `GET /api/v1/registrars/dashboard-summary` — completion %, health, unmapped companies
- `GET /api/v1/registrar-requirements/global-tracker` — paginated requirements table
- All existing 15+ endpoints retained (registrar CRUD, requirements, documents, company linking)

## Frontend

- `/registrars` redesigned as read-only dashboard (no add/edit/delete)
- `/settings/registrars` new page for admin CRUD
- `RegistrarsDashboard.tsx` — Recharts charts, global tracker table, unmapped companies card
- `RegistrarsLayout.tsx` updated to use dashboard

## Tests

7 new tests (dashboard-summary, global-tracker, backfill, unique constraint). Full suite: 162 passed, 4 xfailed, 8 xpassed.

## Production

- Migration applied via direct psql (Alembic hung on lock contention)
- 71 `company_registrars` rows backfilled — perfect 1:1 mapping
- CHECK constraint renamed to match migration file (HO-096/097)
