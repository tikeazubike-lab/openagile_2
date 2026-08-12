---
id: HO-029
title: Phase A Acceptance Fixes + F-013 & F-TD-001 Specs Ready
status: COMPLETE
author: Hermes Agent (Governance)
reviewer: Claude (Architect)
created: 2026-07-05
sprint: Phase 3C
---

# HO-029 — Phase A Acceptance Fixes + F-013 & F-TD-001 Specs Ready

## Summary

Completed Phase A human testing acceptance on testdrive.epm.zubbystudio.shop. Fixed 2 of 3 failures found during testing, merged to main, and produced two feature specs (F-013 Companies Page, F-TD-001 Checklist & Teardown) reviewed by DeepSeek Architect. Both specs are patched and ready for implementation.

## What Was Done

### 1. Phase A Human Testing (testdrive.epm.zubbystudio.shop)

| Test | Result | Root Cause | Fix |
|------|--------|------------|-----|
| Companies — full list loads | 🔶 DEFERRED | Page is a scaffold stub ("Build it out next") — not a bug, feature not built | Planned as F-013 |
| Price History — OKOMUOIL loads | ✅ Fixed | Frontend defaulted to `days=30`; OKOMUOIL's 2 records (Dec 2025) were filtered out | Changed default to 365 |
| 401 redirects to login | ✅ Fixed | Root `StaticFiles` mount at `/` intercepted all paths and returned 404 | Removed mount, catch-all handles SPA routes |

### 2. SPA Routing Fix (commit `a5cee42`)

**Problem:** `app.mount("/", StaticFiles(...))` at `main.py:88` matched the root prefix first (Starlette checks Routes before Mounts, but the Mount at `/` catches everything). All client-side routes like `/login`, `/holdings`, `/companies` got 404s from the mount.

**Fix:** Removed `app.mount("/", StaticFiles(...))`. SPA is served via a catch-all route with `@app.get("/{full_path:path}")` that returns `index.html`. `/assets/` paths are still served via a dedicated `StaticFiles` mount at `/assets`.

**Files changed:**
- `backend/app/main.py` — removed root StaticFiles mount, added `@app.get("/")` to catch-all handler

**Deployed to:** testdrive.epm.zubbystudio.shop

### 3. Price History Default Range Fix (same commit)

**Problem:** Frontend defaulted to `days=30` in `_app.price-history.tsx:120`. OKOMUOIL's only price records are from Dec 30-31, 2025 (6 months old). The 30-day API filter returned empty.

**Fix:** Changed default from `30` → `365`.

**Files changed:**
- `estate-portfolio-manager/src/routes/_app.price-history.tsx` — line 120, `useState<number>(30)` → `useState<number>(365)`

### 4. Merge to Main

- PR from `test` branch merged to `main` (commit `c788b85`)
- Fixes pushed directly to `main` (commit `a5cee42`)
- Docker container rebuilt and restarted on VPS

## Feature Specs Produced

### F-013 — Companies Page

| Spec | Status |
|------|--------|
| File | `.context/feature-specs/F-013-companies-page.md` |
| Architect Review | ✅ CHANGES REQUESTED → Patched |
| Verdict | Ready for implementation |

**Scope:** Build Companies scaffold stub into a searchable/filterable table with TanStack React Table + company profile page at `/companies/:id`.

**Key corrections from architect review:**
- Removed `market` filter (no DB column — YAGNI)
- Added `registrar_name` as backend change needed
- Added `GET /api/v1/companies/{id}` as must-create endpoint
- Added `GET /api/v1/holdings?company_id=X` filter
- PriceHistory chart extraction optional (inline if time-constrained)
- Filter persistence via TanStack Router URL search params

### F-TD-001 — Test Checklist & Teardown

| Spec | Status |
|------|--------|
| File | `.context/feature-specs/F-TD-001-test-checklist-teardown.md` |
| Architect Review | ✅ CHANGES REQUESTED → Patched |
| Verdict | Ready for implementation |

**Scope:** Admin-only guard on `/test-checklist`, DB-persisted checklist runs, history list, then teardown testbuild.zubbystudio.shop.

**Key corrections from architect review:**
- Removed configurable checklist items (scope creep — YAGNI)
- Added full API contract (POST/GET request/response shapes)
- Added Alembic migration to plan
- Added sequencing note for file move + route path sync

## Current State

| Component | Status | Location |
|-----------|--------|----------|
| testdrive.epm.zubbystudio.shop | ✅ Live with SPA routing fix | VPS Docker |
| testbuild.zubbystudio.shop | ⏳ Still running (to teardown in F-TD-001) | VPS Docker |
| Companies page | 🔶 Scaffold stub — to be built (F-013) | SPA route `_app.companies.tsx` |
| Test checklist | ✅ Live at `/test-checklist` | `backend/app/checklist.html` |
| Feature specs | ✅ Both reviewed & patched | `.context/feature-specs/` |

## Agent Configuration

Per current `.context/agents.yaml`:
- **Backend:** DeepSeek Flash (`openrouter/deepseek/deepseek-v4-flash`)
- **Frontend:** Kimi (`openrouter/kimi/k2.0`)
- **Review/Architect:** DeepSeek Pro (`openrouter/deepseek/deepseek-v4-flash`)

## Next Steps for Claude Web

1. Review HO-029 to catch up on Phase A results and spec status
2. Implementation can proceed:
   - F-013: Backend (DeepSeek Flash) + Frontend (Kimi) — Companies page + profile page
   - F-TD-001: Backend + Frontend (DeepSeek Flash + Kimi) — Checklist persistence + teardown
3. Review implementation output and provide oversight
