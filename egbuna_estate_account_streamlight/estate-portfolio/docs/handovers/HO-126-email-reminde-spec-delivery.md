---
type: HO
id: HO-126
title: Claude → OpenCode: F-026 Email Reminder Infrastructure — Spec Delivery
date: 2026-08-15
from: Claude Web (The Brain / Architect)
to: OpenCode (deepseek-flash builder)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

## Context

F-026's email reminder infrastructure (one of two deferred, explicitly
decoupled items from F-026's 2026-07-31 closure) is now prioritized.
Bulk import (`/settings/registrars` CSV/markdown) is queued next after
this, per one-feature-per-session discipline — do not start it in
parallel with this work.

## Zone 2 review status

**Waived** — Zubbyik explicitly waived DeepSeek Pro consensus review for
this spec, cost/token reasons, 2026-08-15. Claude Web is sole Zone 2
reviewer for this feature, same case-by-case pattern as F-022's backend.
This does not extend to bulk import — that waiver decision will be made
separately when that spec is delivered.

## Spec

Full spec attached: `F-026-email-reminder-infrastructure.md` — place at
`.context/feature-specs/F-026-email-reminder-infrastructure.md` on
commit.

Summary for quick reference:
- New `reminder_log` table (idempotency + audit)
- New env vars for SMTP config (secrets, not committed)
- Reusable email-sending utility (generic, not reminder-only)
- OS cron job following the `daily_nav_snapshot.py` pattern exactly —
  **do not use n8n**
- Two new admin-only endpoints: `POST /admin/reminders/test-send`,
  `GET /admin/reminders/log`
- Minimal frontend: reminder log view + test-send button under
  `/settings/registrars` (or a new `/settings/notifications` tab — your
  call, note which you chose and why in the implementation report)
- 8 acceptance criteria (AC-1 through AC-8) — see spec Section 6

## Before you start

**All four open questions are resolved (revised once, below) —
implementation is unblocked, no need to pause for clarification:**

- **Provider: Mailgun** (Zubbyik's existing free-tier account —
  supersedes the AWS SES option floated earlier in this thread; SES is
  no longer relevant to this feature). Talk to it over plain SMTP
  (`smtp.mailgun.org` or `smtp.eu.mailgun.org` — confirm which region the
  sending domain is registered under — port 587, STARTTLS) using
  Mailgun's SMTP username/password from the domain's SMTP credentials
  panel, **not** the Mailgun API key. Keeps the email utility itself
  provider-agnostic (plain `smtplib`/equivalent) — swapping providers
  later is an env-var change, not a code change.
- **No sandbox/recipient-verification step** — Mailgun's free plan sends
  to any recipient once the sending domain's SPF/DKIM records are
  verified. Simpler than the SES plan originally discussed.
- **Sender identity**: use the one custom sending domain the free plan
  allows — recommend `alerts@zubbystudio.site`. Zubbyik already controls
  that domain's DNS on Cloudflare, so adding Mailgun's verification
  records is straightforward. Flag if you go a different route and why.
- **100 emails/day, 1-day Mailgun-side log retention** are the free-tier
  limits — not a practical constraint at this feature's volume. Don't
  design around headroom that isn't needed; `reminder_log` in Postgres is
  this system's real durable audit trail, Mailgun's own dashboard logs
  are secondary.
- **Lead time: 7 days** (revised down from an initial 14-day default).
  **Cadence: daily. Recipient: `zubbyik@gmail.com`.**
- **Env file: `.env.v3`, not `.env`.** Confirmed via `grep -n "env_file"
  docker-compose.v3.yml` — `estate_portfolio_v3` loads `./.env.v3`. The
  repo root has both files; `.env` is not the one this container reads.
  Zubbyik has already appended the SMTP/Mailgun vars there manually and
  force-recreated the container, so the env vars should already be live
  by the time you start — confirm with `docker compose -f
  docker-compose.v3.yml exec estate_portfolio_v3 env | grep -E
  "SMTP_HOST|SMTP_USER|REMINDER"` rather than assuming, since a
  mismatch here fails silently (vars just don't reach the app, no error
  surfaced).

Updated spec attached (Section 3 and Section 8 both revised) — re-pull if
you already have an earlier version open, this is the second revision of
the provider decision.

## Standing rules (unchanged, restated for this handover)

- RED-GREEN: write test → confirm it fails → implement → confirm it
  passes
- One feature, one session, one commit — no mixing with bulk import
- Three-layer acceptance order: DB → API → UI
- Raw command output required for any claim about repo/file/test state —
  no narrated summaries
- Any code change is not complete until an actual commit hash is
  reported back
- Nothing merges to `main` without a PR + Gate 2 (Zubbyik's explicit
  review approval via required GitHub PR review)

## Requested response

Standard implementation report format. Please confirm OQ-F026-EMAIL-1
resolution (or your recommendation if you're proceeding with a
placeholder pending Zubbyik's answer) explicitly at the top of your
reply.
