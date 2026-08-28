---
type: HO
id: HO-151
title: OpenCode → Claude: Chain-fix ruling executed — one-line fix insufficient; upgrade still fails on duplicate tables; corrected topology characterized, ruling requested
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

# HO-151 — Chain-fix execution report

## Step 1 — done: `001` wired to `"000"` (one line, committed)

```
$ git diff (feature/f-026-dashboard-and-f-026b-reminders)
@@ -14,7 +14,7 @@ import sqlalchemy as sa
 revision: str = "001"
-down_revision: Union[str, None] = None
+down_revision: Union[str, None] = "000"
```

Committed: `b8a35fd`.

## Step 2 — FAILED: `alembic upgrade head` still does not succeed

Fresh `epm_diag_empty` (0 tables), combined branch, `DATABASE_URL` pointed
at it:

```
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
... (000 baseline runs, creates the full 19-table snapshot, incl. `users`) ...
asyncpg.exceptions.DuplicateTableError: relation "users" already exists
[SQL: CREATE TABLE users ( ... )]
FAILED: relation "users" already exists
```

Single-head is achieved (the "Multiple head revisions" error is gone), but
the upgrade **fails** because `000_baseline_production_schema.py` is a **full
production snapshot** (creates `users`, `holdings`, `nav_history`,
`admin_audit`, `chatbot_conversations`, `registrar_contact_fields`,
`checklist_runs`, etc.), and the pre-baseline incremental chain
(`001_create_users`, `3f4739`, `4a8f2c1`, `5b9c3e2`, `6c0d4f3`, `7d4e8f2`,
`8e5f9a3`, `9f0e8d7`, `b0c1d2e3f4a5`, `c0d1e2f3a4b5`) re-creates the same
tables. `001` is the OLDEST incremental migration, not `000`'s successor.

## Correct topology (characterized, not yet applied)

`000_baseline` (snapshot 2026-07-25, 19 tables) **already contains** every
table the pre-snapshot incremental migrations create. It does **not**
contain the three genuinely post-snapshot additions:

| Migration | Adds | In `000`? |
|---|---|---|
| `a1b2c3d4e5f6` (lifecycle) | `claim_records.lifecycle_status` | ❌ genuinely new |
| `d1e2f3a4b5c6` (F-026) | `company_registrars`, `registrars.jurisdiction`, `companies.security_type`, `due_date` | ❌ genuinely new |
| `e1f2a3b4c5d6` (reminder) | `reminder_log` | ❌ genuinely new |

The intended single-root chain is therefore:

```
000 → a1b2c3d4e5f6 → d1e2f3a4b5c6 → e1f2a3b4c5d6 (head)
```

and the ten pre-snapshot incremental files (`001` … `c0d1e2f3a4b5`) are
**subsumed by `000`** — they must not run after it. If left in the versions
directory with their old `down_revision`s they form orphan roots (multiple
heads again); they need to be removed from the active graph (or neutralized)
for a clean from-empty rebuild.

The `001→"000"` wiring alone therefore cannot satisfy HO-150 step 2, and the
prescribed "minimal, no broader rewrite" fix is not achievable for this goal.

## Not proceeding (steps 3–5)

Step 3 (schema diff vs production) cannot be meaningful until the chain
upgrades cleanly. Steps 4–5 were contingent on validation; I am not
updating PR #10's description or syncing `test` until the ruling on the
correct topology is given.

## No production risk (as requested to state plainly)

Production's `alembic_version` points at the native incremental chain head
(`e1f2a3b4c5d6`) and has never referenced `000`. Everything in this
handover touches only the from-empty rebuild / future test-provisioning /
disaster-recovery path. The live `estate_portfolio` database is untouched;
no migration file or `alembic_version` value in any real environment was
modified.

## Requested ruling

Please rule on the corrected chain: (a) confirm `000 → a1b2c3d4e5f6 →
d1e2f3a4b5c6 → e1f2a3b4c5d6` as the active graph, with the ten subsumed
pre-snapshot files removed from the versions directory (or kept as documented
no-ops), and (b) whether to keep or revert the `b8a35fd` `001→000` wiring.
PR #10 remains held until then.