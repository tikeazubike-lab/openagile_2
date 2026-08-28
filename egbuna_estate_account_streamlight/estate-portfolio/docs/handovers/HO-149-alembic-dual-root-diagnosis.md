---
type: HO
id: HO-149
title: OpenCode → Claude: Alembic dual-root incident — diagnosis only (Requirements A–C raw output)
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

# HO-149 — Dual-Root Incident Diagnosis (no fixes proposed)

## Requirement A — Empirical `alembic upgrade head` on a genuinely empty DB

Provisioned `epm_diag_empty` (fresh, 0 public tables) and ran against the
**combined branch** (`feature/f-026-dashboard-and-f-026b-reminders`), which
holds the complete migration file set:

```
$ DATABASE_URL=postgresql+asyncpg://openagile:...@172.18.0.14:5432/epm_diag_empty alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
ERROR [alembic.util.messaging] Multiple head revisions are present for given argument 'head';
       please specify a specific target revision, '<branchname>@head' to narrow to a specific head,
       or 'heads' for all heads
FAILED: Multiple head revisions are present for given argument 'head'; please specify a specific
        target revision, '<branchname>@head' to narrow to a specific head, or 'heads' for all heads
```

Forcing both roots (`alembic upgrade heads`) fails too, on a real table
conflict rather than cleanly:

```
$ alembic upgrade heads
sqlalchemy.exc.ProgrammingError: (asyncpg.exceptions.UndefinedTableError)
relation "holdings" does not exist
[SQL: ALTER TABLE holdings ADD COLUMN holding_type VARCHAR(20) DEFAULT 'active' NOT NULL]
```

**Conclusion:** today, `alembic upgrade head` from empty does NOT work. The
chain is not reproducible from empty via a single upgrade command. The
diagnostic DB was dropped afterward.

## Requirement B — Was `000` ever merged to `main`?

```
$ git log main -- backend/alembic/versions/000_baseline_production_schema.py
(empty)

$ git ls-tree main -- backend/alembic/versions/000_baseline_production_schema.py
(empty)
```

**Confirmed explicitly: `000_baseline_production_schema.py` has never reached
`main`.** The HO-083/084/086 disaster-recovery fix exists only on
`test`/feature branches. (Per-branch audit in HO-147 listed it as untracked
on `main` because it is genuinely absent there.)

## Requirement C — When did `001` lose its connection to `000`?

It was **wired, then never propagated to `main`** — not reverted:

```
$ git log --all -p --follow -- backend/alembic/versions/001_create_users_table.py  (down_revision line)
ec903df 2026-06-14  initial commit for openagile copied project
                     +down_revision = None
4d1c5c9 2026-08-13  restore: handover files from feature/f-007-nav-history branch
                     -down_revision = None
                     +down_revision = "000"
```

Per-branch current values:

```
test:          down_revision = "000"     ← correctly wired
origin/main:   down_revision = None      ← never received the 4d1c5c9 change
combined branch (built from origin/main): down_revision = None   ← inherited main's root
```

**Answer:** `001` was set to `"000"` in `4d1c5c9` (2026-08-13). The `test`
branch retains that wiring. `main` never got it, so every `main`-derived
branch (including the combined `feature/f-026-*` branch) presents **two
roots** (`000` + `001`), which is exactly the "Multiple head revisions"
failure in Requirement A. It was never reverted; it was never merged.

**Additional chain-brokenness found while diagnosing:** no single branch is
currently a complete, working single-root chain:

| Branch | 001→000 wiring | File set |
|---|---|---|
| `test` | ✅ `"000"` | ❌ missing `b0c1d2e3f4a5` + `c0d1e2f3a4b5` (only on combined branch) → `alembic heads` errors `KeyError: 'c0d1e2f3a4b5'` |
| combined | ❌ `None` (from main) | ✅ complete |
| `main` | ❌ `None` | ❌ missing `000`, `9f0e8d7c6b5a`, `d1e2f3a4b5c6`, `e1f2a3b4c5d6` |

This means the HO-084 "12/12 validated from empty" claim was validated
against the on-disk state at the time (all files present + `001→000` wiring),
not against a clean `git clone` → `checkout` → `upgrade head`, which would
have failed then too (the four migrations were untracked; a fresh clone had
no `000`, `a1b2c3d4e5f6`, `b0c1d2e3f4a5`, `c0d1e2f3a4b5`, `d1e2f3a4b5c6`).
That claim has not been re-verified since and does not hold for a clean
checkout today.

## Requirement D — Freeze on new migrations

Noted. No new `alembic revision` files were created in this session; none
landed on any branch. No exceptions requested.

## Noted, not actioned

`9f0e8d7c6b5a` missing from `main` while present/applied in production
remains logged as a symptom of the same direct-VPS-execution-without-PR
systemic cause (HO-148's separate note). No action taken here.

## Status

PR #10 remains held. Diagnosis complete — awaiting your ruling on
remediation. No migration file, `down_revision`, or `alembic_version` table
was modified in any environment during this handover.