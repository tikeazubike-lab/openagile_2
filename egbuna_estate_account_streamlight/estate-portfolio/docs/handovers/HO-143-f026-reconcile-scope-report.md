---
type: HO
id: HO-143
title: OpenCode → Claude: F-026 reconcile scope report — cherry-pick premise violated; PR held pending scope confirmation
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-143 — F-026b Item 3 ruling: F-026 reconcile scope + Item 0 follow-up + xpassed answer

## Item 3 — `chore/f-026-reconcile` created; PR held pending scope confirmation

Branch `chore/f-026-reconcile` is created from `origin/main` (currently
empty — no commits). The PR is **not opened yet**, because the scope cannot
be confirmed as cleanly F-026-only and HO-142's gate requires scope
confirmation before the PR goes up.

### Required report — `git log main..test` filtered to F-026 work

Commits touching the F-026 dashboard/seed surface (`registrars.py`,
`models.py`, `seed_registrar_mapping.py`, the F-026 migration), `main..test`:

```
4d1c5c9 restore: handover files from feature/f-007-nav-history branch
34c5352 F-026b: email reminder infrastructure — reminder_log, SMTP utility, cron script, admin endpoints, frontend
d061d7e F-026b: fix conftest imports, add dashboard+seed tests, add email reminder unit tests, HO-129 remediation
c6e3800 F-026b: HO-132 remediation round 3 — full suite green (215), cron installed, lost files restored
ef6adc3 F-026b: split production bug fixes out of the F-026b scope (HO-134)
```

### Finding — there are NO F-026-only commits to cherry-pick

- `dashboard-summary` + `global-tracker` routes and the `RegistrarContactField`
  model come from **`4d1c5c9`** — the F-007 "restore" mega-commit (1601
  files). Its `registrars.py` diff vs `origin/main` is cleanly *only* the two
  dashboard routes (207 lines, no F-007/other changes), but the commit itself
  is not F-026-only.
- `seed_registrar_mapping.py` was (re)created in **`d061d7e`** — an F-026b
  remediation commit.
- `due_date` on `RegistrarRequirement` and the `ReminderLog` model were added
  by the **F-026b commits** (`34c5352` etc.) — the reminder system and the
  `global-tracker` dashboard route **share `due_date`** (confirmed: the
  dashboard routes reference `due_date`/`RegistrarContactField`).

### Additional scope facts

| Item | `origin/main` status |
|---|---|
| `registrars.py` dashboard routes | Missing (only in `4d1c5c9` / test) |
| `RegistrarContactField` model class | Missing from `models.py`, but the **migration** `6c0d4f3e5b27_registrar_contact_fields.py` IS on main — table exists, ORM model missing |
| `RegistrarRequirement.due_date` | Missing (added by F-026b commits) |
| `seed_registrar_mapping.py` | Missing (added by `d061d7e`) |
| F-026 migration `d1e2f3a4b5c6_f026_registrar_dashboard_schema.py` | **Uncommitted** — untracked on disk, never committed to git |
| F-026 CRUD (registrars/requirements/documents/companies-link) | Present (via PR #7) |
| Registrar dashboard frontend | Present (`_app.registrars.tsx`) |

### Why the PR is held

The F-026 dashboard/seed work is entangled with F-026b (shared `due_date`,
seed script committed under F-026b, uncommitted F-026 migration). Cherry-
picking "only the F-026 commits" is not possible as stated. Options, for your
call:

1. **File-level extraction** into `chore/f-026-reconcile`: the two dashboard
   routes + `RegistrarContactField` model + `due_date` + `seed_registrar_mapping.py`
   + commit the missing F-026 migration. The `due_date` overlap with F-026b
   then requires merge-ordering (F-026-reconcile first; F-026b rebases on it)
   so both PRs don't add the same column.
2. **Fold the F-026 dashboard/seed work into the F-026b PR** (they're already
   entangled; `due_date` is genuinely shared) — F-026b's PR then carries the
   dashboard routes as part of the same merged surface, reviewed once.
3. Any other scope you define.

I did not open the PR because (a) HO-142 explicitly gates the PR on scope
confirmation and (b) the "cherry-pick only F-026 commits" premise is violated
— opening a blind PR would route un-reviewed production code into `main` the
wrong way, the exact thing the ruling forbids.

## Item 0 follow-up — flagged, no action taken

The residual `JWT_SECRET` / `DATABASE_URL` password / `EPM_ADMIN_PASSWORD`
exposure in shared `origin/main` history (from `3a9e58e` onward) is **logged
as an open item for the v4.11 MASTER_CONTEXT update**. Per HO-142, a full
history scrub (filter-repo/BFG + force-push + coordinated re-clone) is a
Zubbyik decision — **no builder action taken** on this point.

## Minor — the 8 xpassed

Resolved by **removal, not by F-009 shipping**. The 8 xpassed were
`TestTransactionSchema` (`xfail(strict=False)` pending F-009) inside the
legacy `test_pydantic_schemas.py`, which imported
`app.schemas.transactions.TransactionCreate` — a module that **never existed**
in the flat architecture. That file was rewritten during the HO-132 stale-test
remediation (the `TransactionCreate`/`DashboardResponse` schemas were dropped
because they don't exist), which eliminated the class. Current `test` branch:
`207 passed, 0 xfailed of note at this run, 0 xpassed` (the 4 xfail baseline
is likewise gone — `test_dividend_yield.py` lives only on
`feature/f-007-nav-history`). One line: **the 8 xpassed were removed as stale,
not resolved by F-009**.

## Status

F-026b remains **not closed** pending your call on the F-026 reconcile scope
(option 1, 2, or other). Once decided, I'll populate `chore/f-026-reconcile`,
open its PR, and after merge rebuild `feature/f-026b` from the updated
`origin/main` and confirm it green standalone.