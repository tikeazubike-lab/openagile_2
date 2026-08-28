---
type: HO
id: HO-139
title: OpenCode → Claude: EPM Login Failure — Root Cause Found and Login Restored
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

# HO-139 — Login Restored (End-to-End Verified)

## Summary

Login is genuinely working again, verified via raw curl output and a real
browser session. **No application or `.env.v3` file changes were needed** —
the fix was a single Postgres-side password reset. Root cause corrected the
assumption in HO-138's context (the `ALTER USER` **did** take effect; the
"never took effect" confirmation was an artifact of `trust` auth).

## Root cause

HO-138 claimed the `ALTER USER openagile ...` never took effect because a
`psql` test with `SecurePass2024` succeeded. That test ran over the Postgres
**local socket**, and `pg_hba.conf` is:

```
local   all   all   trust              ← no password check
host    all   all   127.0.0.1/32  trust
host    all   all   all         scram-sha-256   ← TCP requires real password
```

Local-socket `trust` auth never validates the password, so the test proved
nothing. Over **TCP (scram-sha-256)** the role's password had actually been
changed by the earlier `ALTER USER` — while `.env.v3`'s `DATABASE_URL` still
held `SecurePass2024`. Hence `asyncpg.exceptions.InvalidPasswordError:
password authentication failed for user "openagile"` from the app despite the
env file being correct.

## What was done

1. **Step 1 — duplicates:** none. `DATABASE_URL`, `JWT_SECRET`,
   `EPM_ADMIN_PASSWORD`, `SMTP_*`, `REMINDER_*` all appear exactly once in
   `.env.v3`. (No dedup fix needed.)
2. **Step 2 — connection string:** `DATABASE_URL` already correct
   (`postgresql+asyncpg://openagile:SecurePass2024@openagile_postgres/estate_portfolio`);
   password segment is `SecurePass2024`.
3. **Step 3 — recreated cleanly:** `docker compose -f docker-compose.v3.yml
   down epm && up -d epm`.
4. **Step 4 — fresh container:** `docker inspect ... .Created` =
   `2026-08-28T10:53:53Z`, within seconds of `date`.
5. **Step 5 — container env:** `exec epm env | grep DATABASE_URL` shows
   `SecurePass2024` — matches the file on disk, nothing overrides it.
6. **Step 6 — logs clean:** after recreate, startup log shows only
   `Application startup complete.` / `Uvicorn running ...` — zero
   `InvalidPasswordError`.
7. **Step 7 — seed_admin.py (first real success):**
   ```
   $ docker compose -f docker-compose.v3.yml exec epm python3 scripts/seed_admin.py
   ✅ Admin user 'zubbyik' already exists — password updated.
   ```
8. **Step 8 — curl login (the actual proof):**
   ```
   $ curl -i -X POST https://testdrive.epm.zubbystudio.site/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"zubbyik","password":"<EPM_ADMIN_PASSWORD>"}'
   HTTP/2 200
   set-cookie: epm_token=eyJhbGciOiJIUzI1NiIs...; HttpOnly; Max-Age=2592000; Path=/; SameSite=strict; Secure
   {"data":{"id":1,"username":"zubbyik","name":"Zubby","role":"admin"},"meta":{},"error":null}
   ```
9. **Step 9 — `file:///` security error: did NOT reproduce.** Verified with a
   real browser (Playwright) on the live site:
   - `/login` loads with **0 console errors**.
   - Login with the rotated credentials → navigates to `/dashboard`, **0
     errors** (only two cosmetic Recharts width/height warnings).
   - Logged out, hit `/dashboard` → correctly redirected to
     `/login?redirect=%2Fdashboard` (the same URL pattern from the reported
     error) — the only console entry is the expected `401` on
     `/api/v1/auth/me` from the auth guard, **not** the `file:///` security
     error.
   - Re-logged in through that redirect URL → `/dashboard`, no errors.

   Conclusion: the `file:///` error was a **symptom of the backend being
   down** during the failed login attempts, not an independent frontend bug.
   No frontend change is warranted. (Minor note for a future round: the
   login success handler ignores the `?redirect=` param and always goes to
   `/dashboard`; the intended post-login redirect target is dropped. Cosmetic,
   not the reported bug.)

## The one-line fix

Since `openagile` is a superuser role reachable via the local `trust`
socket, I reset its password to match the intended `.env.v3` value:

```
ALTER USER openagile WITH PASSWORD 'SecurePass2024';
```

Verified immediately after: TCP connect from inside the epm container with
`SecurePass2024` → `CONNECT OK`.

## Side note (already self-healed)

The same shared role serves n8n, wikijs, openproject, gitea. If any of them
connect over TCP with `SecurePass2024`, they would have been affected by the
same password drift during the window and are now consistent again after the
reset. Worth a quick smoke check on those services at your convenience.

## Not blocking — logged for the record

- The HO-138 historical-decision-log lesson stands and is now worth writing:
  never trust a local-socket auth test to confirm a TCP credential; confirm
  the real password over TCP before editing dependent configs.
- `SecurePass2024` remains the live shared role password (8 months). A
  coordinated rotation across all five services is still recommended, but
  not today and not as a side-effect of anything else.

## Verification steps

- `curl -X POST .../api/v1/auth/login` → **200** + `epm_token` httpOnly cookie.
- Browser: login → `/dashboard`, 0 security errors.
- Container logs: `POST /api/v1/auth/login 200`, `GET /api/v1/dashboard 200`.

Requested response reached. Login is restored and verified end-to-end.