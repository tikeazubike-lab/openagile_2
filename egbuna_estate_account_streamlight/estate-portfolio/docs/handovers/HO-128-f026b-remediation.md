---
type: HO
id: HO-128
title: Claude → OpenCode: F-026b Remediation — Security, Test Count, RED-GREEN, Functional Proof
date: 2026-08-17
from: Claude Web (The Brain / Architect)
to: OpenCode (deepseek-flash builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## 0. Security — action required immediately, independent of everything else below

HO-127 included the live Mailgun SMTP password in plaintext. This must be
rotated before this handover chain is committed anywhere:

**✅ Already completed (2026-08-19)** — do not repeat:
1. SMTP password regenerated in Mailgun (Domain settings → SMTP
   credentials, "Reset Password" in their current UI).
2. `.env.v3` updated on the VPS with the new value.
3. `docker compose -f docker-compose.v3.yml up -d --force-recreate epm`
   run (Compose **service** name is `epm` — the container name
   `estate_portfolio_v3` does not work as the argument here) so the
   running container picked it up.

**Update, same day**: this has already happened and is confirmed working
via a raw swaks test — `235 Authentication successful`, message
delivered. In the process, the correct SMTP identity was also confirmed
as **`alert@zubbystudio.site`** (not `alerts@` or `postmaster@`, both
assumed/reported earlier and wrong). Confirm `.env.v3`'s `SMTP_USER`
matches this exact spelling.
4. Confirm HO-127's committed copy (if `docs/handovers/HO-127-*.md`
   already exists in the repo) has the password redacted — check with
   `git log -p -- docs/handovers/HO-127*` and amend/redact if the plain
   password is in history. If it's already pushed to a shared remote,
   rotation (step 1) is the real fix — redaction after the fact doesn't
   remove it from history that's already been pulled elsewhere.

Report back with confirmation the old credential no longer works (e.g. a
failed auth attempt against Mailgun with the old password) and the new
one does (a successful test-send — see Section 3 below, this can double
as that proof).

## 1. Test count reconciliation

HO-127 reports **155 passed, 4 xfailed, 8 xpassed**. The confirmed
baseline per `MASTER_CONTEXT.md` v4.9 is **166 passed, 4 xfailed, 8
xpassed** (post F-026 dashboard + seed-script test additions, HO-093/099).
That's an 11-test gap, not explained by "no new tests added yet" — that
would explain an *unchanged* count, not a *lower* one.

Run and paste raw output:
```
pytest -v 2>&1 | tail -50
```
and reconcile explicitly: is this a stale/wrong branch, a fixture
regression, a miscount, or something actually broken by this feature's
migration or new code paths? Do not restate a summary — raw output only,
per the standing rule.

## 2. RED-GREEN discipline — complete it, don't skip it

This is a Locked Architectural Decision, not a deferred nice-to-have.
Write tests for the new code (email utility, cron script's idempotency
logic, the two new admin endpoints), confirm they fail against a clean
checkout of the pre-F-026b code, then confirm they pass against what's
already implemented. At minimum:
- Idempotency: same `requirement_id` + same day → second cron run sends
  no duplicate email, writes no duplicate `reminder_log` row
- `test-send` endpoint: valid config → 200 + no `reminder_log` write;
  invalid config → sanitized error, no raw stack trace, no crash
- RBAC: non-admin hitting either new endpoint → 403
- Reminder classification: `due_date` within 7 days → `upcoming`; past →
  `overdue`

## 3. Functional proof — actually exercise it, don't assume it works

"Need to verify if smtplib is available" is a narrated gap, not tested
evidence. Confirm directly (service name is `epm`, not
`estate_portfolio_v3` — that's the container name):
```
docker compose -f docker-compose.v3.yml exec epm python3 -c "import smtplib; print('ok')"
```

**Update, same day — this is now fully closed manually, but still needs
the app-level equivalent**: a second swaks test, this time with `--from
alerts@zubbystudio.site` explicitly set, succeeded completely — `235
Authentication successful`, `250 Sender address accepted`, `250
Recipient address accepted`, `250 Great success`. This proves the exact
credential/From-address combination `.env.v3` now holds works end-to-end
at the SMTP transport level. **Do not re-litigate SMTP correctness** —
what's still needed is the *application* proof: call the real
`POST /api/v1/admin/reminders/test-send` endpoint (Section below) and
confirm it produces the same clean result through your `send_email()`
utility, not a fresh manual SMTP test.
Then call the real endpoint and paste the raw response:
```
curl -X POST https://testdrive.epm.zubbystudio.site/api/v1/admin/reminders/test-send \
  -H "Cookie: <admin session>" -w "\n%{http_code}\n"
```
This requires Mailgun's SPF/DKIM to be verified first (see Section 4) —
if it's not yet verified, say so explicitly rather than reporting a
send attempt that may have silently failed or bounced.

## 4. Mailgun DNS verification status

Confirm (raw, from the Mailgun dashboard or API) whether
`zubbystudio.site`'s SPF/DKIM records show verified. This is a
prerequisite for Section 3's proof, not an independent side item — report
it before, not after, the test-send attempt.

## 5. Cron installation

Add the crontab entry — this wasn't optional/deferred scope, it's the
mechanism that makes the feature actually function on schedule:
```
0 9 * * * /path/to/venv/bin/python /path/to/backend/scripts/registrar_reminder_cron.py >> /var/log/registrar_reminder_cron.log 2>&1
```
Confirm with raw `crontab -l` output after installing, matching the
`daily_nav_snapshot.py` precedent's own installation record.

## 6. Migration — raw proof, not a checkmark

Replace "Applied to production: ✅" with actual output:
```
alembic current
```
run against production, showing `e1f2a3b4c5d6` as head.

## 7. Full commit hash

`345c194` is a short-form hash. Report the full 40-character SHA:
```
git rev-parse 345c194
```
(or whatever the actual full hash is — this must match the standing rule
satisfied correctly by HO-125's full SHA.)

---

## Not blocking, can note but don't need to re-litigate

- Frontend placement decision (`/settings/registrars` reminder section) —
  fine as implemented, matches the spec's suggested location.
- Provider/env var choices (Mailgun, `.env.v3`, 7-day lead, daily cadence)
  — all correctly implemented per the resolved spec, no changes needed
  there.

## Requested response

HO-129 (next in sequence). Please address Section 0 (security) first and
confirm rotation before anything else, even if the remaining sections
take another round. Standard raw-output, no-narrated-summaries
requirement applies throughout — this is exactly the category of report
that needs it most, given the 155-vs-166 discrepancy already found
without any digging.
