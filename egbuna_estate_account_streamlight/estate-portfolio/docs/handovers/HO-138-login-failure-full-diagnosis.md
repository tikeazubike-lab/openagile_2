---
type: HO
id: HO-138
title: Claude → OpenCode: EPM Login Failure — Full Autonomous Diagnosis and Fix
date: 2026-08-23
from: Claude Web (The Brain / Architect)
to: OpenCode (deepseek-flash builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Purpose of this handover

This supersedes HO-137. Work through this entire checklist autonomously,
applying fixes as you find issues, and **do not stop to ask for
confirmation between steps** — only report back once login is genuinely
verified working end-to-end, or if you hit Step 10's stop condition.
Minimize round trips; Zubbyik has already spent significant time on
manual back-and-forth debugging this and needs it resolved in one pass.

## Context — condensed history, so you don't need to ask for it

During F-026b's security remediation, Zubbyik rotated three credentials
in `estate-portfolio/.env.v3`: `DATABASE_URL`'s password, `JWT_SECRET`,
and `EPM_ADMIN_PASSWORD`. The `ALTER USER` attempt against the shared
Postgres role `openagile` **never actually took effect** — confirmed via
a direct TCP-forced `psql` test that Postgres's real current password for
that role is still `SecurePass2024` (the original value, from
`~/openagile/.env`, `POSTGRES_PASSWORD=SecurePass2024`). This role is
shared across five services via `POSTGRES_MULTIPLE_DATABASES`: n8n,
wikijs, openproject, gitea, estate_portfolio — none of them are believed
affected, since the real password never changed.

Zubbyik attempted a `sed` fix to restore `SecurePass2024` into
`.env.v3`'s `DATABASE_URL`, then force-recreated the `epm` service — but
`docker compose logs epm` still shows the same
`asyncpg.exceptions.InvalidPasswordError: password authentication failed
for user "openagile"` afterward. This has not been root-caused yet.

Separately: `seed_admin.py` has never successfully run this entire
session, since it needs DB access, which has been broken throughout. The
new `EPM_ADMIN_PASSWORD` value has never actually been written to the
`users` table.

Separately again: after one login attempt, the browser console showed
`Security Error: Content at https://testdrive.epm.zubbystudio.site/login?redirect=%2F
may not load or link to file:///.` — unclear if this is a symptom of the
backend failure or an independent frontend bug. **Do not investigate this
until Step 9** — fixing it blind before the backend is confirmed working
risks chasing a symptom.

## Step 1 — check for duplicate/stray env entries first

`.env.v3` has been manually edited many times this session (SMTP vars
appended, JWT_SECRET changed, admin password changed, a DB-password
revert attempted). Before assuming the `sed` fix failed for some subtle
reason, rule out the simple explanation:

```bash
grep -n DATABASE_URL .env.v3
grep -c DATABASE_URL .env.v3
```

If the count is more than 1, that's very likely the actual bug — a
duplicate line from an earlier append could be the one actually taking
effect, depending on how the app loads the file. If found, **delete the
stale duplicate(s) entirely**, leaving exactly one correct line.

While you're in there, run the same check for the other recently-touched
keys, since the same duplication risk applies to all of them:
```bash
for key in JWT_SECRET EPM_ADMIN_PASSWORD SMTP_HOST SMTP_USER SMTP_PASSWORD SMTP_FROM_ADDRESS REMINDER_RECIPIENT_EMAIL REMINDER_LEAD_DAYS; do
  echo "$key: $(grep -c "^$key=" .env.v3)"
done
```
Fix any count greater than 1 the same way — keep the correct value, delete duplicates.

## Step 2 — confirm the correct full connection string

Don't assume host/port/dbname are unchanged — confirm what they should
be (check `git diff`/`git log -p -- .env.v3` if a prior committed version
exists, or the container's other config) before reconstructing the line.
The password segment specifically must be exactly `SecurePass2024`.

## Step 3 — recreate cleanly

```bash
docker compose -f docker-compose.v3.yml down epm
docker compose -f docker-compose.v3.yml up -d epm
```
Using `down` then `up` rather than `--force-recreate` this time, to rule
out any stale-process edge case with the recreate flag itself.

## Step 4 — confirm the container is actually fresh

```bash
docker inspect estate_portfolio_v3 --format='{{.Created}}'
date
```
Timestamps should be within seconds/minutes of each other. If not, the
recreate didn't actually happen and something is blocking it — investigate
that before proceeding further.

## Step 5 — confirm the running container sees the correct value

```bash
docker compose -f docker-compose.v3.yml exec epm env | grep DATABASE_URL
```
Must show `SecurePass2024` in the password segment. If it doesn't match
what's in the file on disk, something is overriding it (a parent shell
env var, a different `env_file` actually in effect, etc.) — find out
what and report it even if you also fix it.

## Step 6 — confirm logs are clean

```bash
docker compose -f docker-compose.v3.yml logs epm --tail=50
```
Zero `InvalidPasswordError` entries in the fresh log output.

## Step 7 — run seed_admin.py for real

```bash
docker compose -f docker-compose.v3.yml exec epm python3 scripts/seed_admin.py
```
Paste full raw output — this has never actually succeeded yet.

## Step 8 — verify login via curl, not just the browser

Confirm the actual login endpoint path/payload shape from the router
code first if this is wrong:
```bash
curl -i -X POST https://testdrive.epm.zubbystudio.site/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<admin-username>","password":"<new-EPM_ADMIN_PASSWORD>"}'
```
Paste the raw status code and response body. This is the actual proof —
not a screenshot, not "it should work now."

## Step 9 — only now, investigate the frontend file:/// error

If Step 8 confirms a working login (200 + valid token/session) but the
browser still shows the `file:///` security error, this confirms it's a
frontend-only bug independent of the backend fix. Look for redirect logic
in the login success handler — a common cause is a redirect target built
from an empty/undefined value (e.g. `window.location.href = something`
where `something` resolves to an empty string, which some browsers
interpret relative to `file://`). Fix it, or if it needs a design
decision, report the exact code location and stop there.

## Step 10 — stop condition

If Step 8's curl call still fails after Steps 1-7 are all confirmed
clean (no duplicates, fresh container, correct env var loaded, clean
logs, seed_admin.py succeeded) — **stop, do not keep guessing**. Report
back with: the full (secrets redacted) `.env.v3` dump, full container
logs, and the exact curl response. Further blind fixes at that point risk
making it worse rather than better.

## Not blocking — log for the record, address later

- `SecurePass2024` is a placeholder-looking value that's been live for 8
  months across five services. Worth a genuine, coordinated rotation
  across all five at some point — not urgent, not today, not as a
  side-effect of anything else.
- This incident (multiple rounds of login failure across several hours)
  is worth a brief entry in the historical decision log once resolved.
  Lessons worth capturing: never edit dependent configs before confirming
  an `ALTER USER` (or equivalent) actually took effect; keep the old
  secret value until the new one is confirmed working end-to-end, not
  just set; `.env` files accumulate duplicate keys under repeated manual
  editing and are worth a periodic dedup check.

## Requested response

HO-139 — only once login is genuinely verified via Step 8's raw curl
output (and Step 9 if applicable), or immediately if Step 10's stop
condition is hit.
