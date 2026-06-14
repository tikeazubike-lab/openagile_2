# Claude Handover Brief — Estate Portfolio Manager
**From**: Antigravity (Investigator + Implementer)  
**To**: Claude (Architectural Review + Feature Design)  
**Date**: 2026-04-11  
**Protocol**: MASTER_CONTEXT.md v3.0 — Handover Protocol  
**Framework**: Zone 2 task — architectural decisions + feature design needed before Antigravity implements

---

## 0. Your Role in This Handover

You are being asked to do **two things**:

**A. Architectural Review** — Critique the decisions made this session. Ask the hard "why" questions. Flag tradeoffs. Identify anything that will cause problems at scale or during future maintenance.

**B. Feature Design** — Design the implementation approach for the next feature tier (P2 items listed in Section 6). The designs will be handed back to Antigravity for implementation.

Do NOT implement code. Your output should be design documents, critique notes, and clarifying questions for the user.

---

## 1. Infrastructure Contract (Mandatory Context)

```yaml
Server:
  OS: Ubuntu 24.04 LTS
  IP: 185.216.177.250
  User: zubbyik
  Location: Netcup VPS
  CPU: 8 vCPU | RAM: 16GB | Disk: 500GB SSD
  
Local Dev Machine:
  OS: Fedora Linux 42 (Workstation Edition)
  RULE: NEVER run Docker commands locally — GitHub Actions only

Deployment Pipeline:
  Method: GitHub Actions → SSH → server
  Repo: github.com/zubbyik/zubbyik-openagile_frappe_update
  Trigger: push to main branch
  Workflow: .github/workflows/deploy.yml
  Server path: /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio

Reverse Proxy: Traefik v2.10
  - All HTTP/HTTPS routed through Traefik
  - SSL: Cloudflare certresolver
  - Network: openagile_openagile_network (for Traefik routing)

Shared PostgreSQL:
  Container: openagile_postgres
  Network: openagile_network
  User: openagile (superuser, shared across all services)
  Databases: n8n, wikijs, openproject, gitea, estate_portfolio (just added)

Application:
  Name: estate-portfolio
  URL: https://estate.zubbystudio.shop
  Container: estate_portfolio_app
  Stack: Streamlit (Python 3.11) + PostgreSQL 15
  Port: 8501 (internal)
  Networks: openagile_network + openagile_openagile_network (dual-network)
```

### Network Architecture (Critical to Understand)
```
openagile_network          → root infrastructure (Traefik, postgres, grafana, n8n...)
openagile_openagile_network → Frappe stack + Traefik routing layer

estate_portfolio_app joins BOTH:
  - openagile_network           (to reach openagile_postgres by container name)
  - openagile_openagile_network (Traefik uses this network for routing)
```

---

## 2. What Antigravity Did This Session

### Session Goal
Forensic analysis of the estate portfolio codebase (using INVESTIGATOR_AGENT.md protocol), followed by P1 bug fixes and migration to shared Postgres.

### Changes Made (All in git, NOT yet pushed to server)

#### 2a. P1 Bug Fixes — `app.py`

| Bug | Fix Applied |
|-----|-------------|
| Stale DB connection (`@st.cache_resource` with no TTL) | Changed to `@st.cache_resource(ttl=600)` — reconnects every 10 min. Added `psycopg2.OperationalError` catch with `st.cache_resource.clear()` + retry in both `query_db()` and `execute_db()` |
| Password debug print leaking 2 chars to stdout | Removed entirely |
| `INTERVAL '%s days'` SQL param bug (Price History page broke) | Changed to `(%s * INTERVAL '1 day')` — correct psycopg2 parameterization |
| Obsidian import UI was a stub (printed success without importing) | Now calls `subprocess.run(["python3", "scripts/import_obsidian.py", "/app/NigerianStocks"])`. Also added file-upload path using `tempfile.TemporaryDirectory` |
| Scraper activity log showed 0 rows (source filter was `ngx_scraper` only) | Changed to `GROUP BY DATE(created_at), source` — now shows all sources including `eodhd` |

#### 2b. Shared Postgres Migration

**`docker-compose.yml`** (estate-portfolio):
- Removed dedicated `postgres` service + `postgres_data` volume
- Added `openagile_network: external: true` 
- `streamlit` service now joins both networks
- Removed `depends_on: postgres` (service gone)

**Root `openagile/docker-compose.yml`**:
- Added `estate_portfolio` to `POSTGRES_MULTIPLE_DATABASES`

**`init_db.sql`**:
- All 8 `CREATE TABLE` → `CREATE TABLE IF NOT EXISTS` (idempotent)

**`.env.example`**:
- Updated: `DB_HOST=openagile_postgres`, `DB_USER=openagile`

**`.github/workflows/deploy.yml`**:
- Added `Bootstrap Database Schema` step: runs `init_db.sql` against `openagile_postgres` via `docker exec -i`

---

## 3. CRITICAL PRE-DEPLOYMENT BLOCKER ⛔

> [!CAUTION]
> **DO NOT push to main yet.** The code changes are committed locally but the server is not ready. Pushing now will destroy the running application.

### Why It Will Break
The updated `docker-compose.yml` removes the local `postgres` container. The server's live `.env` still points to:
```
DB_HOST=postgres        ← old local container (which will no longer exist)
DB_USER=portfolio_user  ← user that only exists in old local postgres
```

After push, the app container will start but all DB queries will fail with connection refused.

### Required Migration Sequence (In This Exact Order)

**Step 1: Export data from old local postgres (on server)**
```bash
# On server — run BEFORE any push
docker exec estate_portfolio_db \
  pg_dump -U portfolio_user estate_portfolio \
  > /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backups/pre_migration_$(date +%Y%m%d).sql
```

**Step 2: Create the estate_portfolio database in shared postgres**

The `POSTGRES_MULTIPLE_DATABASES` env var only runs on first init (via the init script). Since shared postgres already exists and is running, create the DB manually:
```bash
docker exec openagile_postgres \
  psql -U openagile -c "CREATE DATABASE estate_portfolio;"
```

**Step 3: Apply schema to shared postgres**
```bash
docker exec -i openagile_postgres \
  psql -U openagile -d estate_portfolio \
  < /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/init_db.sql
```

**Step 4: Import data dump into shared postgres**
```bash
docker exec -i openagile_postgres \
  psql -U openagile -d estate_portfolio \
  < /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/backups/pre_migration_*.sql
```

**Step 5: Update server `.env`**
```bash
# Edit /home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio/.env
# Change:
DB_HOST=openagile_postgres
DB_USER=openagile
DB_PASSWORD=<the POSTGRES_PASSWORD value from openagile root .env>
# Keep: DB_NAME=estate_portfolio, EODHD_API_KEY=<key>
# Remove: RAPIDAPI_KEY (no longer used)
```

**Step 6: Now push to GitHub → Actions deploys**

> [!WARNING]
> **Credential rotation needed**: The actual DB password, RAPIDAPI_KEY, and EODHD_API_KEY values were shared in a chat session and should be treated as potentially exposed. Rotate: EODHD API key (eodhd.com dashboard), generate new DB password, remove RAPIDAPI_KEY from .env.

---

## 4. Decision Log (What Was Tried, Why, Alternatives Rejected)

### Decision: Shared Postgres over isolated per-app postgres

**MASTER_CONTEXT rule says**: "Never create a new Postgres container — one exists, reuse it."  
**Historical context**: The estate portfolio was built *before* this rule was written (Dec 2025), with its own postgres. This session brings it into compliance.

**Why kept separate originally**: Isolation — different user (`portfolio_user`), different port, different volume. Clean boundary.  
**Why merging now**: Resource efficiency on 16GB server, simpler backup strategy, one database to monitor.

**Tradeoff accepted**: The `openagile` superuser now has access to estate_portfolio data, alongside n8n, wikijs, etc. No row-level security. Acceptable for single-tenant personal use.

**Alternative rejected**: Keep isolated postgres but add it to `openagile_network`. This was simpler but still violated the "reuse" principle. The extra container wastes ~200MB RAM.

### Decision: `@st.cache_resource(ttl=600)` over connection pooling

**Why TTL over pooling**: `psycopg2.pool.ThreadedConnectionPool` requires significant refactor — every `query_db()` call would need pool acquire/release logic. TTL-based cache is a minimal fix.

**Limitation**: Still not true connection pooling. Under concurrent user load (multiple browser tabs), psycopg2 in a Streamlit app will share one connection. For personal use with ~1 user this is fine.

**Future path**: If this becomes multi-user, replace with `SQLAlchemy` + `psycopg2` pool or `asyncpg`.

### Decision: Subprocess for Obsidian import (not in-process call)

**Why subprocess**: `import_obsidian.py` uses its own DB connection setup and `sys.exit()`. Calling it in-process would clash with Streamlit's cached connection and could exit the Streamlit server.

**Limitation**: Subprocess cannot stream progress to the UI. User sees spinner until completion. For large vaults (>500 files) this could time out at 120s.

**Alternative considered**: Refactor import_obsidian.py into a library function. Rejected as out-of-scope for P1 fixes.

---

## 5. Current State: What Works, What Doesn't

```yaml
Working:
  - EODHD scraper (eodhd_scraper.py) → .XNSA ticker format → price updates ✅
  - UI price update button (Settings → Price Scraper → Run EODHD Scraper) ✅
  - Dashboard with sector pie + top 10 holdings bar chart ✅
  - All 10 pages render (Companies, Holdings, Transactions, etc.) ✅
  - GitHub Actions CI/CD pipeline (deploys on push to main) ✅
  - Traefik routing via cloudflare certresolver ✅

Fixed This Session (pending deployment):
  - DB connection resilience (TTL + reconnect) ✅
  - INTERVAL SQL param bug on Price History page ✅
  - Obsidian import UI now actually imports ✅
  - Scraper activity log now shows eodhd records ✅
  - Password debug print removed ✅

Broken / Not Yet Done:
  - Shared postgres migration (BLOCKER — see Section 3)
  - No edit/delete for holdings, companies, dividends (P2)
  - Duplicate holdings on re-import (no UNIQUE constraint on holdings.company_id) (P2)
  - No scheduled price updates (manual only) (P2)
  - No portfolio NAV history chart (P3)
  - No dividend yield calculation (P3)
  - NGX scraper + RapidAPI buttons still visible in UI but non-functional (tech debt)

Known Legacy Issues (Pre-existing, Not Fixed):
  - import_obsidian.py does not use ON CONFLICT DO UPDATE for holdings → double-imports accumulate
  - holdings table has no UNIQUE constraint → multiple rows per company
  - company ticker max_chars=10 in UI form, but DB supports VARCHAR(20)
```

---

## 6. Feature Design Brief for Claude (P2 Backlog)

These are the features Claude should design. Antigravity will implement once designs are approved.

### Feature 1: EODHD Free-Tier Rotation Scheduler

**Context**: EODHD free tier = 20 API calls/day. Portfolio has ~72 active companies. With 20 calls/day, you can update the full portfolio every ~4 days (rotating batches).

**User preference**: Use rotation scheduler pattern (not upgrade to paid tier yet).

**Design questions for Claude**:
1. Where should the scheduler live? Options:
   - APScheduler inside the Streamlit process (simple, but dies when app is idle)
   - Separate `scheduler` Docker sidecar container (robust, always runs)
   - GitHub Actions scheduled workflow (`schedule: cron:`) calling `docker compose exec`
   - Python `schedule` library with a long-running background thread
2. How to track "which batch ran last"? Options: DB table `scraper_state`, flat file, or use `price_history` timestamps to infer the least-recently-updated stocks
3. How should the rotation work — fixed day-of-week batches OR dynamic "update the 20 stalest stocks"?
4. What happens on weekends / market holidays when NGX doesn't trade? EODHD returns stale data — the scraper should detect this and not count it as a quota call.

**Constraints**:
- Server is always on (Netcup VPS, 24/7)
- No GPU, ~4GB available RAM per service
- Python 3.11-slim base image (no system-level cron unless via sidecar)
- MUST respect 20 calls/day limit — never exceed (no retry storms)

**[INFERRED]**: The scraper already has `time.sleep(1)` between calls and detects `429 RATE_LIMIT`. The rotation scheduler should use this as a safety net but primary throttle via batch sizing.

### Feature 2: Edit/Delete UI for Holdings, Companies, Dividends

**Context**: The DB schema has `deleted_at TIMESTAMP NULL` columns on all main tables (soft-delete pattern). Nothing surfaces them in the UI. Users currently cannot fix data entry mistakes without direct DB access.

**Design questions for Claude**:
1. Where should edit/delete live in the UI? Options:
   - Inline editing in the dataframe (Streamlit `st.data_editor`)
   - Separate "Edit" view per page with a record selector
   - Action buttons on each row (custom HTML)
2. Soft delete (set `deleted_at`) vs hard delete? The schema enforces soft-delete; should UI respect this or surface a "hard delete" option for superusers?
3. The `holdings` double-import bug (no UNIQUE constraint) — should edit/delete be designed to handle existing duplicate rows, or should the schema be fixed first (add UNIQUE constraint, deduplicate)?

**Constraints**:
- Streamlit's `st.data_editor` supports inline editing but has limitations with complex types
- The `deleted_at` soft-delete is the correct pattern — do not hard delete

### Feature 3: Portfolio NAV History Chart (P3 — Preview Only)

**Context**: Dashboard shows current snapshot value. No chart of "portfolio value over time." The `price_history` table has per-stock daily prices, but no materialized portfolio-level aggregate.

**Design questions for Claude**:
1. Should NAV snapshots be computed on-demand (SQL joining price_history × holdings) or pre-materialized in a `portfolio_snapshots(date, total_value)` table?
2. On-demand join: `SUM(h.num_shares * ph.close_price)` for each day in price history — is this performant enough for ~72 stocks × 365 days?
3. Who writes to `portfolio_snapshots`? The scheduler? A trigger? The scraper?

### Feature 4: Multi-Lot Holdings (P2 — Schema Change Required)

**Context**: Current schema: one holdings row per company. Real portfolio: bought GTCO in 2018, 2020, and 2023 at different prices. True cost basis requires per-lot tracking.

**Design questions for Claude**:
1. Schema options:
   - Add `purchase_date`, `lot_label` columns to existing `holdings` table
   - Create new `holding_lots` table, keep `holdings` as aggregate view
2. The migration from current single-row-per-company to multi-lot. What's the right strategy — assume current row = "lot 1" or mark as "blended"?
3. How does this affect the dashboard calculations? `average_cost_basis` is currently a single value. Multi-lot means FIFO/LIFO/AVCO choice.

---

## 7. Implicit Rules (Do Not Violate)

```
1. DB_HOST in .env MUST resolve to a running container name on the network the app is attached to.
   After migration: DB_HOST=openagile_postgres (on openagile_network)
   
2. EODHD_API_KEY must be in .env — scraper does sys.exit(1) if missing.

3. openagile_openagile_network must exist (created by frappe_docker stack) before
   estate-portfolio compose up — declared external: true.

4. openagile_network must exist (created by root openagile stack) — also external: true now.

5. Both parent stacks must be running before estate-portfolio can start.
   Dependency order: root stack → frappe_docker → estate-portfolio

6. init_db.sql UNIQUE constraint: price_history(company_id, price_date) — scraper uses
   ON CONFLICT DO UPDATE. Do not remove this constraint.

7. Traefik routing expects estate-portfolio container on openagile_openagile_network.
   traefik.docker.network label MUST match.

8. holdings table currently assumes one row per company_id. Any query using
   SUM(h.num_shares) without GROUP BY will double-count if duplicates exist.
   Fix required before multi-lot feature: add UNIQUE constraint + deduplicate.

9. GitHub Actions is the ONLY deployment mechanism. No manual docker commands on server
   for code changes. .env changes on server are the ONE exception (manual edit via SSH).
```

---

## 8. Files Changed This Session

```
egbuna_estate_account_streamlight/estate-portfolio/
├── app.py                          ← P1 bug fixes (DB connection, INTERVAL SQL, imports, log)
├── docker-compose.yml             ← Removed local postgres, dual-network, no depends_on
├── init_db.sql                    ← All CREATE TABLE → CREATE TABLE IF NOT EXISTS
├── .env.example                   ← Updated: DB_HOST=openagile_postgres, DB_USER=openagile
└── .github/workflows/deploy.yml  ← Added Bootstrap Database Schema step

openagile/ (root stack)
└── docker-compose.yml             ← Added estate_portfolio to POSTGRES_MULTIPLE_DATABASES
```

---

## 9. Verification Steps (Post-Migration)

```markdown
1. Test Command (after migration + push):
   docker compose exec -T streamlit python -c "import psycopg2; c = psycopg2.connect(host='openagile_postgres', dbname='estate_portfolio', user='openagile', password='<pw>'); print('✅ Connected'); c.close()"

2. Expected Output: ✅ Connected

3. If It Fails:
   a. Check container is on both networks: docker inspect estate_portfolio_app | grep -A20 Networks
   b. Check openagile_postgres is running: docker ps | grep openagile_postgres
   c. Check DB exists: docker exec openagile_postgres psql -U openagile -l | grep estate
   d. Check .env values: docker compose exec streamlit env | grep DB

4. Rollback:
   Re-add the local postgres service to docker-compose.yml and revert .env to old values.
   Old postgres data is preserved in the backup SQL dump from Step 1.
```

---

## 10. Open Questions for Claude to Resolve

Before Antigravity implements P2 features, Claude should provide answers to:

1. **Rotation scheduler architecture** — APScheduler in-process vs GitHub Actions cron vs sidecar container? Give tradeoffs with this specific server profile (always-on VPS, Streamlit app, 20 calls/day limit).

2. **Edit/Delete UI pattern** — `st.data_editor` inline vs separate edit forms? Consider that Streamlit reruns the whole script on every widget interaction.

3. **Holdings schema migration** — multi-lot vs single-lot. Is P2 (edit/delete) even feasible without fixing the UNIQUE constraint first? What's the correct migration sequence?

4. **Portfolio NAV chart** — on-demand SQL join vs pre-materialized snapshot table. Recommend based on 72 stocks × 365 days query cost.

5. **Security** — the user shared credentials in a chat session (DB password, EODHD API key, RapidAPI key). Recommend rotation priority and whether the RAPIDAPI_KEY should be removed from .env entirely since that scraper no longer works for NGX.

---

## 11. Linked Artifacts (For Full Context)

- **Investigation Report** (Antigravity): Full forensic analysis, all 15 roadmap items  
  → `brain/51270429-3520-4350-8167-3c45d81da215/estate_portfolio_investigation.md`

- **CI/CD Setup Walkthrough** (Previous session):  
  → `brain/4556288f-dab8-4c30-9fb2-3d2a42dc25e1/walkthrough.md`

- **NGX Price API Research Walkthrough** (Previous session):  
  → `brain/a72446b8-c42b-4be4-9412-38370b6f71e4/walkthrough.md`

---

**END OF HANDOVER BRIEF**  
**Next Agent**: Claude (OpenAgile Master Project)  
**Expected Output**: Architectural critique + feature design documents for items in Section 6  
**After Claude Review**: Return to Antigravity for implementation
