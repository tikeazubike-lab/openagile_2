---
type: HO
id: HO-142
title: Claude Web → OpenCode: F-026b Item 3 ruling — F-026 reconciliation PR required; Item 0 follow-up
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

## Ruling on Item 3 — F-026b PR shape

Accepted evidence: `feature/f-026b` cannot run its own suite standalone
because `test_registrars_dashboard.py` depends on `/api/v1/registrars/
dashboard-summary` and `/global-tracker`, which exist on `test` but not on
`main`. This is a real dependency, not a scoping error on your part.

**This also surfaces a separate, more important gap**: MASTER_CONTEXT v4.8
declared F-026 "fully complete... production verified clean" on
2026-07-31, including a direct-psql production migration. If those routes
were deployed to production but never merged to `main` via PR, `main`'s
git history has been behind actual production state for roughly a month,
without Gate 2 review ever happening on that merge. This is logged as a
standing discrepancy, tracked separately from F-026b's closure.

**Neither of your two proposed options is authorized as-is.** Do this
instead, mirroring the Item 2 pattern:

1. Open `chore/f-026-reconcile` (from `main`) — cherry-pick **only** the
   F-026 dashboard/seed-related commits from `test`. Before opening it,
   report `git log main..test --oneline` filtered to F-026 work only, so
   scope can be confirmed before the PR goes up.
2. Route it through Gate 2 (PR + explicit approval) like any other merge
   to `main` — no exception for the fact that this is "catching main up,"
   since main has never actually had this code reviewed.
3. Once merged, rebuild `feature/f-026b` from updated `origin/main`.
   Confirm it is green standalone (`pytest -q`, full raw output) as the
   clean 5-commit branch originally intended in HO-136.
4. Open the F-026b PR from that clean branch.

Do not proceed with `test → main` wholesale, and do not cherry-pick F-026
routes directly into `feature/f-026b` — both would either pollute F-026b's
PR scope or route an unreviewed production-only feature into `main` without
its own Gate 2 pass.

## Follow-up on Item 0 — residual secret exposure in shared history

Untracking + `.gitignore` is accepted as closing the "prevent future
re-exposure" scope of Item 0. It does **not** close the fact that
`JWT_SECRET`, the `DATABASE_URL` password, and `EPM_ADMIN_PASSWORD` remain
retrievable from already-pushed commits on `origin/main` (from `3a9e58e`
onward) via ordinary `git log -p`. Since all three were already rotated,
the live risk is contained, but the historical exposure itself is not
remediated by untracking alone.

**Do not act on this yet.** A full history scrub (`git filter-repo` or BFG)
on already-shared history requires a force-push and coordinated
re-clone/re-fetch across every clone of this private repo — this is a
Zubbyik decision, not a builder-initiated action. Flag it back to me as an
open item for the v4.11 MASTER_CONTEXT update; no action expected from you
on this specific point until that decision is made.

## Minor — test-count reconciliation

`pytest --collect-only` on `test` post-split shows `211` (`207 passed + 4
xfailed`), with no mention of the `8 xpassed` tests that were part of the
baseline since F-022 (`TestTransactionSchema`, `xfail(strict=False)`
pending F-009). Confirm in the next handover whether these resolved
(F-009 shipped?) or simply weren't included in this particular
collect-only run's scope — one line is sufficient, not blocking F-026b's
closure.

## Status

F-026b remains **not yet closed**. Report back via **HO-143** (next in the
HO-126–155 buffer) once the F-026-reconciliation PR is merged and
`feature/f-026b` is confirmed green standalone.
