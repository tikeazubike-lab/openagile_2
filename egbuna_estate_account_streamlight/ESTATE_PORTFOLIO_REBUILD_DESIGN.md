# Estate Portfolio — FastAPI + React Rebuild
## Architectural Brainstorm & Design Specification

**From**: Claude (The Brain)
**To**: Antigravity (Implementer) + Zubby (Owner)
**Date**: 2026-04-15
**Protocol**: MASTER_CONTEXT.md v3.0 — Zone 2 Design
**Status**: Brainstorm document. Decisions flagged [LOCKED] are finalised. Items flagged [OPEN] need owner confirmation before implementation.

---

## 0. Decisions Absorbed From Brainstorming Session

| Question | Answer |
|----------|--------|
| Primary device | Both desktop + mobile — responsive design required |
| Frontend feel | Functionality-first, but we'll still make it sharp |
| Users | Admin (you) + read-only viewer (family member) |
| Price data | Manual quick entry + CSV upload; CSV-out Stooq scraper lives separately |
| Scope | Full rebuild + new features (NAV history, watchlist, rebalancing) |
| Backend style | API-only (Claude recommendation: see Section 2) |
| Stooq scraper | Standalone Python script — referenced in README, not in app container |
| Container strategy | Claude recommendation: single container (see Section 3) |

---

## 1. What We're Actually Building

A **personal investment portfolio tracker** for Nigerian Stock Exchange (NGX) holdings.

Core jobs the app does:
1. **Track** — what you own, at what cost, in what quantity
2. **Value** — what it's worth today (manual/CSV price input)
3. **Analyse** — return %, dividend yield, sector allocation, NAV history
4. **Record** — dividends received, corporate actions (bonus issues, rights)
5. **Plan** — target allocation, rebalancing gap, watchlist

Two users: **admin** (full read/write) and **viewer** (read-only, no edit controls).

---

## 2. Backend Architecture Decision: Pure REST API

**Recommendation: FastAPI as a pure REST API. React owns all UI.**

Why this is the cleanest choice for your setup:

- **Separation of concerns**: FastAPI does data + business logic. React does rendering + state. No mixing.
- **Mobile-readiness**: A pure API backend means if you ever want a React Native mobile app, the backend is already there — zero refactor.
- **Testability**: API endpoints are independently testable with curl/Postman without touching the UI.
- **The alternative** (server-side rendering via Jinja2 templates) would give you FastAPI doing double duty as a template engine — that's the Streamlit problem in a different costume.

**Auth strategy**: JWT (JSON Web Tokens), issued by FastAPI on login, stored in the browser as an `httpOnly` cookie (not localStorage — avoids XSS risk). React sends the cookie automatically with every API request.

**Background tasks**: FastAPI has a built-in `BackgroundTasks` system for lightweight async jobs (e.g., triggering a portfolio snapshot after price update). For heavier scheduled work (e.g., nightly NAV snapshot), use a simple APScheduler running inside the FastAPI process — no separate Celery/Redis needed given your low-resource constraints.

---

## 3. Deployment: Single Container (Recommended)

**Recommendation: Single container. FastAPI serves the built React static files.**

Build process:
```
React (npm run build) → /app/static/
FastAPI mounts /app/static/ and serves index.html for all non-API routes
API routes live under /api/v1/...
```

Why single container beats two containers for your use case:
- **Resource**: Two containers = two Python/Node processes + two Nginx configs + more RAM. The VPS has 16GB but the shared Postgres, Frappe, OpenProject, n8n, WikiJS, Gitea, Woodpecker are already on it.
- **Simplicity**: One Dockerfile, one GitHub Actions deploy step, one Traefik rule.
- **Traefik**: Single container means a single router entry — no split routing rules between API and frontend containers.
- **When to split**: If you later add a second frontend app, or want to scale the API independently, split then. Not now.

**Container name**: `estate_portfolio_app` (same as current — Traefik rule unchanged)

---

## 4. Full Technology Stack [LOCKED]

### Backend
```yaml
Framework:     FastAPI (latest stable) + Uvicorn
Python:        3.12-slim (upgrade from 3.11)
ORM:           SQLAlchemy 2.0 (async) + asyncpg driver
Migrations:    Alembic
Auth:          python-jose (JWT) + passlib (bcrypt)
Scheduling:    APScheduler (lightweight, in-process)
File handling: python-multipart (CSV/Excel uploads)
Excel parsing: openpyxl + pandas (for NGX price sheet import)
Validation:    Pydantic v2 (FastAPI's native)
```

### Frontend
```yaml
Framework:     React 18 + Vite (build tool)
Language:      TypeScript (not plain JS — catches bugs at build time, worth it)
State:         TanStack Query (server state) + Zustand (UI state)
Routing:       React Router v6
Tables:        TanStack Table v8 (the best React table library — sorting, filtering, pagination built in)
Charts:        Recharts (lightweight, composable, works well with React)
UI Components: shadcn/ui (unstyled, accessible, you own the code — not a dependency lock-in)
Forms:         React Hook Form + Zod (validation)
Icons:         Lucide React
Styling:       Tailwind CSS v4
```

### Why these specific choices
- **TanStack Query**: Handles API caching, background refetch, loading/error states — removes ~40% of boilerplate you'd otherwise write
- **TanStack Table**: Your tables have sorting, filtering, pagination needs. This is purpose-built for it.
- **shadcn/ui**: Not a component library you install — it's a collection of copy-pasteable components you own. No version lock-in. Works perfectly with Tailwind.
- **Zustand over Redux**: You have minimal global state (auth user, edit mode toggle). Zustand is 10 lines of setup vs Redux's 100.
- **TypeScript**: The API response shapes are complex (holdings with computed fields, price history, etc.). TypeScript lets you define those shapes once and catch mismatches at compile time.

---

## 5. Project Structure

```
estate-portfolio/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── config.py            # Settings from env vars
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── auth/
│   │   │   ├── router.py        # /api/v1/auth/login, /logout, /me
│   │   │   ├── dependencies.py  # get_current_user, require_admin
│   │   │   └── models.py        # User pydantic schemas
│   │   ├── routers/
│   │   │   ├── dashboard.py     # /api/v1/dashboard
│   │   │   ├── companies.py     # /api/v1/companies
│   │   │   ├── holdings.py      # /api/v1/holdings
│   │   │   ├── prices.py        # /api/v1/prices (entry + history)
│   │   │   ├── dividends.py     # /api/v1/dividends
│   │   │   ├── transactions.py  # /api/v1/transactions
│   │   │   ├── registrars.py    # /api/v1/registrars
│   │   │   ├── watchlist.py     # /api/v1/watchlist
│   │   │   └── nav_history.py   # /api/v1/nav-history
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic (not in routers)
│   │   │   ├── portfolio.py     # NAV calc, return %, XIRR
│   │   │   ├── price_import.py  # CSV/Excel parsing + validation
│   │   │   └── scheduler.py     # APScheduler jobs
│   │   └── static/              # Built React files land here
│   ├── alembic/                 # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # TanStack Query hooks per domain
│   │   ├── components/          # Shared UI components
│   │   ├── pages/               # One file per route
│   │   ├── store/               # Zustand stores
│   │   └── types/               # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   └── stooq_scraper/           # See Section 10
├── configs/
│   └── users.json               # Auth credentials (mounted as volume)
├── docker-compose.yml
├── .github/workflows/deploy.yml
└── README.md                    # Includes Stooq reminder (see Section 10)
```

---

## 6. Database: What Changes, What Stays

**The existing `estate_portfolio` database in `openagile_postgres` is preserved entirely.** No destructive migrations. All changes are additive.

### Tables to ADD (new features)

```sql
-- NAV history: daily portfolio value snapshot
CREATE TABLE nav_history (
    id          SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL UNIQUE,
    total_value NUMERIC(15,2) NOT NULL,
    total_cost  NUMERIC(15,2) NOT NULL,
    gain_loss   NUMERIC(15,2) GENERATED ALWAYS AS (total_value - total_cost) STORED,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist: companies you're researching but haven't bought
CREATE TABLE watchlist (
    id          SERIAL PRIMARY KEY,
    company_id  INTEGER REFERENCES companies(id),
    target_price NUMERIC(10,2),
    notes       TEXT,
    added_at    TIMESTAMPTZ DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ  -- soft delete
);

-- Users table: replaces YAML file auth
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    name        VARCHAR(100),
    password_hash TEXT NOT NULL,
    role        VARCHAR(20) DEFAULT 'readonly',  -- 'admin' or 'readonly'
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    last_login  TIMESTAMPTZ
);

-- Price audit log: every price change recorded
CREATE TABLE price_audit (
    id          SERIAL PRIMARY KEY,
    company_id  INTEGER REFERENCES companies(id),
    old_price   NUMERIC(10,4),
    new_price   NUMERIC(10,4) NOT NULL,
    changed_at  TIMESTAMPTZ DEFAULT NOW(),
    changed_by  INTEGER REFERENCES users(id),
    source      VARCHAR(50)  -- 'manual', 'csv_upload', 'stooq_csv'
);

-- Sector targets: for rebalancing tool
CREATE TABLE sector_targets (
    id          SERIAL PRIMARY KEY,
    sector_name VARCHAR(100) UNIQUE NOT NULL,
    target_pct  NUMERIC(5,2) NOT NULL,  -- e.g. 25.00 = 25%
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Corporate actions: bonus issues, rights issues
CREATE TABLE corporate_actions (
    id              SERIAL PRIMARY KEY,
    company_id      INTEGER REFERENCES companies(id),
    action_type     VARCHAR(50) NOT NULL,  -- 'bonus', 'rights', 'split', 'merger'
    action_date     DATE NOT NULL,
    ratio_numerator   INTEGER,  -- e.g. 1 (bonus: 1 new share for every...)
    ratio_denominator INTEGER,  -- e.g. 5 (... 5 held)
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Tables to MODIFY (additive only)

```sql
-- Holdings: add draft status + delete support
ALTER TABLE holdings ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'live';
-- status values: 'draft' | 'live'
-- existing rows backfilled to 'live' automatically via DEFAULT

-- Holdings: unique constraint (after dedup)
-- [VERIFY THIS] Run dedup check first:
-- SELECT company_id, COUNT(*) FROM holdings WHERE deleted_at IS NULL 
-- GROUP BY company_id HAVING COUNT(*) > 1;
ALTER TABLE holdings ADD CONSTRAINT holdings_company_id_unique UNIQUE (company_id);

-- Dividends: add source tracking + DRIP support
ALTER TABLE dividends ADD COLUMN IF NOT EXISTS source VARCHAR(50) DEFAULT 'manual';
ALTER TABLE dividends ADD COLUMN IF NOT EXISTS is_scrip BOOLEAN DEFAULT FALSE;
-- is_scrip = TRUE means dividend was paid as shares (DRIP), not cash
ALTER TABLE dividends ADD COLUMN IF NOT EXISTS scrip_shares INTEGER;
-- scrip_shares = number of shares received instead of cash
```

---

## 7. API Design: All Endpoints

### Auth
```
POST   /api/v1/auth/login          → {access_token, user: {id, name, role}}
POST   /api/v1/auth/logout         → clears httpOnly cookie
GET    /api/v1/auth/me             → current user info
PUT    /api/v1/auth/change-password → admin only
```

### Dashboard
```
GET    /api/v1/dashboard           → all KPIs in one call (portfolio value, cost, gain/loss, 
                                     top holdings, sector donut, recent transactions)
```

### Companies
```
GET    /api/v1/companies           → list (with current_price, sector, registrar_name)
POST   /api/v1/companies           → create (admin)
PUT    /api/v1/companies/{id}      → edit (admin)
DELETE /api/v1/companies/{id}      → soft delete (admin)
```

### Holdings
```
GET    /api/v1/holdings            → list with computed fields:
                                     current_value, cost_basis, return_pct, 
                                     dividend_yield, status
POST   /api/v1/holdings            → add new (admin) — defaults to draft
PUT    /api/v1/holdings/{id}       → edit (admin)
PUT    /api/v1/holdings/{id}/publish → flip draft → live (admin)
DELETE /api/v1/holdings/{id}       → soft delete (admin)
GET    /api/v1/holdings/deleted    → list soft-deleted (admin, for restore)
PUT    /api/v1/holdings/{id}/restore → restore soft-deleted (admin)
```

### Prices
```
GET    /api/v1/prices              → current prices for all companies
POST   /api/v1/prices/quick        → single stock quick price entry (admin)
POST   /api/v1/prices/bulk-csv     → multipart upload → validate → preview → commit (admin)
GET    /api/v1/prices/history/{company_id} → price history for one company
GET    /api/v1/prices/audit        → recent 50 price changes (admin)
POST   /api/v1/prices/audit/{id}/revert → revert a specific price change (admin)
```

### Dividends
```
GET    /api/v1/dividends           → list (filter by year, company)
POST   /api/v1/dividends           → add single entry (admin)
POST   /api/v1/dividends/bulk-csv  → CSV upload (admin)
PUT    /api/v1/dividends/{id}      → edit (admin)
DELETE /api/v1/dividends/{id}      → soft delete (admin)
GET    /api/v1/dividends/summary   → annual totals + WHT summary (for tax view)
```

### Transactions
```
GET    /api/v1/transactions        → list (filter by company, type, date range)
POST   /api/v1/transactions        → add (admin)
PUT    /api/v1/transactions/{id}   → edit (admin)
DELETE /api/v1/transactions/{id}   → soft delete (admin)
```

### Registrars
```
GET    /api/v1/registrars          → list with linked companies
POST   /api/v1/registrars          → create (admin)
PUT    /api/v1/registrars/{id}     → edit (admin)
DELETE /api/v1/registrars/{id}     → soft delete (admin)
```

### NAV History
```
GET    /api/v1/nav-history         → list of daily snapshots (for chart)
POST   /api/v1/nav-history/snapshot → manually trigger snapshot (admin)
                                      (also called automatically by scheduler)
```

### Watchlist
```
GET    /api/v1/watchlist           → list
POST   /api/v1/watchlist           → add company (admin)
PUT    /api/v1/watchlist/{id}      → update target price/notes (admin)
DELETE /api/v1/watchlist/{id}      → remove (admin)
```

### Corporate Actions
```
GET    /api/v1/corporate-actions   → list (filter by company)
POST   /api/v1/corporate-actions   → add (admin)
PUT    /api/v1/corporate-actions/{id} → edit (admin)
```

### Rebalancing
```
GET    /api/v1/rebalancing         → current allocation vs targets, gap per sector
GET    /api/v1/sector-targets      → target % per sector
PUT    /api/v1/sector-targets      → update targets (admin)
```

---

## 8. Frontend Pages & Navigation

```
Sidebar Navigation:
├── 📊 Dashboard
├── 💼 Holdings
├── 🏢 Companies
├── 💰 Dividends
├── 📈 Price History
├── 🔄 Transactions
├── 📋 Registrars
├── 👁 Watchlist           [NEW]
├── 📉 NAV History          [NEW]
├── ⚖️ Rebalancing          [NEW]
└── ⚙️ Settings
    ├── Price Entry         [PROMINENT — this is used daily]
    ├── Data Import (CSV)
    ├── Corporate Actions
    ├── User Management     [admin only]
    └── Deleted Records     [admin only]
```

**Edit Mode**: A toggle in the top navbar (not sidebar), visible only to `admin` role.
```
[ 👁 Viewing ] ←→ [ ✏️ Editing ]
```
In Viewing mode: all tables are read-only, no action buttons.
In Editing mode: inline edit, add row, soft-delete buttons appear across all pages.

**Draft Holdings**: In Editing mode, draft holdings show as a distinct visual row (muted/italic style, with a "Publish" button). In Viewing mode, draft holdings are hidden entirely.

---

## 9. UI Design Direction

You said functionality-first, but since we're doing a full rebuild, let's make it look the part. My recommendation:

**Dark financial dashboard aesthetic** — think Bloomberg Terminal meets modern fintech. Not flashy, but sharp.

- **Color palette**: Near-black background (`#0d1117`), white primary text, emerald green (`#10b981`) for gains, red (`#ef4444`) for losses, amber (`#f59e0b`) for warnings/draft status
- **Typography**: `DM Mono` for numbers/tickers (monospaced, financial feel) + `Geist` for UI text (clean, modern)
- **Tables**: Zebra stripe with hover highlight, sticky headers, sortable columns — TanStack Table handles this
- **Charts**: Recharts with custom dark theme — portfolio value line chart, sector allocation donut, NAV history area chart
- **Responsive**: Sidebar collapses to bottom nav on mobile; tables get horizontal scroll with sticky first column (ticker/company name)

**The one memorable thing**: Numbers animate on load — portfolio value counts up from 0 to actual value on Dashboard. Subtle, not gimmicky, but makes the data feel alive.

---

## 10. Stooq Scraper — Standalone Script

**Location**: `scripts/stooq_scraper/` in the same repo (isolated folder, NOT part of the Docker build)

**What it does**:
1. Takes a list of NGX tickers
2. Fetches EOD price from Stooq: `https://stooq.com/q/d/l/?s={ticker}.xnsa&i=d`
3. Outputs a CSV with columns: `ticker, price, date`
4. That CSV is what you upload to the app's Bulk CSV Import

**The script is run manually on your local Fedora machine** — `python3 scripts/stooq_scraper/scrape.py` — when you want to do a bulk price update.

**README reminder** (to be placed prominently in `README.md`):

```markdown
## 💡 Price Data Sources

The app supports manual price entry and CSV upload.

**Quick daily updates**: Use Settings → Price Entry in the app.

**Bulk weekly updates**: 
1. Download the NGX Group daily price sheet from https://ngxgroup.com/exchange/trade/equities/
   OR run the Stooq scraper (see below) to generate a CSV automatically.
2. Upload via Settings → Data Import → Bulk CSV.

**Stooq Scraper** (standalone — not part of the app):
Located in `scripts/stooq_scraper/`. Run on your local machine:
```bash
cd scripts/stooq_scraper
python3 scrape.py --tickers tickers.txt --output prices.csv
```
Then upload `prices.csv` in the app. See `scripts/stooq_scraper/README.md` for setup.

> ⚠️ Stooq coverage of NGX tickers (XNSA exchange) is not guaranteed for all stocks.
> If a ticker returns no data, fall back to manual entry or the NGX price sheet.
```

---

## 11. Authentication: Users in Database (Not YAML)

For the rebuild, store users in the `users` DB table (defined in Section 6) instead of a YAML file. Why:
- No file to manage or mount as a volume
- Password changes via the Settings UI (admin can reset any user's password)
- Extensible: last login tracking, active/inactive flag, future audit log by user

**Login flow**:
1. POST `/api/v1/auth/login` with `{username, password}`
2. FastAPI verifies bcrypt hash
3. Issues JWT, sets it as an `httpOnly` `SameSite=Strict` cookie (30-day expiry)
4. React Router redirects to Dashboard
5. All subsequent API calls send cookie automatically

**Initial setup**: Alembic migration creates `users` table + seeds one admin user from env vars:
```
ADMIN_USERNAME=zubbyik
ADMIN_PASSWORD=<set in .env>
```

---

## 12. CSV Import: Column Mapping Design

The NGX price sheet doesn't have standardised column names. The import flow handles this:

```
Step 1: Upload file (CSV or Excel)
        → App reads headers, shows them to user

Step 2: Column mapping UI
        ┌─────────────────────────────────────┐
        │ Your file has these columns:        │
        │                                     │
        │ "Symbol"    → maps to: [Ticker  ▼]  │
        │ "Close"     → maps to: [Price   ▼]  │
        │ "Date"      → maps to: [Date    ▼]  │
        │ "Volume"    → maps to: [Skip    ▼]  │
        └─────────────────────────────────────┘

Step 3: Preview (first 10 rows)
        → Validation errors highlighted in red
        → Unknown tickers flagged with company name suggestion

Step 4: Commit (only valid rows)
        → Summary: "47 prices updated, 3 rows skipped (unknown ticker)"
```

**Validation rules**:
- Price: numeric, > 0, < ₦100,000 (sanity cap — flag anything above for confirmation)
- Date: valid date, not future, warn if > 30 days old
- Ticker: must exist in `companies` table — list unmatched tickers explicitly

---

## 13. Business Logic: Key Computations

These live in `backend/app/services/portfolio.py`, not in SQL and not in the frontend.

### Holdings computed fields (per holding)
```python
current_value   = shares * current_price
cost_basis      = shares * average_purchase_price
return_pct      = ((current_value - cost_basis) / cost_basis) * 100
dividend_yield  = (annual_dividend_per_share / current_price) * 100
```

### Dashboard KPIs
```python
total_portfolio_value = sum(current_value for all live holdings)
total_invested        = sum(cost_basis for all live holdings)
unrealised_gain_loss  = total_portfolio_value - total_invested
unrealised_gain_pct   = (unrealised_gain_loss / total_invested) * 100
```

### XIRR (annualised return) — P2, not P0
```python
# Uses scipy.optimize for IRR calculation across multiple transaction dates
# Only computed on-demand per holding (expensive), not on every dashboard load
```

### NAV Snapshot (scheduled daily)
```python
# APScheduler fires at 18:00 WAT (15:00 UTC) on weekdays
# Computes total_value + total_cost at that moment
# Inserts into nav_history table
# User can also trigger manually from Settings
```

### Rebalancing gap
```python
current_sector_pct = sector_value / total_portfolio_value * 100
gap = current_sector_pct - target_pct
# Positive gap = overweight, Negative = underweight
```

---

## 14. GitHub Actions: Deploy Pipeline

Same pattern as existing MASTER_CONTEXT convention, adapted for the rebuild:

```yaml
# .github/workflows/deploy.yml
name: Deploy Estate Portfolio

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build React frontend
        working-directory: frontend
        run: |
          npm ci
          npm run build
          # Output lands in frontend/dist/

      - name: Copy React build into backend static dir
        run: cp -r frontend/dist/* backend/app/static/

      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /root/openagile/estate-portfolio
            git pull origin main
            docker compose build
            docker compose up -d
            docker compose ps
```

Note: React is built in GitHub Actions (not on the VPS) — the VPS only runs the Docker container. This keeps the VPS lean.

---

## 15. Open Questions [OPEN — Need Your Input]

These need decisions before Antigravity can start:

1. **WHT rate**: Dividends WHT is currently hardcoded at 10%. Should the rebuild make this configurable per company or per dividend entry? (Some NGX companies may have different treaty rates)

2. **Transaction types**: What transaction types exist in your data? Assumed: `buy`, `sell`. Any others? (`bonus_receipt`, `rights_subscription`, `transfer_in`?)

3. **Holdings uniqueness**: The proposed UNIQUE constraint assumes one open position per company. Is that always true, or do you ever hold the same stock in two accounts/portfolios?

4. **Viewer access scope**: The read-only viewer — do they see everything (all pages, all data) or only a summary view (Dashboard + Holdings)?

5. **NAV snapshot timing**: 18:00 WAT daily on weekdays — does this timing work, or should it be user-configurable?

6. **Beta subdomain**: Grok mentioned `demo.estate.zubbystudio.shop` for the new app while old runs on `estate.zubbystudio.shop`. Do you want this parallel-running period, or do you want to cut over directly (rename, old app down)?

---

## 16. Implementation Order for Antigravity

Once this document is confirmed, implementation should go in this order:

### Phase 2A — Foundation (1 week)
1. Repo restructure (`backend/`, `frontend/`, `scripts/`)
2. FastAPI skeleton + DB connection (async SQLAlchemy)
3. Alembic migrations (existing tables + new tables from Section 6)
4. Auth system: users table, JWT login/logout, role middleware
5. React skeleton: Vite + TypeScript + Tailwind + routing + auth context
6. GitHub Actions pipeline (build React → bake into container → deploy)
7. Traefik config: new container on `demo.estate.zubbystudio.shop`

### Phase 2B — Core Data Pages (1 week)
8. Dashboard API endpoint + React page (KPIs, sector donut, top holdings)
9. Holdings page (list + draft/live + edit mode)
10. Price Entry (quick single + bulk CSV with column mapping)
11. Companies page (CRUD)
12. Price History page

### Phase 2C — Remaining Pages (1 week)
13. Dividends (CRUD + CSV import + annual summary)
14. Transactions page
15. Registrars page (CRUD + company links)
16. Watchlist page

### Phase 2D — New Features (1 week)
17. NAV History chart + APScheduler snapshot job
18. Rebalancing tool (sector targets + gap analysis)
19. Corporate Actions page
20. Soft-delete restore UI (Settings → Deleted Records)
21. Stooq scraper standalone script

### Phase 2E — Polish + Cutover
22. Mobile responsive pass (sidebar → bottom nav on mobile, table scroll)
23. Dashboard number animation (count-up on load)
24. README with Stooq reminder + full setup docs
25. Cut over: `estate.zubbystudio.shop` → new app, old Streamlit container down

---

## 17. Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Backend | FastAPI pure REST API | Clean separation, mobile-ready, testable |
| Frontend | React 18 + TypeScript + Vite | Type safety, fast builds, modern tooling |
| State | TanStack Query + Zustand | Query for server state, Zustand for UI state |
| Tables | TanStack Table | Purpose-built, sorting/filtering/pagination included |
| Container | Single (FastAPI serves React static) | Lower resource use, simpler Traefik config |
| Auth | JWT in httpOnly cookie + DB users table | Secure, no YAML file maintenance, UI-managed |
| Edit mode | Top navbar toggle (admin only) | Not sidebar — keeps nav uncluttered |
| Draft status | Holdings table only | Most needed; full draft-on-all-tables is overkill |
| Price input | Quick entry + CSV with column mapper | NGX sheet format varies; generic mapper is resilient |
| Stooq | Standalone script in `scripts/` folder | Not in container; README reminder keeps it findable |
| NAV snapshots | APScheduler in-process | No Redis/Celery needed; low resource cost |

---

**END OF BRAINSTORM / DESIGN SPECIFICATION**

**Status**: Ready for your review of Section 15 (Open Questions) before handing to Antigravity.
**Next step**: Confirm/correct open questions → Claude produces final handover brief to Antigravity → Implementation begins.
