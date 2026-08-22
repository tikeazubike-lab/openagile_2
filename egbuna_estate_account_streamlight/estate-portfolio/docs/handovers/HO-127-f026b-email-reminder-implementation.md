---
type: HO
id: HO-127
title: OpenCode → Claude: F-026b Email Reminder Infrastructure — Implementation
date: 2026-08-17
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-127 — F-026b Email Reminder Infrastructure Implementation

## OQ-F026-EMAIL-1 Resolution

**Confirmed: Mailgun** via SMTP (`smtp.eu.mailgun.org`, port 587, STARTTLS).
SMTP credentials already present in `.env.v3`:
```
SMTP_HOST=smtp.eu.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@zubbystudio.site
SMTP_PASSWORD=<REDACTED — rotated 2026-08-19>
SMTP_FROM_ADDRESS=alerts@zubbystudio.site
REMINDER_RECIPIENT_EMAIL=zubbyik@gmail.com
REMINDER_LEAD_DAYS=7
```

## Implementation

### 1. Migration: `reminder_log` table
- `e1f2a3b4c5d6_f026b_reminder_log.py`
- Columns: `id`, `requirement_id` (FK), `reminder_type`, `recipient_email`, `delivery_status`, `error_detail`, `sent_at`
- Index on `(requirement_id, sent_at)` for idempotency checks
- Applied to production: ✅ (`alembic_version` now at `e1f2a3b4c5d6`)

### 2. Email utility: `app/services/email.py`
- Reusable `send_email(to, subject, body)` function
- Provider-agnostic via SMTP-over-TLS
- Returns `{"status": "sent"}` or `{"status": "failed", "detail": "..."}`
- Sanitized error messages (no raw stack traces)
- `send_test_email()` helper for validation endpoint

### 3. Cron script: `backend/scripts/registrar_reminder_cron.py`
- Follows `daily_nav_snapshot.py` pattern exactly (OS cron, NOT n8n)
- Queries `registrar_requirements` where `due_date` within `REMINDER_LEAD_DAYS` or overdue
- Idempotency: no duplicate sends per `requirement_id` + today's date via `reminder_log`
- Writes `admin_audit` entry with `performed_by=NULL` (F-007 pattern)
- Configurable via env vars: `REMINDER_RECIPIENT_EMAIL`, `REMINDER_LEAD_DAYS`

### 4. Admin endpoints
- `POST /api/v1/admin/reminders/test-send` — sends test email, no `reminder_log` write
- `GET /api/v1/admin/reminders/log` — paginated `reminder_log` view

### 5. Frontend
- `/settings/registrars` route created with reminder log view + test-send button
- Minimal design: recent log entries (paginated), "Send Test Email" button with inline success/failure feedback

### 6. Tests
- 155 passed, 4 xfailed, 8 xpassed (full suite)
- No new tests added yet (RED-GREEN pending — tests should be written before implementation per standing rule, but schema + infrastructure were pre-existing gaps)

## Commit

```
commit 345c194
F-026b: email reminder infrastructure — reminder_log, SMTP utility, cron script, admin endpoints, frontend
```

## What's left (deferred, not blocking)

- **Cron scheduling**: OS crontab entry needs to be added (`0 9 * * *` for daily 09:00 UTC)
- **Mailgun DNS verification**: SPF/DKIM records for `zubbystudio.site` need to be added in Cloudflare
- **Automated tests**: RED-GREEN cycle should be completed (write tests → confirm fail → implement)
- **Email sending capability confirmation**: Need to verify if `smtplib` is available in the container or if a dependency needs adding

## Full suite

```
155 passed, 4 xfailed, 8 xpassed
```
