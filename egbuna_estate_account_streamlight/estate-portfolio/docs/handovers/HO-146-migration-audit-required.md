---
type: HO
id: HO-146
title: Claude Web → OpenCode: URGENT — full migration-chain audit required before PR #10 review; possible recurrence of the disaster-recovery gap
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Why this is being escalated past F-026b's own thread

HO-145's "noted for the record" section reports that **two additional,
previously-unknown migrations were uncommitted on disk**: `b0c1d2e3f4a5`
(admin_audit nullable — locked decision dated 2026-07-16) and
`c0d1e2f3a4b5` (chatbot — F-022, closed 2026-07-25). A third,
`a1b2c3d4e5f6` (lifecycle), remains uncommitted right now and was waved
off as "not required for F-026b."

If `admin_audit`'s migration has been uncommitted since mid-July, production
has been running schema that never existed in git for over a month. This is
the same category of gap `000_baseline_production_schema.py` was built to
permanently close (HO-083/084/086) — discovering three more instances of it
now means that fix did not close the underlying problem, only the specific
symptom visible at the time. This is being treated as a standing,
recurring gap, not a one-off oversight, until proven otherwise.

**PR #10 is held. Do not proceed toward Gate 2 review until this handover's
requirements are satisfied.**

## Required — full migration-chain audit

1. Untracked-file audit, across `main`, `test`, and every active feature
   branch (not just the four already found):
   ```
   comm -23 <(find backend/alembic/versions -name '*.py' | sort) \
            <(git ls-files backend/alembic/versions | sort)
   ```
   Run this per-branch (checkout each, or use `git show <branch>:path` to
   enumerate tracked files without checkout) and report raw output for
   each. I need to know the true count of uncommitted migrations, not
   confirmation that the four found so far are handled.

2. `alembic heads` on the combined branch (`feature/f-026-dashboard-and-
   f-026b-reminders`) once all four are committed — raw output. Also
   report the explicit `down_revision` chain for all four (`b0c1d2e3f4a5`,
   `c0d1e2f3a4b5`, `d1e2f3a4b5c6`, plus wherever `a1b2c3d4e5f6` fits) so I
   can confirm there is a single linear head, not a branch requiring a
   merge revision.

3. Resolve `a1b2c3d4e5f6` (lifecycle) — either commit it now if it's a
   real ancestor/descendant in the same chain, or confirm explicitly (with
   its `down_revision`) that it's genuinely unrelated to this chain and
   safe to leave for a separate handover. "Not required for F-026b" is not
   sufficient — I need to know whether it's a live disaster-recovery risk
   regardless of F-026b's scope.

4. Cross-check against production: `alembic current` (or equivalent
   direct query against production's `alembic_version` table) versus what
   the git chain's head actually is, once reconciled. I want confirmation
   production and the git chain agree, not an assumption that they do.

5. One-paragraph root-cause note: how did migrations from two already-
   closed, already-governance-reviewed features (F-007-era admin_audit,
   F-022 chatbot) end up uncommitted for weeks without the existing
   "write ≠ commit" standing rule (established after HO-080–119) catching
   it? This matters for whether the rule itself needs strengthening
   (e.g., a pre-session or pre-handover `git status` check) rather than
   just being restated again.

## Also required, smaller

Show `RegistrarContactField`'s actual field list from `models.py` next to
the migration's column list — confirm it's a real mapping, not a stub
sufficient only to satisfy an import.

## Status

F-026b / F-026-reconcile (PR #10) do not proceed to Gate 2 review until
this audit is delivered and I've ruled on it. Report back via **HO-147**.
