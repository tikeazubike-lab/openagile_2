# SYSTEM_SURVEY — Estate Portfolio Manager (EPM)
**Date**: 2026-06-15
**Source**: VPS audit at /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/
**Status**: Phase 1 — Read-only survey. No code changes.

---

## architecture_summary

EPM v2 is a self-hosted Nigerian stock portfolio tracker. The application
is a FastAPI backend serving a React 18 SPA from static files, deployed
as a single Docker container behind Traefik on a Netcup VPS. A legacy
Streamlit v1 app (docker-compose.yml) still runs in parallel at the
production domain while v2 runs at the staging domain. No GitHub Actions
CI/CD pipeline exists — deployment is handled by a manual deploy.sh script.

---

## modules

### Backend (backend/app/)
| Module | File | Lines | Purpose |
|--------|------|-------|---------|
| Config | config.py | 40 | Settings from env vars (pydantic-settings) |
| Database | database.py | 35 | Async SQLAlchemy engine, get_session() |
| Deps | deps.py | 97 | JWT auth, role guards, token creation |
| Main | main.py | 97 | FastAPI factory, router registration, SPA catch-all |
| Models | models.py | 374 | 14 SQLAlchemy models (flat single file) |
| Auth router | routers/auth.py | 124 | Login, logout, /me, change-password |
| Dashboard router | routers/dashboard.py | 140 | KPIs, sector allocation, top holdings |
| Holdings router | routers/holdings.py | 246 | CRUD + publish + soft delete |
| Companies router | routers/companies.py | 37 | List only (no CRUD UI yet) |
| Prices router | routers/prices.py | 620 | Quick entry, PDF upload, CSV, audit, revert, history |
| Registrars router | routers/registrars.py | 579 | Full CRUD + requirements + documents + company linking |
| Claims router | routers/claims.py | 115 | CRUD for AMCON/CAC claim records |
| Obsidian router | routers/obsidian.py | 35 | Import trigger + sync log |
| Portfolio service | services/portfolio.py | 40 | Business logic (currently minimal) |

### Scripts (backend/scripts/)
| Script | Lines | Purpose |
|--------|-------|---------|
| seed_admin.py | 67 | Idempotent admin user creation |
| seed_ngx_companies.py | 210 | One-time NGX company population from PDF |
| import_obsidian.py | 261 | Obsidian vault → PostgreSQL migration |

### Root-level scripts (⚠️ SCATTERED — should be in scripts/)
| File | Purpose |
|------|---------|
| scripts/ngx_scraper.py | NGX price scraper (status unclear) |
| scripts/rapidapi_scraper.py | RapidAPI scraper (likely defunct) |
| scripts/yfinance_scraper.py | yfinance scraper (no NGX coverage — defunct) |
| scripts/test_apis.py | Ad-hoc API testing |
| extract_tickers.py | One-off ticker extraction utility |
| extract_tickers_from_txt.py | Duplicate of above |
| test_pdf.py → test_pdf8.py | 8 PDF parser development experiments |
| test_regex.py → test_regex3.py | 3 regex development experiments |

### Frontend (estate-portfolio-manager/src/)
| Layer | Files | Status |
|-------|-------|--------|
| Routes | 19 .tsx files | All pages exist — some are StubPage |
| Components (domain) | 17 files | holdings, registrars, layout, shared |
| Components (shadcn/ui) | 47 files | Full shadcn library installed |
| API hooks | queries.ts (30+ hooks) | All domains covered |
| Stores | authStore.ts, uiStore.ts | Zustand |
| Hooks | useTheme.ts, useCountUp.ts | Custom hooks |
| Utils | lib/format.ts | fmtNaira, fmtPct |

---

## dependencies

### Backend (requirements.txt — 19 packages)
```
alembic==1.14.0        migrations
asyncpg==0.30.0        async postgres driver
bcrypt==4.0.1          PASSWORD HASH — DO NOT UPGRADE (passlib incompatibility)
cryptography==44.0.0   JWT support
fastapi==0.115.6       web framework
httpx==0.28.1          async HTTP client (tests)
jsonschema==4.23.0     API contract validation
passlib==1.7.4         password hashing wrapper
pydantic==2.10.3       data validation
pydantic-settings==2.7.0  config from env
pytest==8.4.1          test runner
pytest-asyncio==1.3.0  async test support
python-frontmatter==1.1.0  Obsidian vault parsing
pdfplumber==0.11.4     NGX PDF parsing
python-jose==3.3.0     JWT encoding/decoding
python-multipart==0.0.20  file upload support
SQLAlchemy==2.0.36     ORM
uvicorn==0.32.1        ASGI server
```

⚠️ Missing from requirements.txt:
- scipy (needed for XIRR — specced but not installed)
- APScheduler (needed for NAV History automation — specced but not installed)

⚠️ Root-level requirements.txt also exists — likely Streamlit v1 leftover.

### Frontend (key packages from audit context)
- React 18 + TypeScript + Vite
- @tanstack/router, @tanstack/query, @tanstack/table
- Zustand, Recharts, Tailwind v4, Lucide React
- shadcn/ui (full component library — 47 components)

---

## entrypoints

| Entrypoint | Path | Purpose |
|-----------|------|---------|
| FastAPI app | backend/app/main.py | API + SPA static serving |
| React SPA | estate-portfolio-manager/src/routes/__root.tsx | Client routing root |
| Streamlit v1 | app.py (root level) | Legacy app (still running) |
| Docker v1 | docker-compose.yml | Streamlit container |
| Docker v2 | docker-compose.v2.yml | FastAPI+SPA container |
| Manual deploy | deploy.sh | VPS deployment script |
| DB init | init_db.sql | One-time SQL setup |
| DB seed | backend/scripts/seed_admin.py | Admin user creation |

---

## risks

### RISK-1 — CRITICAL: No GitHub Actions CI/CD
**Severity**: High
**Finding**: No .github/workflows/ directory exists. Deployment is via
manual deploy.sh. This means:
- No automated testing before deploy
- No staging gate
- No rollback mechanism
- Every deploy is a manual operation

### RISK-2 — HIGH: Duplicate Test Trees
**Severity**: High
**Finding**: Tests exist in THREE locations:
1. backend/tests/ (17 files — primary)
2. epm-tests/ (15 files — duplicate with partial differences)
3. Root level: test_pdf*.py (8), test_regex*.py (3), scripts/test_apis.py

This creates confusion about which tests are authoritative, risks
divergent test logic, and makes CI configuration impossible without
choosing one tree.

### RISK-3 — HIGH: Root-Level Debris
**Severity**: Medium-High
**Finding**: Project root contains:
- temp_daily.txt, temp_prices1.txt, temp_prices2.txt (temp files)
- tickers.txt, ngx_companies_list.txt (data files)
- test_pdf.py through test_pdf8.py (8 development experiments)
- test_regex.py, test_regex2.py, test_regex3.py
- extract_tickers.py, extract_tickers_from_txt.py (duplicate utils)
- cron.log (log file in repo)
- Dialin-—-Analytics-Dashboard-UI-by-Orix-Creative-on-Dribbble.png (design reference image)
- NigerianStocks/ (Obsidian vault committed to repo — should be gitignored)

### RISK-4 — MEDIUM: Two Docker Compose Files, Two Environments
**Severity**: Medium
**Finding**: docker-compose.yml (Streamlit v1) and docker-compose.v2.yml
(FastAPI+SPA) coexist. The v2 cutover to production has not happened.
This means the "real" production URL (estate.zubbystudio.shop) still
serves the old Streamlit app. Risk of confusion about which is live.

### RISK-5 — MEDIUM: scipy and APScheduler Missing from requirements.txt
**Severity**: Medium
**Finding**: XIRR computation (specced, Gherkin written) requires scipy.
NAV History automation requires APScheduler. Neither is in requirements.txt,
so both features will fail at runtime the moment the code that calls them
is deployed.

### RISK-6 — MEDIUM: Scattered Defunct Scrapers
**Severity**: Low-Medium
**Finding**: Three scrapers exist (ngx_scraper, rapidapi_scraper,
yfinance_scraper) with unclear status. yfinance has no NGX coverage
(confirmed). RapidAPI scraper status unknown. These create confusion
about the data ingestion strategy and may be executed accidentally.

### RISK-7 — LOW: .env Files in Repository
**Severity**: Low (if on VPS only, not pushed to GitHub)
**Finding**: .env, .env.v2, .env.v2.example all present in file tree.
If the actual .env (with real secrets) is committed to git, this is
a security risk.

---

## duplication

| Duplication | Location A | Location B | Impact |
|------------|-----------|-----------|--------|
| Test trees | backend/tests/ | epm-tests/ | High — unclear which is authoritative |
| Import script | backend/scripts/import_obsidian.py | scripts/import_obsidian.py | Medium — two versions |
| Requirements | backend/requirements.txt | ./requirements.txt (root) | Low — different purposes |
| Ticker extraction | extract_tickers.py | extract_tickers_from_txt.py | Low — one-off utilities |
| Docker configs | docker-compose.yml | docker-compose.v2.yml | By design — but v1 should be retired |
| Dockerfiles | Dockerfile | Dockerfile.v2 | By design — v1 should be retired |
| .env files | .env | .env.v2 | Low — different environments |

---

## stability_score

```
Overall:  6 / 10

Backend API:          8/10  — 40 endpoints, 14 models, 5 migrations, well-structured
Frontend:             7/10  — 19 routes, 30+ hooks, shadcn components, some stubs
Testing:              5/10  — 17+ test files but duplicate trees, no CI to run them
CI/CD:                2/10  — no GitHub Actions, manual deploy.sh only
Documentation:        7/10  — 5 ADRs, 14 HOs, BRs, feature files, governance docs
Repository hygiene:   4/10  — debris files, duplicate trees, Obsidian vault committed
Infrastructure:       6/10  — Traefik + Docker working, but v1/v2 split unresolved
Dependencies:         7/10  — pinned versions, bcrypt correct, but scipy/APScheduler missing
```

---

## What Is Complete vs Stub

### Backend — All routers have real implementations
All 40 endpoints have production code. No stubs in backend.

### Frontend — Mixed

| Route | Status |
|-------|--------|
| _app.dashboard.tsx | ✅ Real — KPIs, charts, notifications |
| _app.holdings.tsx | ✅ Real — dual table, inline edit, drawer |
| _app.settings.price-entry.tsx | ✅ Real — PDF upload, CSV, quick entry |
| _app.price-history.tsx | ✅ Real — chart, table, filters |
| _app.registrars.tsx | ✅ Real — full document management |
| _app.dividends.tsx | ⚠️ Unknown — present but status unclear |
| _app.nav-history.tsx | ⚠️ Unknown — hook exists (enabled: false) |
| _app.rebalancing.tsx | ⚠️ Unknown — hook exists |
| _app.transactions.tsx | ⚠️ Unknown |
| _app.companies.tsx | ⚠️ Unknown |
| _app.watchlist.tsx | ⚠️ Unknown |
| _app.settings.corporate-actions.tsx | ⚠️ Unknown — likely StubPage |
| _app.settings.data-import.tsx | ⚠️ Unknown — likely StubPage |
| _app.settings.deleted-records.tsx | ⚠️ Unknown — likely StubPage |
| _app.settings.users.tsx | ⚠️ Unknown — likely StubPage |
