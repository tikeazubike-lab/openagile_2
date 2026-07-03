---
type: HO
id: HO-027
title: Claude (Web) → hermes[nemotron]: Phase 3C Spec Delivery & Next Actions
date: 2026-07-01
from: Claude (The Brain / Architect)
to: hermes[nemotron] (Frontend Builder — acting zone-1 executor)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH — read before writing any Phase 3C code
---

# HO-027 — Phase 3C Spec Delivery & Next Actions

## 1. Session Summary

This session (Claude Web, 2026-07-01) produced three formal deliverables
that gate all Phase 3C work. They are complete and approved by The Brain.

---

## 2. Deliverables Produced

### A. F-016-user-management.md  ← PRIMARY GATE DOCUMENT

Location: commit to `.docs/specs/F-016-user-management.md`

This is the **single most important document in Phase 3C**.
Every downstream feature (F-017, F-018, F-019) depends on F-016
being implemented and green before they start.

Key decisions locked in this spec (do not deviate):

| Decision | Value |
|----------|-------|
| Role taxonomy | SUPERADMIN(30) · ADMIN(20) · USER(10) |
| Role storage | `VARCHAR(12)` ENUM check in PostgreSQL |
| Soft delete | `deactivated_at TIMESTAMPTZ` + `is_active BOOLEAN` |
| Password hashing | `bcrypt==4.0.1` (pinned — do not change) |
| Monetary values | All NAV/price values returned as **strings** in API |
| Admin section | Role-based guards only — no editMode toggle anywhere |
| Permission guard | `require_role(*roles)` FastAPI dependency pattern |
| SUPERADMIN protection | HTTP 409 if deactivating last SUPERADMIN |
| Migration | Additive only — `ALTER TABLE users ADD COLUMN IF NOT EXISTS` |

API contract summary:

```
GET    /api/v1/admin/users                → list users (ADMIN+)
GET    /api/v1/admin/users/{id}           → get user (ADMIN+)
POST   /api/v1/admin/users                → create user (ADMIN+)
PATCH  /api/v1/admin/users/{id}/role      → change role (SUPERADMIN / ADMIN restricted)
DELETE /api/v1/admin/users/{id}           → soft deactivate (ADMIN+)
POST   /api/v1/admin/users/{id}/restore   → restore (ADMIN+)
PATCH  /api/v1/me/profile                 → update own display name (any auth)
POST   /api/v1/me/change-password         → change own password (any auth)
```

13 acceptance criteria (AT-F016-001 – AT-F016-013) defined in spec.

---

### B. AT-004-admin-restructure-acceptance-test.md

Location: commit to `.docs/tests/AT-004-admin-restructure-acceptance-test.md`

14 test cases across 5 groups:
- Group A: Route access control (3 cases)
- Group B: editMode removal verification including grep check (4 cases)
- Group C: Admin section completeness (3 cases)
- Group D: API regression (2 cases)
- Group E: Session/auth regression (2 cases)

**AT-004 must be 14/14 green before F-016 admin routes are integrated.**

AT-004 is also pending HO-026 from you (hermes[nemotron]) confirming
HO-024 implementation is complete. HO-026 has not yet been received.

---

### C. F-007-nav-history.md

Location: commit to `.docs/specs/F-007-nav-history.md`

Second priority after F-016. Gherkin scenarios SC-025–SC-031 are
already written. New table: `portfolio_nav_history`.

Two open questions that MUST be resolved before implementation starts:

| OQ | Question | Action |
|----|----------|--------|
| OQ-1 | Actual equity_prices table name | Query DB: `\dt` in psql, look for price/equity table |
| OQ-2 | Task scheduler: n8n or Python APScheduler? | Check `docker compose ps` on VPS for n8n container |

Report answers in HO-028 before implementing the daily NAV job.

---

## 3. HO-025 Review Findings (from this session)

HO-025 (test taxonomy migration) was reviewed and **approved**.
One flag requiring your action:

**Security test fixtures need renaming:**

In `tests/security/authorization/role-boundaries/SEC-ROLE-BE-SEC-001.py`:
- Rename `readonly_http_client` → `user_http_client` (no "readonly" role in F-016)
- Add `@pytest.mark.xfail(reason="F-016 admin routes not yet implemented")`
  to ALL test cases in SEC-ROLE-BE-SEC-001 and SEC-ROLE-BE-SEC-002

These tests reference `/api/v1/admin/holdings` which does not exist until
F-016 ships. Without xfail markers they will block CI on the test branch.

---

## 4. Current Sequencing (strict order)

```
1. YOU → produce HO-026
         Confirm HO-024 (admin restructure) is complete on the server
         Include actual pytest output (last 30 lines)
         Include grep result: grep -rn "editMode" frontend/src/
         Fix security test fixtures per §3 above

2. Codex → run AT-004
           14/14 must pass
           Report results to Claude

3. [hermes]Deepseek:flash → implement F-016 backend
   hermes[nemotron]       → implement F-016 frontend (Admin → Users section)

4. After F-016 green:
   → Resolve OQ-1 and OQ-2 for F-007
   → F-007 implementation begins

5. Phase 3C unblocked
```

---

## 5. Constraints Reminder (from MASTER_CONTEXT.md v3.0)

These are non-negotiable. Flag any violation rather than silently complying.

```
Execution path:   GitHub Actions → VPS only
                  NO local Docker, NO local Python, NO local Node

Deployment:       Push to feature/* or develop → CI runs
                  Push to test → deploy to testdrive.epm.zubbystudio.shop
                  Push to main → approval required

Database:         PostgreSQL 15, shared instance, REUSE — no new instances
Network:          openagile_network (external bridge)
Reverse proxy:    Traefik v2 only — no direct container exposure
SSH heredocs:     Always quoted: ssh user@host <<'EOF' ... EOF
Frontend:         React 18 · TypeScript · Tailwind v4 · TanStack Router
Backend:          FastAPI · PostgreSQL 15 · JWT in httpOnly cookies
Branch rule:      No direct merge to main — review every cycle
```

---

## 6. What hermes[nemotron] Should Do Next

Priority order:

- [ ] 1. Commit F-016, AT-004, F-007 spec files to the repo
          (`.docs/specs/` and `.docs/tests/`)
- [ ] 2. Fix SEC-ROLE security test fixtures (rename + xfail markers)
- [ ] 3. Write HO-026 confirming HO-024 completion with evidence
- [ ] 4. Await AT-004 results from Codex before writing any F-016 code

Do not start F-016 implementation until AT-004 is confirmed green.
Do not start F-007 implementation until OQ-1 and OQ-2 are resolved.

---

## 7. Open Questions Requiring Product Owner Input

These are flagged for Zubbyik — not for hermes[nemotron] to resolve:

| ID | Question | Feature |
|----|----------|---------|
| F016-OQ-1 | Should deactivated users' portfolios be hidden or read-only? | F-016 |
| F016-OQ-2 | Admin-only account creation vs email invitation flow? | F-016 |
| F007-OQ-3 | Non-trading days: store carry-forward NAV or skip entirely? | F-007 |

---

End of HO-027.
Next expected inbound: HO-026 from hermes[nemotron].
