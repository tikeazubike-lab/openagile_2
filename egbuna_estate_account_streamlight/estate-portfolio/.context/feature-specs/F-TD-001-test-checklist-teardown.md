---
id: F-TD-001
title: Pre-Merge Test Checklist & Testbuild Teardown
status: PLANNED
owner-backend: DeepSeek Flash
owner-frontend: Kimi
architect: DeepSeek Pro
sprint: Phase 3C
---

# F-TD-001 — Pre-Merge Test Checklist & Testbuild Teardown

## Summary

Formalize the interactive pre-merge test checklist (currently at `/test-checklist`) into a lightweight admin-only testing tool with DB-persisted results, then tear down the abandoned `testbuild.zubbystudio.shop` deployment.

## Current State

- **Checklist page:** Live at `https://testdrive.epm.zubbystudio.shop/test-checklist` — static HTML/JS with 20 checkboxes across 4 sections, pass/fail counters, sign-off markdown generator
- **Checklist source file:** `backend/app/checklist.html` (served by `/test-checklist` route in `main.py`)
- **Standalone copy:** `.github/test-checklist.html` (repo root)
- **testbuild.zubbystudio.shop:** Abandoned Docker Compose service (`docker-compose.test-builder.yml`), still running on VPS port 8000 behind Traefik

## Requirements

### Part 1: Admin-Only Guard + Result Persistence

The checklist stays as a static HTML page (no SPA integration), but:

1. **Admin-only guard:** Move the route into a proper router (`backend/app/routers/checklist.py`) with `require_admin` dependency. Non-admin users get 401.
2. **Persist results:** When "Generate Sign-off" is clicked, POST the results to `POST /api/v1/checklist/runs` which saves to a new `checklist_runs` table:
   - `id` (PK, auto-increment)
   - `admin_id` (FK to users)
   - `results_json` (JSON — the pass/fail state per item)
   - `signoff_markdown` (TEXT)
   - `created_at` (TIMESTAMP)
3. **History list:** Below the checklist on the same page, show past runs fetched from `GET /api/v1/checklist/runs` (last 10, most recent first, with date + pass/fail summary)
4. **Navbar link:** Add `/test-checklist` link under Admin section in `Navbar.tsx` (admin users only)

**Checklist items stay hardcoded in the HTML/JS** — no checklist_items table, no CRUD, no admin UI for editing items. This is deliberately lightweight (YAGNI on configurable items).

### Part 2: File Reorganization

- **Move:** `backend/app/checklist.html` → `backend/app/static/checklist/index.html`
- **Update route:** Must update the `FileResponse` path in the same commit that moves the file (otherwise the existing URL breaks)
- **Route update:** The old `@app.get("/test-checklist")` in `main.py` is removed; the new router at `backend/app/routers/checklist.py` registers the same path via `router.get("/test-checklist")`

### Part 3: Tear Down testbuild.zubbystudio.shop

Only after Part 1 is deployed and verified on testdrive:

1. **Stop container:** `docker compose -f docker-compose.test-builder.yml down`
2. **Backup SQLite volume** before deletion:
   ```bash
   docker run --rm -v test_builder_data:/data -v $(pwd)/backups:/backup alpine cp /data/db.sqlite /backup/testbuilder-$(date +%F).sqlite
   ```
3. **Archive compose file:** `mv docker-compose.test-builder.yml docker-compose.test-builder.yml.archived`
4. **Verify:** `curl https://testbuild.zubbystudio.shop` returns connection refused or 502

### Part 4: Update progress-tracker

- Remove F-TD-001 from pending
- Add note: testbuild.zubbystudio.shop decommissioned, checklist live at `/test-checklist`

## API Contract

### POST /api/v1/checklist/runs (save a run)

**Request:**
```json
{
  "results": { "holds-no-toggle": true, "regs-no-toggle": true, ... },
  "signoff_markdown": "## Pre-Merge Test Results\n..."
}
```

**Response (201):**
```json
{
  "data": {
    "id": 1,
    "created_at": "2026-07-05T10:00:00Z"
  }
}
```

### GET /api/v1/checklist/runs (list history)

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "username": "zubbyik",
      "pass_count": 18,
      "fail_count": 1,
      "skip_count": 1,
      "created_at": "2026-07-05T10:00:00Z"
    }
  ],
  "meta": { "total": 1 }
}
```

## Checklist HTML Changes

The existing static HTML (`checklist.html`) needs:

1. **On "Generate Sign-off":** After generating the sign-off markdown, POST to `POST /api/v1/checklist/runs` via `fetch('/api/v1/checklist/runs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ results, signoff_markdown }) })`
2. **On page load:** `fetch('/api/v1/checklist/runs', { credentials: 'include' })` to show last 10 runs in a list below the checklist
3. **No other changes needed** — the existing pass/fail toggle + signoff generation logic stays the same

## Files

- **Create:** `backend/app/routers/checklist.py` — route + DB operations
- **Move:** `backend/app/checklist.html` → `backend/app/static/checklist/index.html`
- **Modify:** `backend/app/main.py` — remove the old `@app.get("/test-checklist")` route (line 79-85)
- **New Alembic migration:** `checklist_runs` table
- **Modify:** `estate-portfolio-manager/src/components/layout/Navbar.tsx` — add `/test-checklist` link in Admin section (admin only)
- **Archive:** `docker-compose.test-builder.yml` (Part 3)

## Sequencing

1. Backend: Create `checklist_runs` table (Alembic migration)
2. Backend: Create `routers/checklist.py` with POST + GET endpoints + admin guard
3. Frontend: Move `checklist.html` to `static/checklist/index.html`, update route path in same commit
4. Frontend: Update `checklist.html` JS to call new API endpoints
5. Frontend: Add navbar link in `Navbar.tsx`
6. Deploy: Build + restart container
7. Verify: `/test-checklist` loads for admin, 401 for non-admin
8. Teardown (only after verify): Stop testbuilder, backup SQLite, archive compose file

## What NOT to Build (YAGNI)

- **No configurable checklist items** — items stay hardcoded in HTML/JS
- **No checklist templates** — single "Pre-Merge" checklist only
- **No CI/CD integration**
- **No email notifications**
- **No SPA route** — stays as standalone HTML served by FastAPI
- **No multi-template support**
- **No cucumber/gherkin integration**

## Acceptance Criteria

1. `/test-checklist` loads for authenticated admin users (non-admin gets 401)
2. Completing a checklist and clicking "Generate Sign-off" saves the result to DB
3. Saved runs appear in history list on the same page (last 10, with date + pass/fail summary)
4. `/test-checklist` link visible in sidebar Admin section for admin users
5. testbuild.zubbystudio.shop returns 502/connection refused (decomissioned)
6. Backup of testbuilder SQLite exists before deletion
