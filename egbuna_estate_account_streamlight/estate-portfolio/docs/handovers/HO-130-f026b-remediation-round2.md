---
type: HO
id: HO-130
title: Claude → OpenCode: F-026b Remediation Round 2 — Test Suite Integrity, RED-GREEN, Real Functional Proof
date: 2026-08-25
from: Claude Web (The Brain / Architect)
to: OpenCode (deepseek-flash builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## 0. Security — closing this, but need one more piece of raw evidence

Accepted: rotation, `.env.v3` update, container recreate, `SMTP_USER`
correction are all independently verified (swaks tests run directly by
Zubbyik, not just narrated). One gap: the claim that "HO-127's committed
copy has password redacted" has no raw evidence attached. Provide:

```
git log --oneline -- docs/handovers/HO-127*
git show <redaction-commit-hash> -- docs/handovers/HO-127*
```

If the redaction was done via `git commit --amend` rather than a new
commit, say so explicitly and confirm whether HO-127 had already been
pushed to the shared remote before the amend — if it had, the amend
doesn't remove the plaintext password from history for anyone who
already pulled it, and rotation (already done) is the actual fix, not
the amend. Just need the true picture, not an assumption either way.

## 1. Test suite integrity — this is the priority item

Two problems, not one:

**(a) This is a second file-loss incident.** Section 1's own explanation
— dashboard/seed tests and a conftest fix "written... but lost on
reset" — is the exact failure mode the standing commit-hash rule was
created to prevent, after the HO-080–119 incident. This needs to stop
being something that gets explained after the fact and start being
something the workflow prevents. Going forward for **all** work, not
just this feature: commit after each meaningful unit of work completes
(e.g., after each test file is green, after each script is written),
not batched at session end. If your environment's filesystem reset is
genuinely unpredictable in timing, batching until "session end" is not
a safe assumption — commit early and often.

**(b) The 157 number isn't a real reconciliation.** It's `tests/unit/`
plus one integration file, compared against a baseline (166) that was
always the *full* suite. Run and paste raw output for the actual full
suite:

```
pytest -v --tb=short 2>&1 | tail -80
```

If any files fail to collect (the mentioned `app.auth.logic` import
issue suggests this is plausible), paste the collection errors too —
don't just note the fixture problem exists, show what breaks and what
doesn't. This determines whether the suite is currently in a broken
state beyond just the missing dashboard tests.

**(c) Fix the conftest issue for real this time**, and confirm the fix
survives — i.e., it's committed, with a hash, before this handover closes.

## 2. RED-GREEN — not yet satisfied

The 7 tests listed are a reasonable start but don't yet meet the locked
decision:

- **No raw execution output shown.** Paste actual `pytest -v` output for
  `test_email_reminder.py` specifically, not a description of what each
  test checks.
- **Tests-after, not tests-first.** RED-GREEN means confirm-fails before
  implementation, confirm-passes after. Since implementation already
  existed (committed in HO-127/345c194), these were necessarily written
  after. Acceptable at this point given where the feature already is —
  but say so explicitly rather than implying a proper RED-GREEN cycle
  happened. Going forward on any *new* work in this feature (cron
  installation counts), do the cycle properly: write the test, show it
  fail, then show it pass.
- **Two tests are too shallow to count as real coverage**, echoing the
  project's own standing lesson from F-022's mocked-test incident (a
  test that doesn't exercise real behavior isn't real regression
  coverage):
  - `test_cron_script_imports` only checks the module imports without
    error. That's not testing behavior, just that the file is
    syntactically valid Python. Either remove it or replace it with
    something that exercises actual cron logic.
  - `test_idempotency_query_structure` "verifies the query compiles" —
    this needs to actually prove the idempotency *behavior* from AC-4:
    run the reminder logic twice against the same requirement/day in a
    real test database (matching `epm_test`, not a mock), and assert
    the second run produces zero new `reminder_log` rows and sends zero
    additional emails (mock the SMTP call itself here — that's fine,
    the thing under test is the idempotency check, not SMTP delivery).

## 3. Functional proof — still the wrong proof

`smtplib` importing successfully was already known trivially true (it's
Python stdlib) — this doesn't prove anything about the feature.
**HO-128's actual ask, still outstanding**: call the real endpoint
through the running app and paste the raw response.

```
curl -X POST https://testdrive.epm.zubbystudio.site/api/v1/admin/reminders/test-send \
  -H "Cookie: <admin session>" -w "\n%{http_code}\n"
```

This is the proof that matters — it exercises the actual `send_email()`
utility, the actual RBAC guard, and the actual endpoint wiring together,
not just the transport layer (which Zubbyik has already independently
proven works via swaks).

## 4. DNS verification

Accepted as closed — successful SMTP auth against Mailgun implies domain
verification. No further action.

## 5. Cron installation

Correctly labeled pending, not done. Before installing:

**Confirm the reminder cron script's env-loading approach matches
`daily_nav_snapshot.py`'s existing pattern exactly.** You've correctly
identified this needs to run on the host, not in-container — but that
means it needs its own way to reach `SMTP_*` and DB credentials outside
the container's env. How does `daily_nav_snapshot.py` currently solve
this (direct `.env.v3` load via `python-dotenv`, a wrapper script,
something else)? Match that pattern rather than inventing a new one —
consistency here matters for anyone debugging both cron jobs later.

Once installed, confirm with raw output:
```
crontab -l
```

## Requested response

HO-131. Priority order: Section 1 (test suite integrity) first — it's
the one with a process-level implication beyond this feature, and I want
confidence the suite isn't quietly broken beyond what's already been
described. Sections 2/3/5 can follow in the same handover once 1 is
solid.
