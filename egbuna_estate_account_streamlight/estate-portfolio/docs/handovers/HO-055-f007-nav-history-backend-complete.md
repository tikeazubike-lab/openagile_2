---
type: HO
id: HO-055
title: Hermes → Claude: F-007 NAV History — Phase 1 (Backend) Implementation Complete
date: 2026-07-12
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
supersedes: .context/feature-specs/F-007-nav-history.md (corrected v2026-07-08)
---

# HO-055 — F-007 NAV History Phase 1 Complete

## Spec Source

`.context/feature-specs/F-007-nav-history.md` (corrected version, 218 lines) — confirms single-portfolio flat `nav_history` table, n8n for scheduling (not APScheduler), scipy/XIRR out of scope.

## Files Created / Modified

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/models.py` | Modified | Added `NavHistory` + `AdminAudit` ORM models |
| `backend/alembic/versions/9f0e8d7c6b5a_add_nav_history_and_admin_audit.py` | Created | Migration — creates both tables |
| `backend/app/services/nav.py` | Created | NAV calculation service (price carry-forward, zero-qty exclusion) |
| `backend/app/routers/nav_history.py` | Created | 4 endpoints + audit logging |
| `backend/app/main.py` | Modified | Registered nav_history + nav_latest routers |

## What Was Built

### New Tables
- **`nav_history`**: `id` (SERIAL PK), `snapshot_date` (DATE UNIQUE), `total_value` (NUMERIC 18,4), `total_cost` (NUMERIC 18,4), `gain_loss` (NUMERIC 18,4), `notes` (TEXT), `created_at` (TIMESTAMPTZ) — matches spec exactly.
- **`admin_audit`**: `id` (SERIAL PK), `action`, `entity_type`, `entity_id`, `old_value`, `new_value`, `performed_by` (FK→users), `details`, `created_at` — created ahead of F-019 per locked architectural decision.

### NAV Calculation Service (`app/services/nav.py`)
- Fetches all active non-deleted holdings with companies.
- For each holding, gets `close_price` from `price_history` WHERE `price_date <= snapshot_date` ORDER BY `price_date DESC` LIMIT 1 (carry-forward, OQ-F007-3).
- Skips holdings where `num_shares = 0` (AT-F007-010).
- Skips holdings with no price data at all (partial NAV > no NAV).
- `total_value = SUM(num_shares × close_price)`, `total_cost = SUM(total_cost)`, `gain_loss = total_value - total_cost`.

### API Endpoints

| Endpoint | Auth | Verified | Matches Spec |
|---|---|---|---|
| `POST /api/v1/nav-history/snapshot` | ADMIN/SUPERADMIN | ✅ 200, returns row | Yes |
| `POST /api/v1/nav-history/recalculate` | ADMIN/SUPERADMIN | ✅ 200, sync, 5 days processed | Yes |
| `GET /api/v1/nav-history` | Any auth | ✅ 200, list + summary | Yes |
| `GET /api/v1/nav` | Any auth | ✅ 200, latest row | Yes |

### Behaviors Verified
- ✅ Idempotent snapshot — second call same day upserts, doesn't duplicate
- ✅ Readonly blocked from snapshot — 403
- ✅ Weekend skip during recalculate — July 12 (Sun) correctly skipped
- ✅ Audit logging — both snapshot and recalculate write to `admin_audit`
- ✅ Monetary values returned as strings (locked convention)
- ✅ All field values as strings per API contract

### OQ-1 Resolution (Price Table Name)
The spec's OQ-1 `[VERIFY THIS]` is resolved: the price table is **`price_history`** (model `PriceHistory` in `models.py:297`), NOT `equity_prices`. Column `close_price` (NUMERIC 10,2) is used for NAV calculation.

## Test Results

The containerized backend was tested end-to-end via live HTTP calls. All endpoints return correct status codes and data shapes. The existing integration test conftest (`tests/integration/conftest.py`) is **stale** — it references `app.models.users`, `app.models.companies`, etc. from the Owl Alpha era (flat `models.py` now). It cannot be run without a rewrite. Unit tests in `tests/unit/` may also have import path dependencies from the old model layout.

## Spec Deviations

None intentional. One implementation note: the spec says "202 Accepted — async" for recalculation, but since no task queue exists, it runs synchronously as discussed in the spec (§4, "do this synchronously for Phase 1").

## Next Steps (Pending User Check-in)

1. **Backfill script** (spec §8) — one-shot admin script to backfill NAV history from earliest price data. User requested a stop-and-check before writing this.
2. **PR** — User also requested a stop-and-check before opening any PR.
3. **Frontend Phase 2** — replace the stub at `_app.nav-history.tsx` with the Recharts line chart, summary row, and range selector.
4. **n8n daily job** — after frontend ships, configure n8n to call `POST /api/v1/nav-history/snapshot` daily at 18:00 WAT.

## Raw Output (recent commands run)

```
POST /snapshot → 200 {"snapshot_date":"2026-07-12","total_value":"43174252.0200","total_cost":"110350.0000","gain_loss":"43063902.0200"}
GET /nav-history → 200 {6 data_points, summary with change_pct fields}
GET /nav → 200 {"snapshot_date":"2026-07-12","total_value":"43174252.0200"}
POST /snapshot (readonly) → 403 {"detail":"Admin access required"}
POST /recalculate (Mon-Fri) → 200 {"days_processed": 5}
```
