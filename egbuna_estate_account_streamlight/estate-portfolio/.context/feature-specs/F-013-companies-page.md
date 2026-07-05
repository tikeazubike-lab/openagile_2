---
id: F-013
title: Companies Page
status: PLANNED
owner-backend: DeepSeek Flash
owner-frontend: Kimi
architect: DeepSeek Pro
sprint: Phase 3C
---

# F-013 — Companies Page

## Summary

Build out the Companies scaffold stub into a full-featured page with a searchable, filterable list of all NGX-listed companies. Currently the page shows "This page is scaffolded. Build it out next." — the API already serves 195+ companies at `GET /api/v1/companies`, but the frontend doesn't render them.

## Current State

- **Backend:** `GET /api/v1/companies` returns `{ id, ticker, name, sector, status, current_price, last_price_update }` — **no `market` field**, **no `registrar_name`** in response
- **Frontend:** The route exists at `/companies` but renders a scaffold placeholder. `useCompanies()` hook exists in `src/api/queries.ts`
- **Table pattern:** Holdings page uses `@tanstack/react-table` with `flexRender`, `getCoreRowModel`, `getSortedRowModel` — this is the pattern to follow
- **Search/filter:** API has `?search=` param but current frontend has no filter UI

**Known backend gaps (must fix before or alongside frontend):**
1. `list_companies()` does not include `registrar_name` — needs `selectinload(Company.registrar)` and response update
2. `GET /api/v1/companies/{id}` does not exist — must be created for profile page
3. `GET /api/v1/holdings?company_id=X` does not exist — needed for profile page holdings

## Requirements

### Part 1: Companies List Page (`/companies`)

- Full table of all NGX-listed companies using `@tanstack/react-table` (same pattern as holdings page)
- Columns: Ticker, Name, Sector, Registrar
- **Search bar** — filter by ticker or name (client-side `useMemo` on data; 200 rows is fine)
- **Sector filter** — dropdown to filter by sector (Agriculture, Banking, Consumer Goods, etc.)
- Each row clickable → navigates to `/companies/:id` (company profile page)
- **Filter persistence:** Use TanStack Router `search` validators (URL search params) so filters survive navigation to profile and back
- No pagination (YAGNI for 200 rows — client-side filter covers it)
- Loading/empty/error states: shimmer while loading, "No companies match your filter" when empty, error banner on API failure

### Part 2: Company Profile Page (`/companies/:id`)

- Hidden from nav — only accessible by clicking a company from the Companies table
- Shows company details: name, ticker, sector, registrar name, ISIN, market cap, outstanding shares, date listed (data from new `GET /api/v1/companies/{id}` endpoint)
- Shows user's holdings for this company if any (data from `GET /api/v1/holdings?company_id=X`)
- Shows price history chart — either extract `PriceHistoryChart` from `_app.price-history.tsx` into a shared component, or inline the Recharts code. Extraction is cleaner but optional for Phase 3C
- Loading/empty/error states for each section
- Back link to `/companies` that preserves URL search params (filters intact)

## Backend Changes Required

### 1. Update `GET /api/v1/companies` (list)

- Add `selectinload(Company.registrar)` to eager-load registrar relation
- Include `registrar_name` (from `registrar.name`) in response dict
- Also expose `id, ticker, name, sector, status, current_price, last_price_update` (existing fields kept)

### 2. Create `GET /api/v1/companies/{id}` (detail)

- Returns full company detail: `{ data: { id, ticker, name, sector, status, current_price, last_price_update, isin, market_cap, outstanding_shares, date_listed, registrar: { id, name } } }`
- Returns 404 if company not found
- Requires auth (same as list)

### 3. Add `GET /api/v1/holdings?company_id=X` filter

- Holdings router already exists — add optional `company_id` query param to the existing `list_holdings()` endpoint
- When `company_id` is provided, filter holdings to that company only

## Frontend Files

- **Modify:** `estate-portfolio-manager/src/routes/_app.companies.tsx` — full table with search/filter
- **Create:** `estate-portfolio-manager/src/routes/_app.companies.$id.tsx` — company profile page (TanStack Router `$id` convention)
- **Modify:** `estate-portfolio-manager/src/api/queries.ts` — add `useCompany(id)` and `useHoldingsByCompany(companyId)` hooks
- **Possible create:** Shared `PriceHistoryChart` component extracted from `_app.price-history.tsx` (optional)
- **Modify (minor):** `backend/app/routers/companies.py` — add `registrar_name` to list, create detail endpoint
- **Modify (minor):** `backend/app/routers/holdings.py` — add `company_id` query param

## What NOT to Build (YAGNI)

- No NGX data scraping/refresh (F-019)
- No inline editing of company details
- No upload/download CSV (F-NGX-COMPANIES on Data Upload)
- No financial news (F-018)
- No corporate actions (F-014)
- No `market` column/board filter (no DB column — would need migration + backfill, defer)
- No server-side pagination (200 rows is fine client-side)
- No shared PriceHistoryChart extraction if time-constrained (can inline)

## Acceptance Criteria

1. Companies page renders all active companies in a sortable table (ticker, name, sector, registrar)
2. Search by name: typing "okomu" filters to OKOMUOIL
3. Filter by sector: selecting "Agriculture" shows only Agriculture companies
4. Click a company: navigates to `/companies/:id` showing company details
5. Company profile page: shows ticker, sector, registrar name, ISIN, market cap
6. Profile page shows user's holdings for that company (if any)
7. Back button returns to companies list with search/filter preserved
8. Profile page shows loading/error states correctly
9. Error: access protected companies endpoint without auth → 401
