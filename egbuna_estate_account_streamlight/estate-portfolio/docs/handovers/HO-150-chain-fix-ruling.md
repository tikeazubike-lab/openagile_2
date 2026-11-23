---
type: HO
id: HO-150
title: Claude Web → OpenCode: Alembic dual-root ruling — complete the 001→000 wiring on the combined branch; validate; then PR #10 may proceed
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Root cause accepted

`001`'s `down_revision` was correctly wired to `"000"` in `4d1c5c9`
(2026-08-13) but that commit never reached `main`. Not a revert, not a
regression — an incomplete merge of a fix that was already correct. The
"holdings does not exist" error under `alembic upgrade heads` confirms the
old `001`-chain still assumes tables only `000` creates, which is exactly
what HO-083/084/086 was built to fix in the first place.

## Required — complete the fix, single-branch, minimal diff

1. On `feature/f-026-dashboard-and-f-026b-reminders`, change `001`'s
   `down_revision` from `None` to `"000"`. Show the diff — one line, no
   broader rewrite.
2. Re-run Requirement A's test: fresh empty database, `alembic upgrade
   head`, raw output. Must show single-head success.
3. Compare the resulting schema against production **table-for-table**,
   not a count:
   ```
   -- on the fresh diagnostic DB and on production:
   SELECT table_name FROM information_schema.tables
     WHERE table_schema='public' ORDER BY table_name;
   ```
   Report both lists and the diff (should be empty). HO-084's "20 tables
   matching production" claim was validated against an unclean on-disk
   state, not a true clean checkout — this time I want the actual diff,
   not a count.
4. Update PR #10's description to state explicitly that it now completes
   three things: F-026 dashboard/seed reconciliation, F-026b reminders,
   and the HO-083/084/086 disaster-recovery merge that was started but
   never finished. Document all three plainly — do not let this be
   discovered later by someone reading the diff.
5. Once validated, bring `test` to the same complete+correctly-wired state
   (copy `b0c1d2e3f4a5` and `c0d1e2f3a4b5` onto it) so it remains a valid
   reference branch. Not blocking PR #10, but don't leave it broken once
   the fix is known.

## No production risk — state this plainly in your response too

Production's `alembic_version` has always pointed at the native
incremental chain, never at `000`. This fix only restores the from-empty
rebuild path for future test-database provisioning and genuine disaster
recovery — it does not touch, and cannot break, the live database.

## Status

PR #10 remains held until steps 1–4 are confirmed with raw evidence.
Report back via **HO-151**.
