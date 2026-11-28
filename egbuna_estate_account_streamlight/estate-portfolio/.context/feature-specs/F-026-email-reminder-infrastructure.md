# F-026b: Registrar Requirements Email Reminder Infrastructure

**Parent feature**: F-026 Registrar Requirements & Document Tracker (shipped 2026-07-31)
**Status**: Spec ready — pending implementation
**Location**: `.context/feature-specs/F-026-email-reminder-infrastructure.md`
**Author**: Claude Web (Zone 2 Architect)
**Zone 2 review**: **Waived** by Zubbyik for cost/token reasons (2026-08-15) — Claude Web sole reviewer, same case-by-case pattern as F-022's backend. Not a standing policy change.

---

## 1. Purpose

F-026 shipped a hybrid visual + email reminder design for registrar document
deadlines, but only the visual half went live — `registrar_requirements.due_date`
was added specifically to support both, and the dashboard already surfaces
overdue/upcoming items visually. The email half was deferred because no SMTP
capability exists anywhere in the codebase. This spec closes that gap: it adds
a minimal, reusable email-sending capability and a scheduled job that emails
Zubbyik when a registrar requirement is approaching or past its due date.

This is explicitly decoupled from F-026's other deferred item (`/settings/registrars`
bulk import) — no shared code, no sequencing dependency between them.

## 2. Scope

### In scope
- SMTP configuration via environment variables (secrets, not committed)
- A reusable backend email-sending utility (`app/services/email.py` or
  equivalent) — written generically enough that future features needing
  email (not just this one) can reuse it, rather than a single-purpose
  reminder-only function
- A scheduled job following the **F-007 daily-cron precedent** (OS cron,
  not n8n — n8n was rejected on direct operator experience, standing
  decision) that scans `registrar_requirements.due_date` and sends
  reminder emails for upcoming and overdue items
- Idempotency: at most one reminder email per requirement per calendar day,
  regardless of cron run frequency
- A `reminder_log` table for audit trail and duplicate-send prevention
- An `admin_audit` entry per automated send, `performed_by=NULL` — same
  pattern already established for F-007's cron script
- A minimal admin-only "send test email" endpoint, so SMTP config can be
  validated live without waiting for the next cron cycle or SSH-ing into
  logs
- A minimal admin-only reminder log view, for troubleshooting

### Out of scope
- Per-user notification preferences or multi-recipient routing — this is
  a single-owner estate model (confirmed during F-022 RBAC review); one
  fixed recipient is sufficient
- In-app notification bell integration (`BUG-DASH-NOTIFY-001` is a
  separate, already-tracked item — not touched here)
- Retry queues / dead-letter handling beyond logging a failed send —
  defer any delivery-hardening work to a future pass if failures turn
  out to be a real problem in practice
- Email template localization
- Any change to `/settings/registrars` bulk import (F-026's other
  deferred item — explicitly decoupled)

## 3. Data Model

### New table: `reminder_log`

```sql
CREATE TABLE reminder_log (
    id              SERIAL PRIMARY KEY,
    requirement_id  INTEGER NOT NULL REFERENCES registrar_requirements(id),
    reminder_type   VARCHAR(20) NOT NULL CHECK (reminder_type IN ('upcoming', 'overdue')),
    recipient_email VARCHAR(255) NOT NULL,
    delivery_status VARCHAR(20) NOT NULL CHECK (delivery_status IN ('sent', 'failed')),
    error_detail    TEXT NULL,
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reminder_log_requirement_date
    ON reminder_log (requirement_id, (sent_at::date));
```

The composite index backs the idempotency check (`requirement_id` + today's
date → already sent?) without a full table scan.

### No changes to `registrar_requirements`

`due_date` already exists (F-026, Locked Architectural Decisions). No new
columns needed on the parent table.

### New environment variables (secrets — not committed, VPS `.env` only)

**Provider resolved: Mailgun** (existing free-tier account — see
OQ-F026-EMAIL-1 resolution below). Mailgun exposes a standard SMTP relay
alongside its REST API; the reusable email utility (Section 1) talks
plain SMTP-over-TLS, keeping it provider-agnostic — swapping providers
later means changing four env vars, not application code.

**Confirmed deployment target (2026-08-15, via `grep -n "env_file" docker-compose.v3.yml`)**:
`estate_portfolio_v3` loads `./.env.v3`, **not** `./.env` — the repo root
has both, `.env.v3` is the live one for this container. New vars below go
into `.env.v3`. Container must be recreated after editing (`docker
compose -f docker-compose.v3.yml up -d --force-recreate
estate_portfolio_v3`) — Compose only reads `env_file` at container
creation, not on file edit.

```
SMTP_HOST=smtp.mailgun.org                     # or smtp.eu.mailgun.org — confirm region when generating SMTP credentials
SMTP_PORT=587                                  # STARTTLS
SMTP_USER=postmaster@zubbystudio.site          # Mailgun's default SMTP login for the domain
SMTP_PASSWORD=                                 # Mailgun SMTP password (domain settings → SMTP credentials, distinct from the API key)
SMTP_FROM_ADDRESS=alerts@zubbystudio.site      # on the one custom sending domain the free plan allows
REMINDER_RECIPIENT_EMAIL=zubbyik@gmail.com     # confirmed
REMINDER_LEAD_DAYS=7                           # confirmed default
```

**No sandbox/recipient-verification step required** — unlike SES,
Mailgun's free tier sends to any recipient once the sending domain is
verified (SPF/DKIM records added). Simpler setup than the earlier SES
plan, and no ongoing per-email cost to reason about at this volume.

**Known free-tier ceiling, noted not designed around**: 100 emails/day,
1-day Mailgun-side log retention. At this feature's volume (a handful of
reminders across a handful of registrar requirements) 100/day is not a
realistic constraint. The 1-day Mailgun log retention doesn't matter for
this feature specifically since `reminder_log` (Section 3 above) is this
system's own durable audit trail in Postgres — Mailgun's dashboard logs
are a secondary debugging aid only, not depended on.

## 4. API Contract

### `POST /api/v1/admin/reminders/test-send`
- **Auth**: `ADMIN_ROLES` only (reuses existing `app/deps.py` constant)
- **Request body**: none
- **Response 200**:
  ```json
  { "status": "sent", "recipient": "zubbyik@gmail.com" }
  ```
- **Response 502** (SMTP config invalid or send failed):
  ```json
  { "status": "failed", "detail": "<sanitized error, no raw stack trace>" }
  ```
- Does **not** write to `reminder_log` — this is a config-validation tool,
  not a real reminder, and must not pollute the audit trail or affect
  idempotency for actual requirement reminders.

### `GET /api/v1/admin/reminders/log`
- **Auth**: `ADMIN_ROLES` only
- **Query params**: `page`, `page_size` (standard pagination convention,
  matching F-026's `global-tracker` endpoint)
- **Response 200**: paginated `reminder_log` rows, each including the
  joined `registrar_requirements` description for readability

No changes to any existing `registrar_requirements` or `company_registrars`
endpoints.

## 5. Frontend Requirements

Minimal — this is primarily a backend/cron feature:

- A small section on `/settings/registrars` (or a new `/settings/notifications`
  tab if that reads cleaner — builder's call, flag the choice in the
  implementation report) showing:
  - Recent `reminder_log` entries (last 20, paginated)
  - A "Send test email" button wired to `POST /admin/reminders/test-send`,
    showing the raw success/failure response inline
- No dashboard (`/registrars`) changes — the visual half of the hybrid
  reminder already shipped in F-026; this is purely the email delivery
  layer underneath it
- Modal-based, no inline editing (standard project convention — N/A here
  since there's no CRUD, but noting for completeness)

## 6. Acceptance Criteria

| AC | Given | When | Then |
|----|-------|------|------|
| AC-1 | SMTP config missing or invalid | Cron job runs | Job logs the error, does not crash, sends nothing |
| AC-2 | A requirement's `due_date` falls within `REMINDER_LEAD_DAYS` | Cron runs | Exactly one email sent, one `reminder_log` row with `reminder_type='upcoming'` |
| AC-3 | A requirement's `due_date` has already passed | Cron runs | One email sent, `reminder_type='overdue'` |
| AC-4 | A requirement already has a `reminder_log` row for today | Cron runs again same day | No duplicate email sent — idempotency check blocks it |
| AC-5 | Admin calls `POST /admin/reminders/test-send` with valid SMTP config | — | Test email delivered, 200 returned, no `reminder_log` row written |
| AC-6 | Admin calls `POST /admin/reminders/test-send` with invalid SMTP config | — | Sanitized error returned (502), no crash, no raw stack trace exposed |
| AC-7 | Cron sends any reminder email | — | A corresponding `admin_audit` row is written with `performed_by=NULL` (F-007 cron pattern) |
| AC-8 | Non-admin user calls either new endpoint | — | 403, consistent with existing `ADMIN_ROLES` enforcement elsewhere |

## 7. Dependencies

- `registrar_requirements.due_date` — already shipped (F-026)
- `admin_audit.performed_by` nullable — already shipped (F-007, HO-066)
- OS cron scheduling pattern — reuse `daily_nav_snapshot.py`'s approach
  directly (same script structure, same crontab mechanism); **do not use
  n8n** (standing rejection, F-007)
- No new Postgres instance, no schema-swap testing pattern — standard
  project constraints apply

## 8. Open Questions — all resolved (2026-08-15, revised same day)

| ID | Question | Resolution |
|----|----------|------------|
| OQ-F026-EMAIL-1 | SMTP provider? | **Mailgun** — Zubbyik already holds a free-tier account (100 emails/day, SMTP relay + REST API, 1 custom sending domain, ticket support). No new signup, no sandbox/recipient-verification step required (unlike the AWS SES option initially considered) — just domain SPF/DKIM verification on the existing sending domain. Rejected SendGrid (permanent free plan discontinued, now a 60-day trial only) and initially considered AWS SES sandbox mode, superseded once the existing Mailgun account made it the simpler choice |
| OQ-F026-EMAIL-2 | Lead time right? | **Confirmed — 7 days** (revised from an initial 14-day default) |
| OQ-F026-EMAIL-3 | Daily cron cadence sufficient? | **Confirmed — daily**, matching the F-007 NAV snapshot pattern |
| OQ-F026-EMAIL-4 | Recipient address? | **Confirmed — `zubbyik@gmail.com`** |

No open questions remain. Implementation is unblocked.
