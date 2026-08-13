# MASTER_CONTEXT.md — Single Source of Truth

**DO NOT EDIT WITHOUT HANDOVER PROTOCOL**

**Version**: 4.3
**Last Updated**: 2026-07-08
**Maintained By**: Claude Web (The Brain / Architect)
**Previous Version**: 4.2 (2026-07-06)

---

## ⚠️ Temporary Infrastructure Change (Active)

**Reason**: Developer workstation (Fedora 42 laptop) has crashed.
**Duration**: Temporary — reverts when workstation is restored. **Confirmed still active as of 2026-07-08** — not yet restored.
**Status**: Code remains committed to GitHub; project is intact and pullable.

### What changed (temporary only)

| Area | Normal state | Temporary state |
|------|-------------|-----------------|
| Docker commands | Forbidden on local machine — GitHub Actions only | Permitted — executed directly on Netcup VPS server via SSH |
| Local execution | No Docker, no Python, no Node on Fedora | All execution done on VPS directly |
| Deployment trigger | git push → GitHub Actions → VPS | Direct VPS execution permitted until workstation restored |

### What did NOT change

- Code is still committed and pushed to GitHub
- CI/CD pipeline (GitHub Actions) remains the canonical deployment path (design-only — see CI/CD section)
- All other infrastructure constraints remain in force
- This exception reverts automatically when the Fedora workstation is back — see "Workstation Restored" protocol below

---

## Current Infrastructure Contract

### Stack Overview

```yaml
Project: Estate Portfolio Manager v2 (EPM v2)
Type: FastAPI backend + React 18 SPA frontend

Base Platform: Docker Compose
Reverse Proxy: Traefik v2.10
Database: PostgreSQL 15 (shared instance — REUSE, never create another)
Network: openagile_network (external bridge)
Domain Pattern: *.zubbystudio.shop

Server Specs:
  OS: Ubuntu 24.04 LTS
  CPU: 8 vCPU
  RAM: 16GB
  Disk: 500GB SSD
  Location: Netcup VPS

Local Development (TEMPORARILY OFFLINE):
  OS: Fedora Linux 42 (Workstation Edition)
  Hostname: fedora (laptop)
  Hardware: Dell Latitude E6540
  Status: CRASHED — temporary direct-VPS execution permitted
  Normal rule: NEVER run Docker commands here — use GitHub Actions
```

### Active Services on VPS

```yaml
Infrastructure:
  - traefik (routing + SSL via Let's Encrypt)
  - postgres (PostgreSQL 15 — shared, single instance)
  - prometheus (metrics)
  - grafana (dashboards)

Production Apps:
  - estate-portfolio-manager (EPM v2 — FastAPI + React 18)
      Staging:   testdrive.epm.zubbystudio.shop
      Testbuild: testbuild.zubbystudio.shop (pending teardown — F-TD-001)
      ⚠️ Container naming chain (resolved 2026-07-06):
        Both hostnames currently point to the SAME running container ("_v3"):
          - _v3 = a fork of the old demo.estate container, running as temporary staging
          - testdrive.epm.zubbystudio.shop = Traefik alias to _v3
          - testbuild.zubbystudio.shop = nginx checklist page + API reverse-proxy,
            also forwarding to _v3
        This means both URLs currently serve identical backend state. F-TD-001
        (teardown) removes the testbuild nginx/proxy layer, not the _v3 container itself.
  - frappe/erpnext
      Site: edu.erpnext.zubbystudio.shop
      Custom apps: library_management, education, edu_theme (Vue.js 3 + Vite)
  - openproject (project management)
  - n8n (automation — also candidate for daily NAV job scheduler)
  - wiki.js (documentation)
  - gitea (version control)
  - woodpecker (CI/CD)
  - registry (container images)

Networking:
  - All services on openagile_network
  - Traefik labels for all routing
  - HTTPS via Let's Encrypt
  - Internal DNS via container names
  - DNS: Cloudflare
```

### EPM v2 Tech Stack (locked)

```yaml
Backend:
  - FastAPI (Python)
  - PostgreSQL 15
  - SQLAlchemy async
  - Alembic (migrations — additive only, never destructive)
  - bcrypt==4.0.1 (PINNED — passlib incompatibility, do not change)
  - JWT in httpOnly cookies (30-day max_age — never body token)
  - Soft delete via deactivated_at TIMESTAMPTZ (never boolean flag alone)
  - ADMIN_ROLES = {"admin", "superadmin"} — module-level set constant in
    app/deps.py (fixes SUPERADMIN role-check exclusion bug found in AT-004
    A03/D02, HO-039)

Frontend:
  - React 18
  - TypeScript
  - Tailwind v4
  - TanStack Router (URL-first routing)
  - TanStack React Table (data tables)
  - Recharts (charting)
  - Admin route prefix: /settings/* (never /admin/*) — HO-024 implementation
    decision, corrected in specs/tests HO-037/038
  - isAdmin() check: ["admin", "superadmin"].includes(role) — authStore.ts,
    fixed HO-039
  - All CRUD editing is modal-based (shadcn/ui Dialog pattern — e.g. UserModal,
    EditHoldingModal). No inline row editing anywhere in the codebase — HO-023,
    reaffirmed and enforced in _app.holdings.tsx via HO-040/041

Testing:
  - pytest + pytest-asyncio
  - Naming: EPM_TEST_TAXONOMY — DOMAIN-WORKFLOW-LAYER-TYPE-NNN
  - Folders: tests/backend/ tests/frontend/ tests/security/ tests/infrastructure/ tests/fixtures/
  - CI database: epm_test (PostgreSQL 15, shared instance — NEVER ephemeral service container)

Deployment URLs:
  - Staging / test drive: testdrive.epm.zubbystudio.shop
  - Testbuild (teardown pending): testbuild.zubbystudio.shop
```

---

## Locked Architectural Decisions

These are permanent. Never revisit without a formal Zone 2 consensus session
between Claude Web and DeepSeek Pro documented in a handover.

| Decision | Value | Reason |
|----------|-------|--------|
| `bcrypt==4.0.1` pinned | Do not upgrade | passlib incompatibility confirmed |
| JWT location | httpOnly cookie, 30-day max_age | Security — never expose in response body |
| Monetary API values | Always returned as strings | Precision — never numeric in JSON |
| Soft delete | `deactivated_at TIMESTAMPTZ` + `is_active BOOLEAN` | Timezone-aware, auditable |
| No editMode toggle, no inline row editing | Modal-based CRUD only, admin section for all CRUD | HO-023 permanent decision; reaffirmed and enforced in `_app.holdings.tsx` via HO-040/041 |
| `admin_audit` table | All CRUD operations logged here | Audit trail |
| `get_session()` naming | Function naming locked | Breaking change risk |
| Migrations | Additive only — `ADD COLUMN IF NOT EXISTS` | Never drop or rename in production |
| No new Postgres instances | Reuse shared PostgreSQL 15 only | Resource constraint |
| RuleBasedRouter first | For AI chatbot feature F-022 | Architecture decision |
| NAV carry-forward | Use most recent prior price when date missing | F-007 calculation rule, OQ-F007-3 |
| Deactivated user portfolios | Hidden from other USERs' views/aggregates; visible to ADMIN/SUPERADMIN via audit trail | OQ-F016-1, resolved 2026-07-05, reconfirmed HO-042 |
| Account creation flow | Admin-only — no email invitation flow | OQ-F016-2, resolved 2026-07-05, reconfirmed HO-042/047 |
| Admin route prefix | `/settings/*`, never `/admin/*` | HO-024 implementation decision; corrected HO-037/038 |
| `ADMIN_ROLES` set constant | `{"admin", "superadmin"}` in `app/deps.py` | Prevents SUPERADMIN-exclusion bugs (AT-004 A03/D02) |
| `lifecycle_status` on `ClaimRecord` | Single source of truth for claim UI state (3 values: unresolved/unclaimed/claimed). `claim_status` (6-value) remains the backend/audit detail field, never read directly by frontend state-derivation logic | F-011 governance ruling HO-036 (column), HO-045 (canonical mapping ruling) |
| Canonical claim_status → lifecycle_status mapping | `approved→unclaimed`; `pending, partially_paid, rejected, lapsed→unresolved`; `paid→claimed` | HO-045 — "unclaimed" = owed-but-not-collected, matches project's existing "unclaimed dividend" terminology |
| Cost basis gain calculation | Null/missing cost basis → gain calculated against zero cost (full current value counts as gain); holding never excluded from gain calc | OQ-FINV-2, resolved HO-043 |
| F-INV-001 cost entry scope | Both CSV bulk upload AND manual per-holding form ship — not either/or | OQ-FINV-1, resolved HO-043 |
| Merge to `main` | Requires Gate 1 (AT-XXX green, design-only, not yet CI-enforced) **and** Gate 2 (explicit PO/Zubbyik sign-off via required GitHub PR review — enforced now via branch protection) | Established 2026-07-07, see CI/CD Pipeline section |

---

## Agent Roster

### Zone 2 — Architecture / Governance (requires consensus)

| Agent | Role | Model | Responsibilities |
|-------|------|-------|-----------------|
| Claude Web | The Brain / Architect | claude-sonnet-4-6 | Architecture, specs, governance, Gherkin, handovers, RCA |
| DeepSeek Pro | Architecture co-lead | openrouter/deepseek/deepseek-v4-pro | Architecture review, tradeoffs, system design — consensus required with Claude |

**Zone 2 rule**: Both Claude Web AND DeepSeek Pro must agree before any builder agent acts on an architectural decision.

### Zone 1 — Implementation (builders)

| Agent | Role | Model | Responsibilities |
|-------|------|-------|-----------------|
| hermes deepseek-flash | Backend + infrastructure builder | openrouter/deepseek/deepseek-v4-flash | FastAPI, PostgreSQL, Docker, GitHub Actions, CI/CD, VPS ops, backend implementation |
| hermes deepseek-flash | Frontend builder (primary) | openrouter/deepseek/deepseek-v4-flash | React 18, TypeScript, Tailwind v4, TanStack ecosystem — standard frontend work |
| Kimi k2.0 | Frontend builder (escalation) | openrouter/kimi/k2.0 | Complex frontend implementation — escalated from deepseek-flash when needed |
| Codex / Owl Alpha | Test executor (primary) | — | Runs AT-XXX acceptance tests, reports via HO |
| hermes deepseek-flash | Test executor (fallback) | openrouter/deepseek/deepseek-v4-flash | Formally accepted fallback tester when Codex/Owl Alpha unavailable (HO-037) |
| hermes opencode-zen | Hermes governance | — | Governance plans, no implementation |

**Sign-off authority**: Test execution may be delegated to the fallback tester, but AT-XXX **sign-off** authority remains exclusively Claude (Architect) + Zubbyik (PO).

**Frontend escalation rule**: hermes deepseek-flash handles all frontend work. Escalate to Kimi k2.0 only for complex frontend build/implementation situations. Document the escalation reason in the handover.

### ⚠️ CLI / Orchestration Note (added 2026-07-08)

**Hermes is a CLI tool, not a model.** As of 2026-07-08, Zone 1 builder
sessions are transitioning to run through **OpenCode CLI** rather than the
prior Hermes CLI invocation, on a trial basis (4-5 runs before full
adoption). This does **not** change the model or Agent Roster above —
`deepseek-v4-flash` remains the underlying model for backend/frontend
builder work, accessed via OpenCode's `opencode-go` provider instead of
the Hermes CLI wrapper. Trial success criteria: correct HO-number pulling
from the pre-assigned table (never self-assigned), spec-first discipline
held, merge gate respected (PR + Gate 2 approval, never direct push), and
correct context-file loading (`.context/MASTER_CONTEXT.md` only — see
Context System Hygiene section below).

### Deprecated / Reassigned

| Agent | Status | Replaced by |
|-------|--------|-------------|
| hermes nemotron | Reassigned | hermes deepseek-flash (frontend primary) + Kimi (escalation) |
| Antigravity | Legacy reference (v3.0) | hermes deepseek-flash |
| Grok | Legacy reference (v3.0) | DeepSeek Pro |
| Nemotron (`nemotron-3-ultra-550b-a55b`, distinct from "hermes nemotron" above) | Legacy — described in now-archived `.context/AGENT.md` system (June/July 2026 generation) as active frontend owner | hermes deepseek-flash + Kimi. Confirmed superseded — do not treat `.context/AGENT.md` as current, see Context System Hygiene section |

---

## Routing Logic

### Zone 1 — Implementation

**Keywords**: generate, build, scaffold, boilerplate, refactor, "just give me"

**Flow**:
```
Builder → DeepSeek Pro review
```

**Builders**:
- Backend: hermes deepseek-flash
- Frontend: hermes deepseek-flash (escalate to Kimi for complex work)

### Zone 2 — Architecture

**Keywords**: design, critique, plan, tradeoff, learn, RCA, architecture, spec

**Flow**:
```
Claude Web design → DeepSeek Pro consensus → Builder implementation
```

**Default zone**: Zone 2 (add friction by default)

---

## CI/CD Pipeline

⚠️ **Current actual state (verified 2026-07-06, reconfirmed 2026-07-08): the branch-flow/approval-gate content below is target design, not running infrastructure.** There is no `.github/workflows/` directory in the repo — no GitHub Actions exist. Deployments to testdrive/testbuild happen via direct VPS execution only (see Temporary Infrastructure Change above). Test isolation strategy (schema vs. separate database) remains undecided and will be chosen fresh when CI work resumes. Treat everything below as **design-to-implement**, except Gate 2, which is real and enforced today (see next section).

### ⚠️ Gate 2 — Real, Enforced Today (established 2026-07-07)

Unlike Gate 1 (CI/CD, still design-only), **Gate 2 is live GitHub branch
protection on `main`**, independent of any CI pipeline:

1. Require a pull request before merging — no direct pushes/merges to `main`.
2. Require ≥1 approval.
3. Require review from Code Owners — `CODEOWNERS` file at repo root maps `*` → `@zubbyik`. **Any additional approving account must have Write access, not Read — Read-access approvals do not satisfy this rule** (this caused a real approval lockout incident on 2026-07-08).
4. No bypass for admins/collaborators, even under time pressure.
5. Restrict direct push to `main` to nobody — PR-only.
6. When Gate 1 (CI/CD) is eventually wired, its job names get added under "Require status checks to pass" on this same rule — the two gates then stack automatically.

**Process rule for all agents**: every merge to `main` goes through a PR
referencing the passing AT-XXX/HO number, requiring Zubbyik's explicit
review approval. Two direct-to-main bypasses have occurred and been logged
as accepted one-off exceptions (HO-041's B04b fix, and a second bypass on
2026-07-08 caused by an approval-account mixup) — see Historical Decision
Log. Neither authorizes a standing exception; if Gate 2 approval is
blocked or misconfigured, the correct response is to report back and
wait, not bypass.

### Branch Flow (design — not currently enforced beyond Gate 2 above)

```
feature/*, develop
    → static analysis
    → tests (epm_test DB — self-hosted runner)
    → build

test branch
    → static analysis
    → tests
    → build
    → deploy to testdrive.epm.zubbystudio.shop
    → e2e tests

main branch
    → static analysis
    → tests
    → build
    → Gate 1 (design-only): automated approval gate (/approve comment — three-factor:
      authorized commenter + ci-verified label + HEAD SHA staleness check)
    → Gate 2 (ACTIVE): PO sign-off via required GitHub PR review
    → deploy to production
    → e2e tests
```

### CI Rules

- No direct merge to main — review required every cycle (Gate 2 enforces this today)
- Self-hosted runner on VPS connects to `epm_test` database (design-only, not yet running)
- `epm_test` is a named database within the existing PostgreSQL 15 instance
- **NEVER** use ephemeral Postgres service containers in GitHub Actions
- SSH heredocs always quoted: `ssh user@host <<'EOF' ... EOF`

### Execution Path (normal — when workstation is online)

```
Local Fedora (git push only)
    ↓
GitHub Repository
    ↓ triggers
GitHub Actions (self-hosted runner on VPS)
    ↓
Netcup VPS
```

### Execution Path (temporary — workstation offline, current state)

```
Direct VPS execution via SSH permitted
    ↓
Code still committed to GitHub
    ↓
GitHub Actions still canonical deployment path (once rebuilt)
```

### Anti-Patterns (permanent — even during temporary exception)

```
❌ Bypass Traefik — all HTTP/HTTPS must go through it
❌ Create new Postgres instance
❌ Use ephemeral DB containers in CI
❌ Unquoted SSH heredocs
❌ System pip installs (use containers or isolated envs)
❌ Direct merge to main without review AND explicit PO sign-off (Gate 2)
❌ Implement before spec exists (Zone 1 cannot start without AT-XXX criteria)
❌ Inline row editing anywhere in the codebase (HO-023, reaffirmed HO-040)
```

---

## Handover Protocol

### Handover Document Standards

All handovers use format: `HO-NNN-description.md`

Required fields:
```yaml
---
type: HO
id: HO-NNN
title: FROM → TO: description
date: YYYY-MM-DD
from: agent name
to: agent name
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT | HIGH | NORMAL
---
```

### Information Flow

| From | To | Artifact | Requirements |
|------|----|----------|--------------|
| User / Zubbyik | Claude Web | Architecture questions, product decisions, AT results | — |
| Claude Web | Builders | `HO-*.md` | Structured, numbered, actionable |
| Builders | Claude Web | `HO-*.md` | Structured, numbered, status-aware, **raw command output for any claim about repo/file state — not a narrated summary** (added 2026-07-08, see Context System Hygiene) |
| Claude Web | User | Decisions, tradeoffs, clarifications | Max 3 questions at once |

### Handover Rules

- DeepSeek Pro: Never implement before design approval
- hermes deepseek-flash: Never start backend work without contracts/specs and acceptance criteria
- Frontend builder: Never start frontend before APIs are stable
- Nothing merges directly to main — previous output never authorizes skipping review, and merge additionally requires Gate 2 PO sign-off
- **Specs before implementation is absolute** — no builder agent starts without a Claude-authored spec
- **HO numbers are pulled from the Pre-assigned HO numbers table, never self-assigned** — two numbering collisions occurred this session (HO-042 double-assigned; an "HO-031" mistagging in the 2026-07-05 history) from exactly this failure mode

---

## Feature Spec Standards

### Spec File Convention

```
F-NNN-feature-name.md
Location: .context/feature-specs/
Author: Claude Web (always — builders never write specs)
```

### Required Spec Sections

1. Purpose
2. Scope (in / out)
3. Data model
4. API contract (request/response shapes, status codes)
5. Frontend requirements
6. Acceptance criteria (maps to AT-NNN Gherkin scenarios)
7. Dependencies
8. Open questions

### Active Features — Phase 3C

| Feature | Status | Spec | Notes |
|---------|--------|------|-------|
| F-013 Companies Page | Spec ready — pending implementation | `.context/feature-specs/F-013-companies-page.md` | TanStack React Table, company profile page |
| F-016 User Management | **Shipped — built out-of-process** | `.docs/specs/F-016-user-management.md` | ⚠️ One-off exception: DeepSeek Pro implemented directly, no Zone 2 review, justified by urgent credential-provisioning need. Logged 2026-07-05, retroactive HO-030. Does not set precedent. |
| F-011 Claims CSV Upload | **Deployed — upload test PASS** | `.context/feature-specs/F-011-claims-upload.md` (v1.1) | Unmatched CSV rows land as unresolved claims (holding_id=null, lifecycle_status=unresolved, raw_company_name populated). Resolve flow (`PUT /api/v1/claims/{id}/resolve`) works but lacks formal test coverage of the lifecycle_status transition — flagged HO-048, not yet written |
| F-010 Claims (absorbs F-008 Dividends) | **Shipped — deployed to testdrive** | `.context/feature-specs/F-010-claims.md` | ⚠️ One-off exception: pulled ahead of Phase 3C sequence (Lovable template). Frontend `statusMap` reconciled against canonical `lifecycle_status` mapping this session — see HO-045/046 |
| F-007 NAV History | Spec complete — **UNBLOCKED** | `.docs/specs/F-007-nav-history.md` | OQ-F007-3 resolved (carry-forward NAV, matches existing rule) — implementation may proceed |
| F-INV-001 Initial Stock Cost Upload | Spec pending — **UNBLOCKED for spec authoring** | — | OQ-FINV-1/2 resolved: hybrid scope (both CSV + manual form), null cost basis → zero-cost gain calc. Claude to draft spec next. |
| F-017 Remove editMode / Admin CRUD | Spec to write | — | Unblocked now that F-016 shipped; much of the inline-editing cleanup already done ahead of schedule via HO-040/041 |
| F-003b Price entry v2 | Spec to write | — | After F-017 |
| F-006b Dividends v2 | Spec to write | — | After F-017, parallel with F-003b — scope overlap with shipped F-010 to be reconciled when spec is written |
| F-TD-001 Test Checklist + Teardown | Spec ready — pending implementation | `.context/feature-specs/F-TD-001-test-checklist-teardown.md` | Teardown removes testbuild's nginx/proxy layer only, not the shared `_v3` container |
| F-019 Audit Log | Spec TBD | — | Receives events from F-016 |
| F-008 Dividends | **Superseded by F-010** | — | Original stub route `/dividends` left in place, hidden from nav |

### Phase 3C Sequencing (strict — standing rule)

```
AT-004 — 14/14 green — CLEARED 2026-07-07 (HO-039/040/041)
    ↓
F-016: already shipped (one-off exception, pre-dates this gate) — OQ-F016-1/2 resolved
F-011: already deployed (one-off exception) — unresolved-claims support tested, HO-047
    ↓
F-INV-001 spec (Claude, next) → implementation (OQ-FINV-1/2 resolved)
F-007 implementation (OQ-F007-3 resolved) — may proceed now
    ↓
F-017 spec (Claude) → implementation
    ↓
F-003b + F-006b (parallel, each needs spec first)
    ↓
BUG-DASH-NOTIFY-001 (bell/useActionItems — deferred standalone)
```

**Standing exceptions on record (do not set precedent):** F-016 (out-of-process build) and F-010 (pulled ahead of sequence). Both logged 2026-07-05. Neither authorizes skipping Zone 2 consensus or the AT-004 gate for any future feature.

---

## Test Taxonomy

**Standard**: `EPM_TEST_TAXONOMY.md`
**Naming**: `DOMAIN-WORKFLOW-LAYER-TYPE-NNN`

### Folder Structure

```
tests/
  backend/
    auth/login/{unit,integration,contract}/
    holdings/create/{unit,integration,contract}/
    holdings/update/integration/
    prices/quick-entry/integration/
    prices/pdf-upload/{unit,integration}/
    nav-history/integration/
    admin/audit/integration/
    companies/integration/
    dividends/integration/
  frontend/
    auth/login/
    holdings/
    dashboard/
  security/
    authentication/jwt/
    authorization/role-boundaries/
    cookies/
  infrastructure/
    docker/
    traefik/
  fixtures/
    conftest.py
```

### Active Test Status

| Test ID | Status | Notes |
|---------|--------|-------|
| DASH-VIEW-FE-E2E-001 | ✅ PASS | Sector allocation + charts |
| DASH-VIEW-FE-SMK-001 | ✅ PASS | Theme toggle |
| DASH-VIEW-FE-SMK-002 | ❌ DEFERRED | BUG-DASH-NOTIFY-001 — bell/useActionItems — post F-016 |
| HOLD-UPDATE-FE-E2E-001 | CLOSED | Superseded by HO-023 — inline editing removed |
| HOLD-VIEW-BE-E2E-001 | xfail | Blocked pending F-INV-001 |
| PRIC-UPDATE-BE-E2E-001 | ✅ PASS conditional | Price write OK; E2E chain blocked by F-INV-001 |
| SEC-JWT-BE-SEC-001 | ✅ PASS | JWT tamper + missing cookie |
| SEC-ROLE-BE-SEC-001 | xfail | Rename readonly_http_client → user_http_client; F-016 required |
| INF-DOCKER-SMK-001 | ✅ PASS | Staging API + frontend smoke |
| AT-004 (A01–E02, 14 cases) | ✅ 14/14 PASS | Gate cleared 2026-07-07 — see Historical Decision Log for B04b/SUPERADMIN fix details |
| AT-005 (null-holding rendering, 5 AC) | Drafted, not yet run | HO-045/048 — must pass before F-011's unresolved-claims path is considered fully verified |

---

## Open Questions (Product Owner — Zubbyik must answer)

*(none currently open as of 2026-07-08 — all resolved, see Resolved Questions Log)*

### Resolved Questions Log

| ID | Question | Answer | Resolved | Notes |
|----|----------|--------|----------|-------|
| OQ-F016-1 | Deactivated users' portfolios: hidden or read-only? | **Hidden** — from other USERs' views/aggregates; visible to ADMIN/SUPERADMIN via audit trail | 2026-07-05 | Answered during out-of-process F-016 build; reconfirmed independently HO-042 |
| OQ-F016-2 | Account creation: admin-only or email invitation flow? | **Admin-only** — no email invite flow | 2026-07-05 | Same as above; reconfirmed HO-042/047 |
| OQ-F007-3 | Non-trading days: store carry-forward NAV or skip entirely? | **Carry-forward NAV** | 2026-07-07 | Matches pre-existing locked decision — no new work implied |
| OQ-FINV-1 | Initial stock costs: CSV upload or manual form? | **Hybrid — both ship** | 2026-07-08 | Doubles spec surface vs single-method design; confirmed acceptable |
| OQ-FINV-2 | All holdings need cost basis, or only specific portfolios? | **Optional/nullable per holding** — inherited stock, no cost paid | 2026-07-08 | New rule: null cost basis → gain calculated against zero, never excluded |

---

## Handover Chain — Current

| HO | Direction | Status | Contents |
|----|-----------|--------|----------|
| HO-024 | Claude → hermes nemotron | Complete | Admin restructure, editMode removal |
| HO-025 | Claude → Owl Alpha | Complete | Test taxonomy migration |
| HO-026 | hermes → Claude | Closed — superseded by HO-037 | — |
| HO-027 | Claude → hermes nemotron | Sent | Spec delivery F-016, F-007, AT-004 |
| HO-028 | Claude → Hermes governance | Sent | OQ answers; Phase B sequencing |
| HO-029 | Hermes → Claude | Received | Phase A acceptance fixes; F-013 + F-TD-001 specs ready |
| HO-030 | DeepSeek Pro → Claude | Retroactive, no prior Zone 2 review | F-016 implementation complete, out-of-process |
| HO-034a | Hermes → Claude | Complete | F-010 Claims dashboard (renumbered from an original "HO-031" — 2026-07-05 renumbering) |
| HO-035 | Hermes → Claude | Received | F-011 Claims CSV Upload spec |
| HO-036 | Claude → Hermes | Sent | F-011 governance ruling — lifecycle_status column, thresholds, preview shape |
| HO-037 | Hermes → Claude | Received | AT-004 first run — 11/14 PASS |
| HO-038 | Claude → Hermes | Sent | AT-004 ruling — fix ADMIN_ROLES + isAdmin(); isEditing context requested |
| HO-039 | Hermes → Claude | Received | AT-004 re-run — 12/14 PASS, B04b held |
| HO-040 | Claude → Hermes | Sent | B04b ruling — confirmed HO-023 violation |
| HO-041 | Hermes → Claude | Received | B04b fix — **AT-004 14/14 PASS, gate cleared** |
| HO-042 | Claude → Hermes | Sent | AT-004 sign-off + OQ-F016-1/2/F007-3/FINV-1/2 rulings |
| HO-043 | Claude → Hermes | Sent | OQ follow-up closure — F-INV-001 scope, gain-calc rule locked |
| HO-044 | Hermes → Claude | Received | F-010 file dump for lifecycle_status audit (renumbered from a mistagged "HO-042") |
| HO-045 | Claude → Hermes | Sent | F-010 reconciliation ruling — canonical mapping, backfill required, F-011 schema gaps |
| HO-046 | Hermes → Claude | Received | Backfill + schema prep + frontend refactor complete |
| HO-047 | Hermes → Claude | Received | F-016 kickoff request (stale OQ status reported — corrected in HO-048) |
| HO-048 | Claude → Hermes | Sent | Status correction — F-016/F-007 confirmed unblocked; resolve-endpoint test flagged |
| HO-049 | Hermes → Claude | Received | New-session context reconciliation — surfaced legacy `docs/context/` system |
| HO-050 | Claude → Hermes | Sent | Halt — conflicting context systems found, raw audit required |
| HO-051 | Claude → Hermes | Sent | Canonical file ruling (File A confirmed) + legacy cleanup instructions |
| HO-052 | Claude → Hermes | Sent | Restore accidentally-deleted `.context/MASTER_CONTEXT_{server,workstation}.md` overlays |
| HO-053 | Claude → Hermes | Sent | Fourth context system found (`.context/AGENT.md` legacy roster) — audit required |

### Pre-assigned HO numbers

| HO | Purpose |
|----|---------|
| HO-031 | Hermes → Claude: F-017 implementation complete (slot vacated after 2026-07-05 renumbering of the Claims HO out of it) |
| HO-032 | Hermes → Claude: F-003b implementation complete |
| HO-033 | Hermes → Claude: F-006b implementation complete |
| HO-034b | Hermes → Claude: Phase C deployment verification (renumbered from original "HO-034") |
| HO-054 | Hermes → Claude: `.context/AGENT*.md` raw audit results (HO-053 follow-up) |
| HO-055 | Hermes → Claude: F-016/F-007 implementation progress report |
| HO-056 | Hermes → Claude: F-INV-001 implementation complete |

---

## Role Model (F-016)

| Role | Level | Capabilities |
|------|-------|-------------|
| SUPERADMIN | 30 | Full system access; can manage ADMINs; cannot be deactivated if last one |
| ADMIN | 20 | Manage USERs, price uploads, portfolio approvals; cannot touch other ADMINs |
| USER | 10 | Own portfolios and holdings only; no admin section access |

Permission inheritance: additive upward. SUPERADMIN inherits all ADMIN permissions; ADMIN inherits all USER permissions.

---

## Infrastructure Constraints (hard limits)

```
NEVER:
  - Create new Postgres container (one exists — reuse it)
  - Use ephemeral DB containers in CI (use epm_test on shared instance)
  - Bypass Traefik (all HTTP/HTTPS through it)
  - Install packages in system Python (use containers or isolated environments)
  - SSH directly to server for deployments when workstation is online
  - Merge directly to main without review AND explicit PO sign-off (Gate 2, active 2026-07-07)
  - Start implementation without a Claude-authored spec and acceptance criteria
  - Create or run code locally on Fedora during temporary offline period
  - Use inline row editing anywhere in the codebase (HO-023, reaffirmed HO-040)
  - Self-assign HO numbers — pull from the Pre-assigned HO numbers table
  - Treat any file under docs/context-ARCHIVED-* or .context/ARCHIVED-* as current

ALWAYS:
  - Check existing services before adding new ones
  - Use openagile_network for inter-service communication
  - Follow Traefik label convention
  - Quote SSH heredocs: ssh user@host <<'EOF' ... EOF
  - Deploy via GitHub Actions (canonical path — even during VPS-direct exception)
  - Route all main merges through a PR referencing the passing AT-XXX/HO number
  - Update MASTER_CONTEXT.md after every major infrastructure or architectural change
  - Increment version number on every update
  - Use raw command output, not narrated summaries, when reporting repo/file state to Claude for governance purposes
```

### Traefik Label Convention

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.SERVICE.rule=Host(`SUBDOMAIN.zubbystudio.shop`)"
  - "traefik.http.routers.SERVICE.entrypoints=websecure"
  - "traefik.http.routers.SERVICE.tls=true"
  - "traefik.http.routers.SERVICE.tls.certresolver=letsencrypt"
  - "traefik.http.services.SERVICE.loadbalancer.server.port=PORT"
  - "traefik.docker.network=openagile_network"
```

---

## Context System Hygiene (new section, 2026-07-08)

Multiple parallel/stale context-file systems were discovered and cleaned up
this session. **`.context/MASTER_CONTEXT.md` (this file) is the sole
canonical source.** Everything else:

| Path | Status | Notes |
|------|--------|-------|
| `AGENTS_PROMPTS_AND_INSTRUCTIONS/specs/MASTER_CONTEXT_v4.md` | **Deleted**, stub in place | Frozen origin copy this file was promoted from (2026-07-05, commit `2abadbb`) |
| `docs/context/{MASTER_CONTEXT.md, WORKFLOW.md, AGENT_STATE.yaml, DELEGATION_REGISTRY.md, PROJECT_STATUS.md}` | **Archived** → `docs/context-ARCHIVED-pre-openagile-2026-05/` | Described a defunct agent roster (Owl Alpha, Nex N2, DeepSeek v4) and phase (`bugs_open_cleanup`), last touched 2026-05-18/23 |
| `.context/AGENT.md` + `project-overview.md` + `architecture.md` | **Archiving** → `.context/ARCHIVED-legacy-agent-system-2026-07/` | Entry point + support files for the pre-OpenAgile DeepSeek/Flash/Nemotron TDD-workflow generation (commits `3a9e58e`/`ebea483`, June–July 2026) |
| `.context/{code-standards.md, ai-workflow-rules.md, ui-context.md, progress-tracker.md, current-issues.md}` | **Under review** | Content not yet fully audited as of v4.3 — do not treat as authoritative until reviewed (HO-053/054). `ai-workflow-rules.md` in particular is still referenced by the live `opencode.json` config and may contain a RED-test-first discipline worth formally adopting — pending review |
| Root `AGENTS.md` | **Current** | Points solely at `.context/MASTER_CONTEXT.md`, `.context/feature-specs/`, `docs/handovers/` |
| `.context/AGENTS.md` (plural, declared in project `opencode.json`) | **Unconfirmed** | Existence not yet verified via raw `ls` — may not exist, may be a duplicate of root `AGENTS.md`, or may be the source of `opencode.json` silently loading nothing. Resolve before declaring OpenCode CLI trial "go" |
| `/openagile_2/MASTER_CONTEXT.md` (v3.0) and `/openagile_2/docs/context/MASTER_CONTEXT.md` | **Out of scope** | Workspace-wide (all projects), not EPM-specific — separate governance question, not blocking EPM work |

**Rule going forward**: any report on repo/file state for governance
purposes includes raw command output, not a narrated summary — several
contradictions this session were traced directly to summaries that looked
complete but omitted the detail that mattered.

---

## Emergency Protocols

### Production Outage

```
1. Check last change in Historical Decision Log
2. Run diagnostic: docker compose logs SERVICE --tail=100
3. Check Grafana for metrics/alerts
4. Review GitHub Actions run logs for recent deployment
5. Rollback via GitHub Actions revert + push (never manual file transfer)
```

### Lost Context (Fresh Agent Session)

```
1. Provide this file to agent
2. Agent reads Infrastructure Contract + Agent Roster + Feature Sequence
3. Agent checks Open Questions before proposing any implementation
4. Proceed with full context — no assumptions
5. If any other file under .context/ or docs/ claims to be canonical
   context and conflicts with this file, THIS FILE WINS — flag the
   conflict back to Claude rather than resolving it independently
```

### Workstation Restored

```
1. Remove temporary VPS-direct execution permission from this file
2. Confirm all changes made during offline period are committed to GitHub
3. Increment MASTER_CONTEXT.md version
4. Resume normal GitHub Actions deployment flow
5. Restore .context/MASTER_CONTEXT_workstation.md content relevance —
   confirm it's still accurate for the restored setup
```

---

## Maintenance

**After every session with architectural changes:**
- [ ] Update Historical Decision Log
- [ ] Update Open Questions table
- [ ] Update HO chain table
- [ ] Update Feature status table
- [ ] Increment version number
- [ ] Commit with message: `MASTER_CONTEXT: v{N} — {one-line summary}`

**Sync locations:**
- Netcup VPS: updated in-situ by Hermes/OpenCode agents
- Claude Web project: manually copied by Zubbyik after each update
- Gitea: committed to repo as `.context/MASTER_CONTEXT.md`

---

## Historical Decision Log

### EPM v2

**2026-07-08: MASTER_CONTEXT.md v4.3 — Session close-out**
- AT-004 gate closure finalized: B04b (isEditing in `_app.holdings.tsx`) ruled a HO-023 violation (HO-040); fixed via `EditHoldingModal.tsx` replacing `InlineEditRow.tsx` (HO-041). **AT-004 final: 14/14 PASS.**
- Gate 2 established: GitHub branch protection on `main` (required PR, required Write-access approval via CODEOWNERS, no admin bypass). Two one-off bypass exceptions logged: HO-041's direct commit (predates Gate 2) and a second bypass on 2026-07-08 caused by an approval-account permission mixup (wrong account had Read, not Write access) — both accepted one-offs, not precedent.
- F-010/F-011 `lifecycle_status` reconciliation (HO-044/045/046): found the shipped frontend `statusMap` conflicted with F-010's own spec, AND found `lifecycle_status` was never backfilled for pre-existing rows (data-integrity risk, caught before causing visible damage). Canonical mapping ruled (spec's original mapping wins — "unclaimed" means owed-but-not-collected). Backfill run (9 seed rows, no visible impact yet since no approved/paid/rejected/lapsed rows existed). F-011 schema prep done: `holding_id` nullable, `raw_company_name` added. Frontend refactored to read `lifecycle_status` directly.
- All five session-opened Open Questions resolved: OQ-F016-1/2 (reconfirming a 2026-07-05 resolution), OQ-F007-3, OQ-FINV-1 (hybrid CSV+manual), OQ-FINV-2 (null cost basis → zero-cost gain calc, new locked rule).
- F-011 unresolved-claims flow deployed and tested (HO-047) — unmatched CSV rows correctly land as unresolved claims; resolve endpoint works but lacks formal lifecycle_status-transition test coverage (flagged, not yet written).
- Multiple stale/conflicting context systems discovered and cleaned up: `AGENTS_PROMPTS_AND_INSTRUCTIONS/specs/MASTER_CONTEXT_v4.md` (deleted, stubbed), `docs/context/*` (archived — defunct Owl Alpha/Nex N2/DeepSeek v4 roster, `bugs_open_cleanup` phase), `.context/AGENT.md` + support files (archiving — defunct DeepSeek/Flash/Nemotron TDD-workflow generation). Root `AGENTS.md` rewritten to point solely at this file. Remaining `.context/` files (`ai-workflow-rules.md`, `progress-tracker.md`, `code-standards.md`, `ui-context.md`, `current-issues.md`) still under review as of this version — not yet ruled archive-vs-adopt.
- Orchestration note: Zone 1 builder sessions trialing OpenCode CLI in place of Hermes CLI (4-5 run trial) — no Agent Roster/model change, `deepseek-v4-flash` remains the underlying model.
- New standing rule: HO reports on repo/file state must include raw command output, not narrated summaries — traced several contradictions this session directly to this gap.

**2026-07-06: MASTER_CONTEXT.md v4.2 — v4.0/v4.1 reconciliation, legacy doc detached**
- Compared true `MASTER_CONTEXT_v4.0.md` (April 25, 2026 — "Master Prompt Framework" lineage) against v4.1 (EPM v2/Phase 3C lineage) against actual VPS state rather than assuming either doc.
- CI/CD: confirmed neither doc's pipeline design is actually running — no `.github/workflows/` exists. Annotated as target design, not current reality.
- Staging URLs resolved: `testdrive`/`testbuild` both point to the same `_v3` container; `testbuild` additionally fronts an nginx checklist+proxy layer. F-TD-001 removes that layer only.
- Obsidian vault sync: confirmed no `vault-sync.yml` exists; treated as a one-off historical seed, not ongoing infrastructure.
- Legacy `MASTER_CONTEXT_v4_0.md` formally detached per product-owner decision — historical reference only.

**2026-07-05: MASTER_CONTEXT.md v4.1**
- F-016 confirmed shipped, built out-of-process: DeepSeek Pro implemented directly, no Zone 2 review, justified by urgent security requirement. Logged as one-off exception, retroactive HO-030.
- OQ-F016-1/OQ-F016-2 resolved (hidden/SUPERADMIN-visible; admin-only creation).
- F-010 Claims (absorbs F-008) confirmed shipped and deployed, pulled ahead of Phase 3C gate sequence as a one-off exception.
- Handover renumbering: an original "HO-031" (F-010 Claims report) renumbered to HO-034a; original "HO-034" (Phase C verification) renumbered to HO-034b to avoid collision.
- Neither exception authorizes skipping Zone 2 consensus or the AT-004 gate for any future feature.

**2026-07-05: MASTER_CONTEXT.md v4.0**
- Rebuilt from v3.0 to reflect EPM v2 FastAPI/React architecture.
- Agent roster changes: nemotron → deepseek-flash primary, Kimi escalation.
- Added temporary workstation-offline exception, Phase 3C feature sequence, locked decisions, role model, HO chain, test taxonomy.

**2026-07-03: Phase A acceptance testing (HO-029)**
- SPA routing fix, price history default range 30→365 days, Companies page scaffold confirmed, F-TD-001 spec produced. Merged to main (a5cee42, c788b85).

**2026-06-30: Phase 3C specs**
- F-016, F-007 specs produced. AT-004 acceptance test produced (14 cases). BUG-TRIAGE-001 disposition. F-INV-001 identified as required one-off spec.

**2026-06-25: Test taxonomy migration (HO-025)**
- EPM_TEST_TAXONOMY.md adopted, folder structure created, tests migrated, security + smoke tests added.

**2023-06-XX: HO-023 — editMode removal (locked)**
- All inline editing removed system-wide, all CRUD moved to Admin section.

### Legacy (from v3.0 — preserved for reference)

**2026-03-28: Migrated Nginx → Traefik**
**2026-03-15: Shared PostgreSQL Strategy**
**2025-12: Estate Portfolio Streamlit Integration (superseded by EPM v2)**

*(full detail on these three preserved from v4.0/v4.1/v4.2 — unchanged this version)*

---

**END OF MASTER_CONTEXT.md v4.3**
**File Maintainer**: Claude Web (Architect) — update after every major change
**Version Control**: `MASTER_CONTEXT: v4.3 — AT-004 closure, lifecycle_status ruling, Gate 2 established, all session OQs resolved, context-system cleanup`
