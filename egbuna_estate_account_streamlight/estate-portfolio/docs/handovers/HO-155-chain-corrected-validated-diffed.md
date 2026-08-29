---
type: HO
id: HO-155
title: HO-154 executed — chain corrected, validated, diffed against production; two pre-existing drift items surfaced
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## What was done

### Steps 1–2: Archive + re-point (combined branch + test)

- Eleven subsumed files moved to `backend/alembic/versions/ARCHIVED-subsumed-by-000/` on combined branch (9 from test + `b0c1d2e3f4a5`/`c0d1e2f3a4b5` which were only on combined).
- `d1e2f3a4b5c6` down_revision changed from `"c0d1e2f3a4b5"` to `"000"` on both branches.
- `e1f2a3b4c5d6` unchanged (still points to `d1e2f3a4b5c6`).
- `alembic heads` confirms single head: `e1f2a3b4c5d6`.
- `alembic history` confirms clean linear chain: `<base> → 000 → d1e2f3a4b5c6 → e1f2a3b4c5d6`.

### Step 3: DDL review (no surprises)

- `d1e2f3a4b5c6`: creates `company_registrars` + adds `jurisdiction`, `security_type`, `due_date`. All guarded by existence checks. F-026's four items only.
- `e1f2a3b4c5d6`: creates `reminder_log`. Guarded by `_table_exists`. F-026b only.

### Step 4: Empty-DB test (success)

```
$ alembic upgrade head
Running upgrade  -> 000, Baseline: production schema snapshot
Running upgrade 000 -> d1e2f3a4b5c6, F-026: company_registrars join table, jurisdiction, security_type, due_date
Running upgrade d1e2f3a4b5c6 -> e1f2a3b4c5d6, F-026b: Add reminder_log table for email reminder infrastructure
```

22 tables, single head, no errors.

### Step 5: information_schema.columns diff vs production

**Same 22 tables.** Two pre-existing drift items surfaced:

| Diff | Cause | Risk |
|---|---|---|
| `jsonb` → `json` on 7 columns (`audit_logs.old_values/new_values`, `chatbot_conversations.extracted_entities`, `checklist_runs.results_json`, `communication_logs.tags/attachments`, `obsidian_sync_log.error_details`) | Baseline snapshot used `sa.JSON()` instead of `sa.JSONB()` — pre-existing, not caused by this chain | Low (functional; `json` works but loses binary storage/indexing benefit of `jsonb`) |
| `dividends.holding_id` present in diag, absent in production | Baseline includes it (line 215); production was never upgraded to match — pre-existing schema drift | Low (column is nullable, unused) |

All F-026/F-026b columns verified present in production: `company_registrars` table, `registrars.jurisdiction`, `companies.security_type`, `registrar_requirements.due_date`, `reminder_log` table. **No diff on these.**

### Step 6: test synced

Same archive + re-point applied. `alembic heads` → `e1f2a3b4c5d6` (single head). 207 tests pass. Pushed (`07ab11b`).

### Step 7: PR #10 — pending

Description update deferred to your call (the chain is now correct; description can be updated after the F-026 branch is merged).

## What was NOT done

No migration code was changed beyond the down_revision re-point. No `alembic stamp` was used. No production database was touched. PR #10 remains held.

## Request

Two items need your ruling before PR #10 can be described accurately:

1. **`json` vs `jsonb` drift** — should `000` be updated to use `sa.JSONB()` for PostgreSQL, or is `json` acceptable? (Either way, it's pre-existing; the chain didn't cause it.)

2. **`dividends.holding_id` drift** — should this column be dropped from `000` (matching production) or kept (matching the snapshot state)? (Also pre-existing.)
