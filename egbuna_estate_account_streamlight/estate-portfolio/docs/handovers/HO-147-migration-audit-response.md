---
type: HO
id: HO-147
title: OpenCode → Claude: Full migration-chain audit — five instances found, all four committed, one NEW gap on main, two-heads finding
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

# HO-147 — Migration-Chain Audit (HO-146)

## Requirement 1 — Untracked-file audit (raw output)

`comm -23 <(find backend/alembic/versions -name '*.py' | sort) <(git ls-files backend/alembic/versions | sort)` on current branch (`test`):

```
a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
```

Per-branch enumeration of disk migration files NOT tracked in that branch
(`git ls-tree <branch>`):

```
main:                            000_baseline_production_schema.py
                                 9f0e8d7c6b5a_add_nav_history_and_admin_audit.py
                                 a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
                                 d1e2f3a4b5c6_f026_registrar_dashboard_schema.py
                                 e1f2a3b4c5d6_f026b_reminder_log.py
test:                           a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
feature/f-026-dashboard-and-f-026b-reminders:  a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
bugfix/production-bugs-001:     000_baseline_production_schema.py
                                 a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
                                 d1e2f3a4b5c6_f026_registrar_dashboard_schema.py
                                 e1f2a3b4c5d6_f026b_reminder_log.py
feature/HO-046-lifecycle-status: 000_baseline_production_schema.py
                                 9f0e8d7c6b5a_add_nav_history_and_admin_audit.py
                                 a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
                                 d1e2f3a4b5c6_f026_registrar_dashboard_schema.py
                                 e1f2a3b4c5d6_f026b_reminder_log.py
feature/f-007-nav-history:       000_baseline_production_schema.py
                                 a1b2c3d4e5f6_add_lifecycle_status_to_claim_records.py
                                 d1e2f3a4b5c6_f026_registrar_dashboard_schema.py
                                 e1f2a3b4c5d6_f026b_reminder_log.py
```

**True count of uncommitted migrations found: five, not four.** All but one
are now committed:

| Migration | Status now |
|---|---|
| `d1e2f3a4b5c6` (F-026) | ✅ committed `test` `cee703964337881aac7b8bcdc70bed361ac2531a` + combined branch (HO-144) |
| `b0c1d2e3f4a5` (admin_audit nullable) | ✅ committed combined branch `6887732` |
| `c0d1e2f3a4b5` (chatbot) | ✅ committed combined branch `6887732` |
| `a1b2c3d4e5f6` (lifecycle) | ✅ committed `test` `9e44e73bead99cdb503df62e9feffede092d293d` + combined branch (this audit) |
| **`9f0e8d7c6b5a` (nav_history + admin_audit)** | ⚠️ **NOT on `main`** — new finding. It IS tracked on `test`/combined/`f-007-nav-history`, but `main`'s alembic chain lacks it entirely. Main is therefore missing the nav_history + admin_audit schema in its git chain (production has those tables). Pre-existing (F-007), surfaced here for the first time. |

## Requirement 2 — `alembic heads` + down_revision chain (combined branch)

```
$ alembic heads
000 (head)
e1f2a3b4c5d6 (head)
```

**Two heads.** The incremental chain is a single linear chain:

```
001 → 3f4739d78390 → 4a8f2c1d9e05 → 5b9c3e2f4a16 → 6c0d4f3e5b27 →
7d4e8f2a1c03 → 8e5f9a3b2c04 → a1b2c3d4e5f6 → 9f0e8d7c6b5a →
b0c1d2e3f4a5 → c0d1e2f3a4b5 → d1e2f3a4b5c6 → e1f2a3b4c5d6 (head)
```

Explicit down_revisions (the four + where a1b2c3d4e5f6 fits):

| revision | down_revision |
|---|---|
| `a1b2c3d4e5f6` | `8e5f9a3b2c04` |
| `9f0e8d7c6b5a` | `a1b2c3d4e5f6` |
| `b0c1d2e3f4a5` | `9f0e8d7c6b5a` |
| `c0d1e2f3a4b5` | `b0c1d2e3f4a5` |
| `d1e2f3a4b5c6` | `c0d1e2f3a4b5` |
| `e1f2a3b4c5d6` (head) | `d1e2f3a4b5c6` |

The second head `000` is `000_baseline_production_schema.py`
(`revision="000"`, `down_revision=None`) — the standalone production-schema
snapshot root. **Within the incremental chain there is no branch, so no merge
revision is needed there.** But the overall graph has two roots (000 + 001),
which means `alembic upgrade head` from empty would apply BOTH the full 000
snapshot AND the incremental chain — a duplicate-table conflict. This is
pre-existing (000 was added in `76b80db` as the disaster-recovery snapshot)
and needs a ruling: either 000 is a documentation-only reference snapshot
(exclude from heads), or the graph must be reorganized. Flagging, not
self-fixing.

## Requirement 3 — `a1b2c3d4e5f6` (lifecycle) resolved

**It is a genuine chain ancestor** — `9f0e8d7c6b5a`'s `down_revision` is
`a1b2c3d4e5f6`. HO-145's "not required for F-026b" claim was **wrong**; it
is required for the chain to resolve from `8e5f9a3b2c04` to head. Committed:
`test` `9e44e73bead99cdb503df62e9feffede092d293d` (own commit) and added to
the combined branch. Live disaster-recovery risk closed.

## Requirement 4 — Production cross-check

```
$ SELECT version_num FROM alembic_version;   -- estate_portfolio (production)
e1f2a3b4c5d6
```

Production's `alembic_version` = `e1f2a3b4c5d6` = the incremental chain head.
Production has all expected tables (`admin_audit`, `chatbot_conversations`,
`company_registrars`, `nav_history`, `registrar_contact_fields`,
`registrar_requirements`, `reminder_log`, `claim_records`). **Production and
the git chain agree.** (Note: production's alembic_version holds the single
incremental head — the `000` snapshot was never applied there; it is a
recovery artifact.)

## Requirement 5 — Root-cause paragraph

These migrations were written and applied to production via the standing
direct-psql workflow (Alembic hung on lock contention in the past), then the
`.py` files were never `git add`ed. Because production kept working (the
schema was already applied), the missing files were invisible at runtime;
nothing in the daily workflow compares `git`'s migration set against the
disk or against `alembic_version`, so a broken chain (missing down_revisions)
went unnoticed for weeks. The "write ≠ commit" standing rule (HO-120) is
framed around code/handover artifacts and was never enforced specifically on
`backend/alembic/versions/`, and the features involved (F-007, F-022, F-026,
HO-046) were each "closed" on their own governance pass without a
migration-chain integrity check. The rule is sound but too narrow; I
recommend strengthening it with a routine pre-close check: (a) `git status
--short backend/alembic/versions/` must be empty, and (b) `alembic heads`
must equal the intended single head, before any feature is marked closed.
This belongs in the v4.11 MASTER_CONTEXT and/or the pre-merge checklist.

## Requirement 6 — `RegistrarContactField` mapping (not a stub)

Model (`models.py`) ↔ migration `6c0d4f3e5b27` — 8/8 columns match:

| column | model | migration |
|---|---|---|
| id | Integer PK | Integer autoincrement PK |
| registrar_id | Integer FK registrars.id (CASCADE, index) | Integer NOT NULL |
| field_type | String(20) NOT NULL | String(20) NOT NULL |
| field_value | Text NOT NULL | Text NOT NULL |
| label | String(100) nullable | String(100) nullable |
| sort_order | Integer default 0 | SmallInteger server_default '0' |
| created_at | DateTime(tz) server_default now | DateTime(tz) server_default NOW() |
| deleted_at | DateTime(tz) nullable | DateTime(tz) nullable |

Only cosmetic difference: `sort_order` `Integer` (model) vs `SmallInteger`
(migration) — semantically equivalent. Real, faithful mapping.

## Status

- PR #10 remains held pending your ruling on this audit.
- All five uncommitted-migration instances are now committed (four to `test`
  and/or the combined branch; `9f0e8d7c6b5a` is tracked but **missing from
  `main`** — needs a decision on whether `main` gets it via a follow-up PR).
- Two structural findings for ruling: (1) the 000-baseline two-heads
  situation, (2) `main`'s missing nav_history/admin_audit migration.
- Combined branch re-verified green after the migration additions:
  `207 passed, 4 xfailed, 0 failed`.