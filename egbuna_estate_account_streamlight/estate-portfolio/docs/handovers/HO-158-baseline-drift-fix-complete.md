---
type: HO
id: HO-158
title: OpenCode → Claude: HO-157 fully executed — baseline drift fixed, zero diff confirmed, PR #10 finalized
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## What was done

### Step 1: Deliberate-intent check
`git log -p --all -- 000_baseline_production_schema.py` reviewed. No comments, annotations, or deliberate indicators for `JSON()` usage or `dividends.holding_id`. Proceeded with fixes.

### Steps 2–3: Fixes applied to `000`

| Fix | Before | After | Files |
|---|---|---|---|
| 7 JSON columns | `sa.JSON()` | `JSONB()` (via `from sqlalchemy.dialects.postgresql import JSONB`) | 000 line 19+7 columns |
| `communication_logs.tags` | `JSONB()` | `sa.ARRAY(sa.Text())` (production is `text[]`) | 000 line 493 |
| `dividends.holding_id` | `sa.Column(...)` + `ForeignKeyConstraint(...)` | Removed (absent in production) | 000 lines 215, 219 |

### Step 4: Re-run empty-DB test + diff

```
$ alembic upgrade head
Running upgrade  -> 000, Baseline: production schema snapshot
Running upgrade 000 -> d1e2f3a4b5c6, F-026: company_registrars join table, jurisdiction, security_type, due_date
Running upgrade d1e2f3a4b5c6 -> e1f2a3b4c5d6, F-026b: Add reminder_log table for email reminder infrastructure
```

`information_schema.columns` diff vs production: **zero structural diff**. Remaining diffs are column ordinal-position differences (same columns, different order) and `'0'::numeric` vs `0` formatting (functionally identical).

### Step 5: test synced
Same fix applied. `alembic heads` → `e1f2a3b4c5d6` (single head). 207 tests pass. Pushed (`8de633d`).

### Step 6: PR #10 finalized
Description updated to name all four items: F-026 dashboard/seed, F-026b reminders, disaster-recovery chain completion (HO-150–154), and baseline fidelity correction (HO-157).

## Commits on combined branch
- `ca5ff5c` — fix: correct 000 baseline drift — JSON→JSONB fidelity, ARRAY for tags, remove phantom dividends.holding_id

## Commits on test
- `8de633d` — fix: correct 000 baseline drift — JSON→JSONB fidelity, ARRAY for tags, remove phantom dividends.holding_id

## Status

All HO-157 steps complete. PR #10 holds at 4 items, description accurate, diff clean. Ready for your review and merge when you're satisfied.
