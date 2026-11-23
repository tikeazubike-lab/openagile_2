---
type: HO
id: HO-144
title: Claude Web → OpenCode: F-026 reconcile ruling — Option 2 accepted with conditions; urgent uncommitted-migration action
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Urgent, do first, independent of everything else below

`d1e2f3a4b5c6_f026_registrar_dashboard_schema.py` is uncommitted on disk.
This is the exact failure mode behind the HO-080–119 file-loss incident —
commit it to `test` now, own commit, message referencing HO-143/HO-144,
and report the real 40-character SHA in your response. Do this before
starting on the reconciliation branch below.

## Ruling on Item 3 scope — Option 2 accepted, with conditions

HO-143's evidence changes the ruling from HO-142. "F-026-only" commits to
cherry-pick don't exist: `due_date` is a genuinely shared column between
the reminder system and `global-tracker`, the seed script was authored
inside an F-026b commit, and the dashboard routes live only inside a
1601-file restore commit. Artificial file-level extraction (Option 1)
would require manually splitting a shared column across two PRs with
merge-ordering to avoid a double-add — a self-inflicted risk for a
boundary the code no longer actually respects.

**Proceed with Option 2 — fold F-026 dashboard/seed work into the F-026b
branch — under these conditions:**

1. Rename the branch/PR: `feature/f-026-dashboard-and-f-026b-reminders`
   (or equivalent). PR description must state explicitly: this PR carries
   (a) F-026's dashboard/seed work, previously declared complete in
   MASTER_CONTEXT v4.8 and deployed to production via direct VPS execution
   but never merged into `main`'s git history until now, and (b) F-026b's
   email reminder infrastructure — combined because they share the
   `due_date` column and cannot be cleanly separated. This must be
   documented as a deliberate, scoped combination, not silently discovered
   later by someone reading the diff.
2. Add the missing `RegistrarContactField` ORM model to `models.py`. The
   migration already ran and the table already exists in production; its
   absence from the model layer is a live drift bug, independent of this
   reconciliation, and this is the right point to close it rather than
   deferring again.
3. Full `pytest -q` run, raw output, confirmed green before the PR opens.

Once merged: rebuild `feature/f-026b`... — no, disregard; there is no
separate `feature/f-026b` after this point. The combined branch above *is*
the feature branch. Confirm it green standalone (already required by
condition 3) and open the PR directly from it.

## Logged, not blocking

The `4d1c5c9` "restore: handover files" commit (1601 files, including the
dashboard route implementation) is flagged for the v4.11 discrepancy log —
same family of concern as the earlier file-loss pattern. No action
requested on it now.

The xpassed-removal explanation (HO-143) is accepted as accurate framing
for v4.11's test-suite-health section — stale dead-code references
removed, not resolved by F-009 shipping.

## Status

F-026b (now merged in scope with F-026's dashboard reconciliation) remains
**not closed**. Report back via **HO-145** once: the migration commit is
in with its real SHA, the combined branch is built and green, and the PR
is open.
