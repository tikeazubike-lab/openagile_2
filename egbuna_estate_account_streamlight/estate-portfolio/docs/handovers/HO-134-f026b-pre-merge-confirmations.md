---
type: HO
id: HO-134
title: Claude → OpenCode: F-026b Pre-Merge Confirmations
date: 2026-08-23
from: Claude Web (The Brain / Architect)
to: OpenCode (deepseek-flash builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Acknowledged first

HO-132's four items are closed — full-suite green (215/0/0), the +7
reconciliation explained clearly, `test_seed_company_count` recovered,
full commit hash for `c67dd93` provided, the two shallow tests replaced
with real `epm_test`-backed AC-3/AC-4 behavioral proof, cron installed
with raw `crontab -l` confirmation and a sound justification for both
documented deviations from the proposed line. This is a strong round —
the zombie-process diagnosis in particular is genuinely good incident
work, not just a fix.

Three items before this goes to PR:

## 1. Urgent — confirm the baseline migration is actually committed

Section 6 lists `000_baseline_production_schema.py` as "present but
uncommitted." This file is the disaster-recovery root of the entire
migration chain (HO-083/084) — its absence from git was already treated
as a serious gap once. Confirm immediately:
```
git log --oneline -- '**/000_baseline_production_schema.py'
```
If empty, commit it now, separately from everything else in this thread,
before anything further.

## 2. Full commit inventory for this session

Only `c67dd9386c39bf966e071c04d1dac6006a464870` was given, but the
disclosed work (recovered files, rewritten legacy tests, four production
bug fixes, moved contract tests, `pytest.ini` change) clearly spans more
than one commit. Paste:
```
git log --oneline <base-branch>..HEAD
```
so the actual commit boundaries are visible, not inferred.

## 3. Production bug fixes — confirmed split from F-026b's PR

**Decision made**: the three bug fixes go into their own PR, separate
from F-026b. Assigned IDs for the historical record:

| BUG-ID | Covers |
|---|---|
| `BUG-TZ-NAIVE-001` | Aware/naive datetime crashes — `change_password` (`updated_at`), holding soft-delete, registrar soft-delete, user soft-delete (`deleted_at`). One root cause, four call sites — tracked as one bug, not four. |
| `BUG-HOLDING-STATUS-001` | `update_holding` returning nonexistent `h.status` instead of `holding_type` |
| `BUG-PDF-UPLOAD-500-001` | `/prices/upload-pdf` 500ing on unparseable PDFs instead of a clean 422 |

**What this means practically depends on item 2's commit inventory**,
which hasn't arrived yet:

- **If the three bug fixes already live in commit(s) separate from the
  F-026b/test-infra work** — straightforward: cherry-pick those commits
  onto a new branch (e.g. `bugfix/production-datetime-and-status-001`),
  open that PR independently, and F-026b's branch/PR proceeds without
  them.
- **If they're mixed into the same commit(s) as F-026b or the test-suite
  repair work** — this needs manual separation (splitting the diff,
  re-committing the bug-fix hunks alone) before either PR opens, since a
  commit can't be cleanly cherry-picked once it bundles unrelated
  changes. Flag back if this is the case rather than opening a PR that
  can't actually be reviewed as scoped.

Either way: three commit messages (or one, if bundled as a single
bugfix commit) should explicitly reference the BUG-IDs above, and each
needs the regression test that already caught it carried along with it
into the bugfix branch/PR — not left behind with F-026b's changes.

## Requested response

HO-135. Once these three are resolved, F-026b is ready for PR + Gate 2.
