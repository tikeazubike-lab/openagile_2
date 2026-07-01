# AGENTS.md — System Mission & Agent Operating Instructions

**Project**: Estate Portfolio Manager (EPM) v2
**Owner**: Zubby (Product Owner)
**Architect**: Claude (The Brain) — OpenAgile Master Project
**Coder/Builder**: Cursor (this agent — replaces Antigravity)
**Tester**: Codex (test branch, SSH to VPS only)
**UI Generator**: Lovable.dev (React frontend, GitHub PR output)
**Spotter**: Grok (verification, current trends)

---

## System Mission

Build and maintain a **personal Nigerian Stock Exchange (NGX) portfolio
tracker** — Estate Portfolio Manager v2 — running on a self-hosted Netcup
VPS using FastAPI + React 18 + PostgreSQL.

The app tracks:
- Active NGX stock holdings (live prices, return %, dividend yield)
- Claims portfolio (delisted/defunct stocks with AMCON/CAC claim tracking)
- Dividend history
- Portfolio NAV history and rebalancing analysis
- Price updates (manual entry + NGX CSV upload)

---

## Non-Negotiable Architectural Rules

Read these before touching any file. They are not preferences — they are
hard constraints established by the architect (Claude) and verified by
the spotter (Grok). Violating them breaks the system.

### 1. Local Workstation — ZERO EXECUTION

The Fedora workstation has a resource constraint (kernel OOM on code
execution). Cursor's role on the local machine is:

```
✅ ALLOWED locally:   git add, git commit, git push, file editing
❌ FORBIDDEN locally: docker, pip, npm, pytest, python, any execution
```

All execution happens on the Netcup VPS (16GB RAM, 8 vCPU) or GitHub
Actions cloud runners. If you need to verify something, push to the
`develop` branch and check GitHub Actions logs, or SSH to the VPS.

### 2. Deployment — GitHub Actions Only

```
NEVER suggest: "run docker compose up locally"
NEVER suggest: "pip install locally"
ALWAYS:        git commit + git push → GitHub Actions deploys
```

Fast path (develop/feature branches): static analysis + build + staging
deploy. No test gate blocks staging. Full path (main/test): full pyramid.

### 3. SSH Heredoc — Always Quote

```bash
# ❌ WRONG — variables interpolate on runner, not server
<< ENDSSH

# ✅ CORRECT — variables resolve on remote server
<< 'ENDSSH'
```

### 4. Database — Never Create New Containers

Reuse the shared `openagile_postgres` container on `openagile_network`.
Database: `estate_portfolio`. User: `openagile`.
Do NOT create a new Postgres container. Ever.

### 5. Backend Session Function Name

```python
# ✅ CORRECT — current codebase uses get_session
from app.database import get_session

# ❌ WRONG — does not exist
from app.database import get_db
```

### 6. JWT Token Function Signature

```python
# ✅ CORRECT
create_access_token(user_id: int, role: str)

# ❌ WRONG — old pattern, not in codebase
create_access_token(data: dict)
```

### 7. Cookie Lifetime — 30-Day Persistent

```python
# ✅ CORRECT — restore/maintain this
response.set_cookie(key="epm_token", max_age=60*60*24*30, httponly=True,
                    secure=True, samesite="strict")

# ❌ WRONG — session-only, removed by Antigravity incorrectly
response.set_cookie(key="epm_token", httponly=True)  # no max_age
```

### 8. Monetary Values — Always Strings in API Responses

```python
# ✅ CORRECT — API contract: monetary values are strings
{"current_value": "12345.50"}

# ❌ WRONG — float causes JS precision loss
{"current_value": 12345.50}
```

### 9. Traefik — All HTTP/HTTPS Must Go Through It

Never expose container ports directly. All routing via Traefik labels.

### 10. bcrypt Pin — Do Not Upgrade

```
bcrypt==4.0.1  # pinned — passlib 1.7.4 breaks with bcrypt >= 4.1.0
```

---

## Current Project State (as of 2026-04-30)

### What is Working
- FastAPI backend running at demo.estate.zubbystudio.shop
- React frontend: Dashboard + Holdings pages with live data
- JWT auth: login, session persistence, 30-day cookie (pending restore)
- Null-safe rendering: fmtNaira(), ReturnText badge, optional chaining

### What is In Progress (Phase 3A)
- Price Entry page (/settings/price-entry) — spec complete, not built
- Auth bug fixes: beforeLoad hydration, logout sequence, cookie restore

### What is Pending (Phase 3A → 3C)
- 13 remaining stub pages (Transactions, Claims, Companies, Dividends, etc.)
- Obsidian vault → PostgreSQL import (import_obsidian.py)
- ClaimRecord table + Claims page
- NAV history snapshots (APScheduler)

---

## Stack Reference

### Backend
```
FastAPI + SQLAlchemy 2.0 (async) + asyncpg
Python 3.12
Alembic (migrations)
bcrypt==4.0.1 + passlib==1.7.4 (auth)
python-jose (JWT)
python-frontmatter (Obsidian import)

File layout:
  backend/app/
    config.py      — settings from env
    database.py    — async engine, get_session()
    deps.py        — auth: create_access_token(user_id, role),
                            verify_password(), hash_password(),
                            get_current_user(), require_admin()
    main.py        — app factory, StaticFiles, SPA catch-all
    models.py      — all SQLAlchemy models (flat single file)
    routers/
      auth.py      — login, logout, me, change-password
      dashboard.py — dashboard KPIs
      holdings.py  — holdings CRUD
      companies.py — company list (new, Phase 3A)
      prices.py    — price entry, bulk CSV, audit, revert (new, Phase 3A)
  backend/scripts/
    seed_admin.py  — reads ADMIN_USERNAME, ADMIN_PASSWORD env vars
                     MUST be idempotent (skip if user exists)
```

### Frontend
```
React 18 + TypeScript + Vite
TanStack Router (file-based, src/routes/)
TanStack Query v5 (server state)
TanStack Table v8 (data tables)
Zustand (authStore + uiStore)
Tailwind v4 (oklch colour tokens, NOT hex arbitrary values)
shadcn/ui (copy-paste pattern)
Lucide React (icons)
DM Mono (numbers) + Plus Jakarta Sans (UI text)

Routing: src/routes/_app.*.tsx (protected)
         src/routes/login.tsx (public)
Stores:  src/store/authStore.ts
         src/store/uiStore.ts
Hooks:   src/hooks/useTheme.ts (system default + dark override)
         src/hooks/useCountUp.ts (KPI animation)
API:     src/api/queries.ts (TanStack Query hooks)
Utils:   src/lib/format.ts (fmtNaira, fmtPct — null-safe)
```

### Infrastructure
```
Docker Compose (single container for EPM)
Traefik v2.10 (routing + SSL)
openagile_postgres (shared — reuse, never recreate)
openagile_network (external bridge — all services on this)
GitHub Actions (CI/CD — only deployment method)
Netcup VPS: 185.216.177.250, user: zubbyik
```

---

## Agent Handover Protocol

When completing a task, always produce a handover brief:

```
**From**: Cursor (Coder/Builder)
**To**: Claude (The Brain)
**Date**: YYYY-MM-DD
**Protocol**: MASTER_CONTEXT.md v4.0

1. What was done (specific files, changes, commands run on VPS)
2. What is verified working (exact test/check performed)
3. What is broken or uncertain (root cause if known)
4. What the next agent should do (numbered action list)
5. Blockers
```

---

## Reference Documents (read before editing these areas)

| File to edit | Read first |
|-------------|-----------|
| Any auth code | CLAUDE_REVIEW_ANTIGRAVITY_HANDOVER_APR29.md |
| prices.py or price entry UI | CLAUDE_PRICE_ENTRY_FINAL_SPEC.md |
| Holdings page | EPM_PHASE2B_ARCHITECTURE.md |
| docker-compose.yml | MASTER_CONTEXT_v4.md §Infrastructure |
| GitHub Actions YAML | MASTER_CONTEXT_v4.md §CI/CD |
| Any new router | ESTATE_PORTFOLIO_FINAL_HANDOVER_v2.md Part B |
