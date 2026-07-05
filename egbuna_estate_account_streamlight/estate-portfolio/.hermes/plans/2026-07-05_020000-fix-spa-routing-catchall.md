# Fix 3 Human-Testing Failures

> **For Hermes:** Use subagent-driven-development to implement this plan task-by-task.

**Goal:** Fix the 3 failures found during human testing of testdrive.epm.zubbystudio.shop so the release can proceed.

**Root causes:**
1. **SPA routing (Companies blank, 401 no redirect):** `app.mount("/", StaticFiles(html=True))` at `main.py:88` intercepts all client-side routes before the `/{full_path:path}` catch-all and returns 404 instead of `index.html`
2. **Price History (OKOMUOIL empty):** Frontend defaults to `days=30`, but OKOMUOIL's only price records are from Dec 2025 — filtered out by the date window
3. **Companies blank:** Same as #1 — SPA never loads

**Tech Stack:** FastAPI 0.115.6, Starlette 0.41.3, React + TanStack Router, Recharts

---

## Investigation Findings

### Finding 1: SPA routing (affects Companies & 401 redirect)

`main.py:88` mounts StaticFiles at root `/` with `html=True`. In Starlette 0.41.3, this Mount object is placed in the routes list BEFORE the `/{full_path:path}` route (line 102). The mount matches every path starting with `/` and handles it — but `html=True` only serves `index.html` for paths ending in `/` (directory paths). Everything else gets 404.

**Verified internally:**
```
/login     → 404  (should serve index.html)
/holdings  → 404  (should serve index.html)
/          → 200  ✅ (html=True works for root)
```

**Fix:** Remove the root `StaticFiles` mount at line 88, keep the `/assets` mount and the catch-all route.

### Finding 2: Price History date range

OKOMUOIL (company_id=1) has **2 price records** in the DB:
- 2025-12-30, price=1095.00
- 2025-12-31, price=1095.00

The frontend `_app.price-history.tsx:120` defaults to `days=30` and the API `prices.py:269` applies a `days` filter (default 30). The records are 190+ days old — filtered out. The user sees "No price history for OKOMUOIL yet."

**DB confirmed:** 2 records exist for company_id=1. The API `GET /api/v1/prices/history/1?days=365` would show the data. The default of 30 days is too short for stocks with infrequent price uploads.

**Fix:** Change frontend default from `days=30` to `days=365` (or 0 = all).

### Finding 3: 401 redirect

The frontend (`_app.tsx:29-33`) already has the redirect logic:
```typescript
if (!res.ok) throw redirect({ to: "/login" });
```
This works once the SPA loads. The failure was because the SPA never loaded (SPA routing issue above).

---

## Task 1: Fix SPA routing (back-end)

**Objective:** Remove the root StaticFiles mount that intercepts all paths, replace with a proper catch-all that serves `index.html` for all client-side routes.

**Files:**
- Modify: `backend/app/main.py:87-109`

**Step 1: Read current file**

Read `backend/app/main.py` lines 79-109 to confirm exact content.

**Step 2: Apply changes**

Replace the static file serving block (lines 87-109) with:

```python
# ── Static files (React SPA) ──────────────────────────────────────────────────
# Strategy:
#   1. Mount /assets as StaticFiles → serves Vite-hashed JS/CSS bundles
#   2. Root route "/" + catch-all → returns index.html for any SPA route
#      so TanStack Router can handle client-side routing.
# NOTE: Do NOT mount StaticFiles at "/" with html=True — it intercepts all
# paths and returns 404 for client-side routes like /login, /holdings, etc.

_static_dir = os.path.join(os.path.dirname(__file__), "static")
_index_html = os.path.join(_static_dir, "index.html")

if os.path.isdir(_static_dir):
    # Serve Vite build assets (JS, CSS, images) at /assets/*
    _assets_dir = os.path.join(_static_dir, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    # SPA catch-all: any non-API, non-asset path returns index.html
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str = ""):
        response = FileResponse(_index_html)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
```

Changes:
- REMOVED: `app.mount("/", StaticFiles(directory="app/static", html=True), name="static")`
- ADDED: `@app.get("/")` root route stacked on the same handler
- KEPT: `/assets` mount for Vite bundles (unchanged)
- KEPT: `/{full_path:path}` catch-all

**Step 3: Verify internally**

Run inside the container:
```bash
docker exec estate_portfolio_v3 python -c "
import urllib.request
for path in ['/', '/login', '/holdings', '/companies', '/price-history']:
    try:
        resp = urllib.request.urlopen(f'http://localhost:8000{path}')
        print(f'{path}: {resp.status} (content-type: {resp.headers.get(\"content-type\")})')
    except Exception as e:
        print(f'{path}: {e}')
"
```

Expected — all 200:
```
/: 200 (text/html)
/login: 200 (text/html)
/holdings: 200 (text/html)
/companies: 200 (text/html)
/price-history: 200 (text/html)
```

**Step 4: Verify API still works**

```bash
docker exec estate_portfolio_v3 python -c "
import urllib.request, urllib.error
try:
    resp = urllib.request.urlopen('http://localhost:8000/api/v1/companies')
    print(f'/api/v1/companies: {resp.status}')
except urllib.error.HTTPError as e:
    print(f'/api/v1/companies: {e.code} (correctly requires auth)')
"
```

Expected: `401 (correctly requires auth)`

**Step 5: Rebuild and restart**

```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio
docker compose -f docker-compose.v3.yml build epm
docker compose -f docker-compose.v3.yml up -d epm
```

---

## Task 2: Fix Price History default date range (front-end)

**Objective:** Change the default `days` filter from 30 to 365 so companies with older price data (like OKOMUOIL, last updated Dec 2025) show data by default.

**Files:**
- Modify: `estate-portfolio-manager/src/routes/_app.price-history.tsx:120`

**Step 1: Read the file**

Read line 120:
```typescript
const [daysFilter, setDaysFilter] = useState<number>(30); // 7, 30, 90, 365, 0 (All)
```

**Step 2: Apply change**

Change `30` to `365`:
```typescript
const [daysFilter, setDaysFilter] = useState<number>(365); // 7, 30, 90, 365, 0 (All)
```

**Step 3: No rebuild needed** (frontend is built inside Docker — rebuild will cover it in Task 1 Step 5)

**Verification** (post-rebuild):
1. Log in to testdrive
2. Navigate to Price History
3. Select OKOMUOIL from the company dropdown
4. Expected: 2 price records show (Dec 2025) rather than "No price history yet"

---

## Task 3: Verify on testdrive

**Objective:** Confirm all 3 failures are resolved on the live site.

**Step 1: Curl SPA routes**

```bash
for path in /login /holdings /companies /price-history; do
  echo "$path: $(curl -s -o /dev/null -w '%{http_code}' "https://testdrive.epm.zubbystudio.shop$path")"
done
```

Expected: all 200.

**Step 2: Browser test — Companies page**

1. Log in as `zubbyik`
2. Navigate to Companies
3. Expected: 203 companies load, filter/search works

**Step 3: Browser test — Price History**

1. Log in as `zubbyik`
2. Navigate to Price History
3. Select OKOMUOIL from the combobox
4. Expected: 2 price records from Dec 2025 appear (not "No price history yet")

**Step 4: Browser test — 401 redirect**

1. Open incognito / clear cookies
2. Navigate to `https://testdrive.epm.zubbystudio.shop/holdings`
3. Expected: redirect to `/login`

---

## Verification Summary

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | SPA routes (curl) | `/login`, `/holdings`, `/companies`, `/price-history` all return 200 |
| 2 | Companies page (browser) | 203 companies load, filter/search works |
| 3 | Price History OKOMUOIL (browser) | 2 price records from Dec 2025 show by default |
| 4 | 401 redirect (browser incognito) | `/holdings` → redirects to `/login` |
| 5 | API endpoints (curl, no auth) | All return 401 (unchanged security) |

---

## Risks & Notes

- **No side effects:** The SPA routing fix only changes how index.html is served. API endpoints are untouched.
- **Frontend rebuild:** Both changes are baked into the Docker image. A single `docker compose build` covers both.
- **OKOMUOIL data:** Only 2 records exist (Dec 2025). If more price data was loaded today, it may use a different company_id or a different table. Verify after fix by checking `?days=365`.
- **No user-facing regression:** The old static mount was functionally broken for non-root paths. The fix strictly expands the paths that return index.html.
- **Date range UX:** Changing default to 365 means the page initially shows 1 year of data. Users can still switch to 7/30/90/All via the existing filter buttons.
