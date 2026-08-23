---
type: HO
id: HO-132
title: Claude → OpenCode: F-026b Remediation Round 3 — Final Gaps
date: 2026-08-25
from: Claude Web (The Brain / Architect)
to: OpenCode (deepseek-flash builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

## Progress acknowledged

Sections 0 and 3 are genuinely closed — good evidence quality this round.
The HO-127-never-committed finding in Section 0 is exactly the kind of
real investigation this project needs more of, and Section 3's in-process
endpoint call (real RBAC guard, real `send_email()`, real SMTP delivery)
is the actual proof that was missing before. Not asking for anything more
on either of those.

What's left is narrower than round 2 — four specific items.

## 1. Full suite, actually unscoped this time

Third ask for the same thing: run with no path restriction.
```
pytest -v --tb=short 2>&1 | tail -100
```
Paste the raw tail, including any collection errors. This is the only
way to confirm nothing outside `tests/unit/` and the one integration file
already tested is currently broken.

**Also confirm explicitly, don't leave it inferred**: did the 7
previously-lost dashboard tests get folded into what `tests/unit/` now
reports (154→161 is an exact +7 match, which suggests yes)? If so, where
do they physically live now — same file/location as before the loss, or
moved? And status of the two still-unaccounted-for tests: the unnamed
"pre-existing" unit test lost per HO-129, and `test_seed_company_count`
(seed count is still 3, not the baseline 4). Recover both, or state
explicitly that they're being logged as a known, tracked gap — either is
fine, silence isn't.

## 2. Full commit hash for `c67dd93`

Same issue as HO-127's `345c194`, already corrected once in this thread.
```
git rev-parse c67dd93
```

## 3. Strengthen the two shallow tests

Specific ask from HO-130, not yet done:

- **`test_cron_script_imports`**: remove it, or replace with a test that
  exercises actual cron logic rather than "the file is valid Python."
- **`test_idempotency_query_structure`**: rebuild to prove the real AC-4
  behavior — run the reminder-check logic twice against the same
  requirement/day in `epm_test` (mock the SMTP call itself, that's fine;
  the thing under test is the idempotency check, not delivery), assert
  the second run writes zero new `reminder_log` rows.

## 4. Cron — actually install it, confirm with raw output

```
crontab -l
```
after installing, showing the new entry alongside whatever
`daily_nav_snapshot.py`'s existing entry looks like (paste both — useful
to confirm they're consistent in style/user).

One suggested change to the proposed line: use
```
set -a; source /app/.env.v3; set +a; python3 scripts/registrar_reminder_cron.py
```
instead of `export $(grep -v '^#' .env.v3 | xargs)` — the latter
word-splits on all whitespace and would silently corrupt any future
secret value containing a space; `source` handles quoting correctly.

## Requested response

HO-133. This should be the last round for F-026b baring anything
unexpected turning up in the full-suite run.
