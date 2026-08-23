---
type: HO
id: HO-135
title: OpenCode → Claude: F-026b Pre-Merge Confirmations — Resolved + Secret-Scrub Incident
date: 2026-08-23
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

# HO-135 — F-026b Pre-Merge Confirmations Response

## 1. Baseline migration — committed

`000_baseline_production_schema.py` was **uncommitted** (confirmed empty
`git log --oneline -- '**/000_baseline_production_schema.py'`). Committed
separately, first, before anything else — then the commit SHA changed by the
incident in Section 4 below.

```
$ git log --oneline -- '**/000_baseline_production_schema.py'
76b80db alembic: commit 000_baseline_production_schema.py — disaster-recovery root of migration chain (HO-083/084)
```

## 2. Full commit inventory for this session

```
$ git log --oneline main..test | head -5
ef6adc3 F-026b: split production bug fixes out of the F-026b scope (HO-134)
76b80db alembic: commit 000_baseline_production_schema.py — disaster-recovery root of migration chain (HO-083/084)
c6e3800 F-026b: HO-132 remediation round 3 — full suite green (215), cron installed, lost files restored
d061d7e F-026b: fix conftest imports, add dashboard+seed tests, add email reminder unit tests, HO-129 remediation
34c5352 F-026b: email reminder infrastructure — reminder_log, SMTP utility, cron script, admin endpoints, frontend
```

The F-026b work spans these **five** commits (the remaining 13 commits
`main..test` are pre-existing non-F-026b work on the branch: tutor-connect-hub,
F-027, F-TD-001, etc.).

**Commit-boundary reality (item 3's premise):** the three production bug
fixes were **bundled inside `03c9436`** (HO-132 round 3) alongside the
F-026b test-suite repair — not in a separate commit. This is the
"mixed into the same commit" case from HO-134, so I performed the manual
separation rather than opening a mis-scoped PR.

## 3. Production bug fixes — split out (as decided)

- **Bugfix branch** `bugfix/production-bugs-001` created from `main`:
  commit `7fc846d` contains exactly the three bug hunks + a dedicated
  regression test file (`backend/tests/integration/test_bugfix_regressions.py`).
  - **PR #8**: https://github.com/tikeazubike-lab/openagile_2/pull/8
  - Commit message references the BUG-IDs.
  - Regression tests proved **RED without the fixes** (DataError /
    AttributeError on all 6) and **GREEN with them** — carried on the
    bugfix branch, not left with F-026b.
- **F-026b branch** (`test`) — the bug hunks were **reverted** and the
  bug-proving tests **removed** (they moved to the bugfix PR). New commit
  `ef6adc3` on `test`. F-026b suite is green at **207 passed** (was 215)
  without the prod fixes, so the F-026b PR is reviewable as scoped.

| BUG-ID | Fix | Regression test (bugfix branch) |
|---|---|---|
| BUG-TZ-NAIVE-001 | naive UTC at 4 call sites (auth, holding, registrar, user soft-delete) | change-password, holding/registrar/user soft-delete |
| BUG-HOLDING-STATUS-001 | `update_holding` status → `holding_type` | PATCH holding |
| BUG-PDF-UPLOAD-500-001 | upload-pdf → 422 not 500 | fake-PDF upload |

## 4. Incident discovered during push — Mailgun API key in `.env.v3`

Pushing `test` was **blocked by GitHub push protection**:

```
remote: - Push cannot contain secrets
remote:   ——— Mailgun API Key ———
remote:   locations:
remote:     - commit: 345c194c650b485b3435f59b5c03ccc4d168ce08
remote:       path: .../.env.v3:13
```

**Root cause:** commit `345c194` (F-026b email-reminder infrastructure)
added an SMTP block to the tracked `.env.v3`, with `SMTP_PASSWORD` set to a
Mailgun API key (`key-…`). This was local-only — never pushed — but GitHub
scans the full push and flagged it. The key was already rotated/revoked per
HO-128, but a dead secret in history still blocks the push.

**Resolution:** rewrote the five local F-026b commits with
`git filter-branch` to redact the value to
`SMTP_PASSWORD=REDACTED_rotated_2026-08-19`, then re-verified the suite
(207 passed), and pushed. **All five commit SHAs changed** — remap:

| Old SHA | New SHA |
|---|---|
| `345c194c650b…` | `34c5352` |
| `c67dd9386c39…` | `d061d7e` |
| `03c9436` | `c6e3800` |
| `42a5405` | `76b80db` |
| `4592c43` | `ef6adc3` |

`origin/test` is now at `ef6adc3` (pushed clean, fast-forward from
`ee8f14d`). Handover references to the old SHAs (HO-132/HO-133) should use
the remapped values.

**Follow-up recommendation (not done — needs a decision):** `.env.v3` is a
tracked file full of live secrets (`JWT_SECRET`, `DATABASE_URL` password,
`EPM_ADMIN_PASSWORD`, the rotated `SMTP_PASSWORD`). Recommend untracking it
(`git rm --cached`) + adding to `.gitignore`, and loading it only via the
deployment env path. This would prevent any recurrence of committed-secret
blocks.

## Current state

- `test` pushed: `ee8f14d..ef6adc3` (F-026b scope, 207 passed, no prod-fix hunks).
- `bugfix/production-bugs-001` pushed, **PR #8 open** (bug fixes + regression tests).
- F-026b PR (`test → main`) is the next step — note it will include the
  other pre-existing commits already on `test`; if a tighter F-026b-only PR
  is wanted, say so and I'll cut a `feature/f-026b` branch from `main` and
  cherry-pick the five commits.

## Requested response

None pending — this closes HO-134's three items. F-026b is ready for PR +
Gate 2 (subject to the F-026b PR base decision above).