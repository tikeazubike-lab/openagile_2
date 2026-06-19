# architecture.md — EPM Architecture

## Stack

Backend:

Framework: FastAPI 0.115.6

Language: Python 3.12

ORM: SQLAlchemy 2.0.36 async

Migrations: Alembic 1.14.0

DB driver: asyncpg 0.30.0

Database: PostgreSQL 15 (shared openagile_postgres — NEVER create a new one)

Auth: JWT httpOnly cookie, 30-day persistent, bcrypt==4.0.1 PINNED

PDF parsing: pdfplumber 0.11.4

Vault parse: python-frontmatter 1.1.0

XIRR: scipy 1.13.1 (NOT yet in requirements.txt — add before implementing)

Scheduler: APScheduler 3.10.4 (NOT yet in requirements.txt — add before implementing)

Frontend:

Framework: React 18 + TypeScript + Vite

Routing: TanStack Router (file-based, src/routes/)

Server state:TanStack Query v5

UI state: Zustand (authStore, uiStore)

Tables: TanStack Table v8

Charts: Recharts

Styling: Tailwind v4 + oklch CSS variables

Components: shadcn/ui (copy-paste, not a package dependency)

Icons: Lucide React

Infrastructure:

Container: Single Docker container (FastAPI serves React static files)

Compose: docker-compose.v2.yml

Proxy:          Traefik v2.10

TLS Provider:   Let's Encrypt

DNS Challenge:  Cloudflare

Network: openagile_network (external bridge)

Domain: testdrive.epm.zubbystudio.shop (test drive)

Deployment: Direct on VPS — docker compose build + up

---

## Project Root on VPS

/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/

Key paths:

backend/app/main.py — FastAPI factory + router registration + SPA catch-all

backend/app/database.py — get_session() async session factory

backend/app/deps.py — auth functions

backend/app/models.py — ALL SQLAlchemy models (flat single file)

backend/app/routers/ — one file per domain

backend/app/services/ — business logic

backend/scripts/ — seed and import scripts

backend/tests/ — ONLY test tree (epm-tests/ was duplicate — deleted)

estate-portfolio-manager/src/routes/ — TanStack file-based routes

estate-portfolio-manager/src/api/queries.ts — all TanStack Query hooks

estate-portfolio-manager/src/lib/format.ts — fmtNaira, fmtPct (null-safe)

---

## Invariants — Rules the System Must Never Violate

AUTH:

bcrypt==4.0.1 — DO NOT UPGRADE (passlib 1.7.4 incompatible with >= 4.1.0)

Cookie: max_age=60*60*24*30, httponly=True, secure=True, samesite="strict"

Never session-only cookie (no max_age) — this was a confirmed bug

JWT never in localStorage — httpOnly cookie only

DATABASE:

Session function: get_session() — NOT get_db() (does not exist)

Soft delete: deleted_at = datetime.now(timezone.utc) — NOT datetime.utcnow()

Never hard delete any record

Never create a new Postgres container — reuse shared openagile_postgres

API CONTRACT:

All monetary values as JSON strings: "12345.50" not 12345.50

Recharts exception: parse strings to floats at component boundary only

Token function: create_access_token(user_id: int, role: str)

Response envelope: { "data": ..., "meta": { "total": N }, "error": null }

Soft-deleted records excluded from all responses by default

FRONTEND:

All API calls: credentials: 'include' (httpOnly cookie must be sent)

All colours: var(--token-name) — NEVER hardcoded hex

All monetary display: fmtNaira(value ?? null) from lib/format.ts

Null-safe: value?.toFixed(2) ?? "—" — never assume non-null API data

---

## Database Models (13 total in models.py)

User, Registrar, RegistrarContactField, RegistrarRequirement,

RegistrarDocument, Company, Holding, ClaimRecord, Transaction,

Dividend, PriceHistory, PriceAudit, ObsidianSyncLog

---

## API Routers (40 endpoints total)

auth.py — /api/v1/auth (login, logout, me, change-password)

dashboard.py — /api/v1/dashboard

holdings.py — /api/v1/holdings

companies.py — /api/v1/companies

prices.py — /api/v1/prices (quick, pdf, csv, audit, revert, history)

registrars.py — /api/v1/registrars + requirements + documents

claims.py — /api/v1/claims

obsidian.py — /api/v1/obsidian

---

## Holdings Classification

holding_type = 'active'

Companies with status: listed, merged

Cost basis = num_shares × avg_purchase_price

return_pct computed and shown

holding_type = 'claim'

Companies with status: delisted, defunct, uncertain

cost_basis_override = 0 (zero — not the purchase price)

return_pct = null (never computed — mathematically undefined)

Tracked for AMCON/CAC claim administration via ClaimRecord table

---

## Financial Formulas

Average Cost = (Σ shares_bought × price_per_buy) / total_shares

Cost Basis = num_shares × avg_purchase_price

Current Value = num_shares × current_price

Return [%] = ((current_value - cost_basis) / cost_basis) × 100

Total Assets = ac

tive_portfolio_value + claims_portfolio_value

where claims_portfolio_value = actual_payout if paid, expected_payout if pending
