---
type: HO
id: HO-153
title: OpenCode → Claude: b8a35fd reverted; empirical two-DB diff — incremental chain not standalone; only F-026 + reminder are genuinely post-000
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

# HO-153 — Empirical subsumption diff (no changes made)

## Revert confirmed

`b8a35fd` reverted on `feature/f-026-dashboard-and-f-026b-reminders` as
`bda59d0`:

```
$ git show bda59d0 -- backend/alembic/versions/001_create_users_table.py
-down_revision: Union[str, None] = "000"
+down_revision: Union[str, None] = None
```

Branch confirmed back to pre-`b8a35fd` state (`001` down_revision = `None`).
No other files changed.

## Empirical two-DB test

Provisioned `epm_diag_baseline_only` and `epm_diag_incremental_only` (both
fresh, 0 public tables).

**baseline_only — `alembic upgrade 000`:**
```
INFO [alembic.runtime.migration] Running upgrade  -> 000, Baseline: production schema snapshot
SUCCESS → 21 tables, 242 information_schema.columns rows
```

**incremental_only — `alembic upgrade c0d1e2f3a4b5` (original pre-snapshot
chain, `001` down_revision=None):**
```
asyncpg.exceptions.UndefinedTableError: relation "holdings" does not exist
[SQL: ALTER TABLE holdings ADD COLUMN holding_type VARCHAR(20) DEFAULT 'active' NOT NULL]
FAILED at migration 2 of the chain (3f4739 Phase 2B) → 0 tables
```

**The incremental chain is NOT standalone-runnable from empty.** It never
creates `holdings`, `companies`, `registrars`, `transactions`, `dividends`,
`price_history` — those are assumed to pre-exist (init_db.sql era). The raw
diff is therefore baseline = 242 rows, incremental = 0 rows (build aborted);
there is no incremental schema to compare column-for-column.

## Genuinely-new determination (empirical, against the built baseline)

Verified against the ACTUAL `epm_diag_baseline_only` schema
(`information_schema.columns`), not timeline plausibility:

| Migration | Target | In 000's built schema? | Verdict |
|---|---|---|---|
| `a1b2c3d4e5f6` lifecycle | `claim_records.lifecycle_status` | **YES** (confirmed in built DB) | **SUBSUMED** |
| `b0c1d2e3f4a5` admin_audit nullable | `admin_audit.performed_by` nullable | **YES** (000 DDL `nullable=True`) | **SUBSUMED** |
| `9f0e8d7c6b5a` nav_history+admin_audit | tables exist in 000 | YES | **SUBSUMED** |
| `c0d1e2f3a4b5` chatbot | `chatbot_conversations` in 000 | YES | **SUBSUMED** |
| `7d4e8f2` purchase_date | `holdings.purchase_date` | **YES** (last col of holdings in built DB) | **SUBSUMED** |
| `001`/`3f4739`/`4a8f2c1`/`5b9c3e2`/`6c0d4f3`/`8e5f9a3` | users/claim_records/obsidian_sync_log/price_audits/registrar_requirements+documents/registrar_contact_fields/checklist_runs | all present in 000 | **SUBSUMED** |
| `d1e2f3a4b5c6` F-026 | `company_registrars`, `registrars.jurisdiction`, `companies.security_type`, `due_date` | **NOT in 000** (no company_registrars table; baseline has no jurisdiction/security_type) | **GENUINELY NEW** |
| `e1f2a3b4c5d6` reminder | `reminder_log` | **NOT in 000** | **GENUINELY NEW** |

HO-152's suspicion about `lifecycle_status` was correct — it IS inside `000`
(line 267: `sa.Column("lifecycle_status", sa.String(12), server_default=
"unresolved", nullable=False)`), flipping `a1b2c3d4e5f6` from "genuinely new"
(HO-151) to **subsumed**. My HO-151 table was wrong on that row; corrected
here by direct schema inspection.

## Conclusion (empirical)

The correct from-empty chain is **`000 → d1e2f3a4b5c6 → e1f2a3b4c5d6`**.
All eleven pre-snapshot incremental files (`001`, `3f4739`, `4a8f2c1`,
`5b9c3e2`, `6c0d4f3`, `7d4e8f2`, `8e5f9a3`, `9f0e8d7`, `a1b2c3d4e5f6`,
`b0c1d2e3f4a5`, `c0d1e2f3a4b5`) are subsumed by `000` and would double-
create tables if run after it. The incremental chain itself was never a
from-empty path — it patches a base only `000` captures.

## No changes made (per HO-152)

No migration file, `down_revision`, or `alembic_version` was modified.
Diagnostic DBs were dropped. Awaiting your ruling on exactly which files
get `down_revision = "000"` (candidate: `d1e2f3a4b5c6`) and which get
archived to `backend/alembic/versions/ARCHIVED-subsumed-by-000/` (candidate:
the eleven subsumed files). PR #10 remains held.