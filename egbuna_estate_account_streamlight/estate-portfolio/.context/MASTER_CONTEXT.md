# MASTER_CONTEXT.md — Single Source of Truth

**DO NOT EDIT WITHOUT HANDOVER PROTOCOL**

**Version**: 4.8
**Last Updated**: 2026-07-31
**Maintained By**: Claude Web (The Brain / Architect)
**Previous Version**: 4.7 (2026-07-28)

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
Domain Pattern: *.zubbystudio.site (migrated from *.zubbystudio.shop,
  2026-07-16 — .shop retired permanently, cost-driven decision, not
  malfunction-related. See Historical Decision Log. Other services
  (n8n, gitea, wiki.js, openproject, woodpecker, frappe/erpnext) have
  NOT yet been migrated to .site as of this version — they remain
  pointed at the now-defunct .shop domain; Zubbyik has explicitly
  deprioritized migrating them, do not treat as urgent unless raised.)

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
      Staging:   testdrive.epm.zubbystudio.site
      Testbuild: testbuild.zubbystudio.site (pending teardown — F-TD-001)
      ⚠️ Container naming chain (resolved 2026-07-06):
        Both hostnames currently point to the SAME running container ("_v3"):
          - _v3 = a fork of the old demo.estate container, running as temporary staging
          - testdrive.epm.zubbystudio.site = Traefik alias to _v3
          - testbuild.zubbystudio.site = nginx checklist page + API reverse-proxy,
            also forwarding to _v3
        This means both URLs currently serve identical backend state. F-TD-001
        (teardown) removes the testbuild nginx/proxy layer, not the _v3 container itself.
  - frappe/erpnext
      Site: edu.erpnext.zubbystudio.shop ⚠️ NOT YET MIGRATED — this
        still points at the retired .shop domain and is very likely
        unreachable. Deprioritized by Zubbyik.
      Custom apps: library_management, education, edu_theme (Vue.js 3 + Vite)
  - openproject (project management)
  - n8n (automation — rejected for scheduled tasks; OS cron preferred, see
    F-007's daily NAV snapshot script)
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
  - Alembic (migrations — additive only, never destructive; chain now
    reproducible from empty via 000_baseline_production_schema.py, see
    Locked Architectural Decisions)
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
  - CI database: epm_test — now a genuinely separate database on the
    shared PostgreSQL 15 instance (NOT a schema-within-estate_portfolio;
    the earlier schema-swap conftest pattern was retired 2026-07-25 for
    being fragile — see Locked Architectural Decisions and Historical
    Decision Log)

Deployment URLs:
  - Staging / test drive: testdrive.epm.zubbystudio.site
  - Testbuild (teardown pending): testbuild.zubbystudio.site
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
| `lifecycle_status` on `ClaimRecord` | Single source of truth for claim UI state (3 values: unresolved/unclaimed/claimed). `claim_status` (6-value) remains the backend/audit detail field, never read directly by frontend state-derivation logic | F-011 governance ruling
HO-036 (column), HO-045 (canonical mapping ruling) |
| Canonical claim_status → lifecycle_status mapping | `approved→unclaimed`; `pending, partially_paid, rejected, lapsed→unresolved`; `paid→claimed` | HO-045 — "unclaimed" = owed-but-not-collected, matches project's existing "unclaimed dividend" terminology |
| Cost basis gain calculation | Null/missing cost basis → gain calculated against zero cost (full current value counts as gain); holding never excluded from gain calc | OQ-FINV-2, resolved HO-043 |
| F-INV-001 cost entry scope | Both CSV bulk upload AND manual per-holding form ship — not either/or | OQ-FINV-1, resolved HO-043 |
| Merge to `main` | Requires Gate 1 (AT-XXX green, design-only, not yet CI-enforced) **and** Gate 2 (explicit PO/Zubbyik sign-off via required GitHub PR review — enforced now via branch protection) | Established 2026-07-07, see CI/CD Pipeline section |
| `admin_audit` table schema | `id, action, entity_type, entity_id, old_value, new_value, performed_by (FK→users), details, created_at` | Built ahead of F-019 during F-007 implementation (2026-07-12) — ratified as a one-off exception rather than rolled back, since a working, sensible schema already existed. F-019 builds on this schema rather than redesigning it. |
| `seed_admin.py` password behavior | **Intentionally overwrites the admin password on every re-run** (not idempotent) | Confirmed via
direct code read, 2026-07-12 — explicit design for GitHub Secret rotation recovery. This is not a bug; a stale test once assumed idempotency and was corrected to match reality, not the other way around. Locking this here so a future session doesn't re-flag it as a regression. |
| RED-GREEN test discipline | Write test → confirm it fails → implement → confirm it passes, in that order, for new feature work | Adopted 2026-07-13 from the archived `ai-workflow-rules.md` (pre-OpenAgile generation) — one of three practices judged worth keeping despite the surrounding file being superseded |
| One-feature-per-session | One agent session = one feature (F-XXX), one commit per feature, no mixed-feature execution | Same source as above, adopted 2026-07-13 |
| Three-layer acceptance order | Acceptance testing validates DB → API → UI in that order, each layer confirming the previous before moving up | Same source as above, adopted 2026-07-13 |
| Governance reports require raw output | HO reports on repo/file state must include raw command output, not narrated summaries | Standing rule since 2026-07-08 (see Context System Hygiene) — reconfirmed necessary again during the F-007 test-suite saga (HO-059 initially restated an investigation instead of confirming applied fixes), and again during F-022 backend review (mocked tests claiming regression coverage they didn't provide; a xpassed/xfailed count discrepancy that needed raw reconciliation) |
| `admin_audit.performed_by` nullable | Column changed from required FK to nullable, for automated/system-triggered audit entries with
no human actor (e.g. cron jobs) | Established 2026-07-16 for F-007's daily NAV cron script (HO-066). Manual/human-triggered actions still require a real FK; only automated actions may use NULL. |
| Zone 2 consensus — case-by-case waiver | DeepSeek Pro's architectural review remains the **default** for Zone 2 decisions, but Zubbyik may explicitly waive it for a specific feature/decision (cost/token constraints), decided per-instance — not a standing policy change | Established 2026-07-16. F-022's backend was the first instance: review waived on Zubbyik's explicit instruction, Claude Web self-reviewed as sole sign-off. Each future waiver must be explicitly requested, not assumed. |
| `epm_test` is a real, separate database | A genuine separate database on the shared PostgreSQL 15 instance (not a schema within `estate_portfolio`) — reconfirms/replaces the earlier aspirational-but-never-provisioned `epm_test` reference | Established 2026-07-25 (HO-078/083/084). The prior schema-swap (`estate_portfolio_test` schema + `search_path` override) was retired as fragile — it had already caused one real outage (the `DB_HOST`/connection failure that started this thread) and provided weaker isolation from production data. `Base.metadata.create_all` + `alembic stamp head` was used initially to unblock testing quickly, then replaced by a proper `alembic upgrade head` run once the baseline migration (below) made that possible. |
| Baseline migration (`000_baseline_production_schema.py`) | New root of the Alembic chain — introspected directly from live production, includes all 20 tables (18 ORM-modeled + 2 legacy) plus the `portfolio_summary` VIEW | Established 2026-07-25 (HO-083/084/086). Root cause: the original chain assumed a base schema from `init_db.sql`, run once against production and never committed to the repo — `alembic upgrade head` from empty failed as a result (discovered while investigating F-022's `epm_test` provisioning). This was a genuine disaster-recovery gap, not just a test-tooling issue: production had no reproducible schema origin in version control. Production itself required **no changes** — it was already at head; the baseline only makes the *chain* reproducible from empty for test databases and future DR. |
| Legacy tables `audit_logs`, `communication_logs` | Left as-is indefinitely — included in the baseline migration for accuracy, not added to `models.py` | Confirmed Owl-Alpha-era leftovers, no ORM models, no code references. Decision: no action, not a cleanup priority (HO-083/084). |
| `company_registrars` many-to-many join table | Replaces the single `companies.registrar_id` FK as the source of truth for company↔registrar relationships. Old column deprecated, not dropped (additive-only) — backfilled once, then unused going forward. | Established 2026-07-25/28 (F-026, HO-090/091/095). A single FK cannot represent co-registered companies (e.g. Seplat Energy Plc: DataMax Registrars primary + Computershare UK co_registrar) — the join table's `role` enum (`primary`/`co_registrar`) handles this cleanly. Production backfill produced 71 rows, verified as a perfect 1:1 mapping against `companies.registrar_id` (zero orphans, zero missing) — see Historical Decision Log. |
| Company vs. registrar entity separation | Any entity that is both a listed company and a registrar (e.g. Africa Prudential Plc) gets two fully independent records — one in `companies`, one in `registrars` — never a single merged record or a special self-reference. | Established 2026-07-25 (F-026 spec). Reason given: they are legally/functionally distinct entities "to the taxman" even when informally under one parent. Expressed via the same `company_registrars` join mechanism as any other link, not a special case. |
| `registrars.jurisdiction` | `VARCHAR(20) NOT NULL DEFAULT 'nigeria'`, values `nigeria` / `international` | Established 2026-07-25 (F-026). Standing rule, not a one-off: every non-Nigerian registrar needs different fields/behavior (e.g. NGX-specific requirement-type templates don't pre-populate for international registrars). Computershare UK (Seplat's co-registrar) is currently the only `international` row. |
| `companies.security_type` | `VARCHAR(20) NOT NULL DEFAULT 'equity'`, values `equity` / `etf` / `mutual_fund` | Established 2026-07-25 (F-026). Lets funds/ETFs (e.g. United Capital Mutual Funds sub-funds, Meristem Growth/Value ETF) exist as `companies` rows — needed to carry a registrar relationship — without being treated as ordinary equity holdings. No holdings/NAV logic changes as a result; purely additive metadata for now. |
| `registrar_requirements.due_date` | `DATE NULL` | Established 2026-07-25 (F-026). Nullable — most requirements have no hard deadline; supports the hybrid (visual + email) reminder system. |

---

## Agent Roster

### Zone 2 — Architecture / Governance (requires consensus)

| Agent | Role | Model | Responsibilities |
|-------|------|-------|-----------------|
| Claude Web | The Brain / Architect | claude-sonnet-4-6 | Architecture, specs, governance, Gherkin, handovers, RCA |
| DeepSeek Pro | Architecture co-lead | openrouter/deepseek/deepseek-v4-pro | Architecture review, tradeoffs, system design — consensus required with Claude (waivable case-by-case, see Locked Architectural Decisions) |

**Zone 2 rule**: Both Claude Web AND DeepSeek Pro must agree before any builder agent acts on an architectural decision, unless Zubbyik has explicitly waived review for that instance.

### Zone 1 — Implementation (builders)

| Agent | Role | Model | Responsibilities |
|-------|------|-------|-----------------|
| OpenCode (deepseek-flash builder) | Backend + infrastructure builder | openrouter/deepseek/deepseek-v4-flash via opencode-go provider | FastAPI, PostgreSQL, Docker, GitHub Actions, CI/CD, VPS ops, backend implementation |
| OpenCode (deepseek-flash builder) | Frontend builder (primary) | openrouter/deepseek/deepseek-v4-flash via opencode-go provider | React 18, TypeScript, Tailwind v4, TanStack ecosystem — standard frontend work |
| Kimi k2.0 | Frontend builder (escalation) | openrouter/kimi/k2.0 | Complex frontend implementation — escalated from deepseek-flash when needed |
| Codex / Owl Alpha | Test executor (primary) | — | Runs AT-XXX acceptance tests, reports via HO |
| OpenCode (deepseek-flash builder) | Test executor (fallback) | openrouter/deepseek/deepseek-v4-flash | Formally accepted fallback tester when Codex/Owl Alpha unavailable (HO-037) |

**Sign-off authority**: Test execution may be delegated to the fallback tester, but AT-XXX **sign-off** authority remains exclusively Claude (Architect) + Zubbyik (PO).

**Frontend escalation rule**: OpenCode's deepseek-flash builder handles all frontend work. Escalate to Kimi k2.0 only for complex frontend build/implementation situations. Document the escalation reason in the handover.

### ⚠️ CLI / Orchestration Note — Hermes CLI Retired, OpenCode CLI Adopted (2026-07-16)

**Hermes CLI has been fully replaced by OpenCode CLI** as of MASTER_CONTEXT
v4.5, following a clean 4-5 run trial (correct HO-number pulling from the
pre-assigned table, spec-first discipline held, merge gate respected,
correct context-file loading). This does **not** change the model or
Agent Roster — `deepseek-v4-flash` remains the underlying model for
backend/frontend builder work, accessed via OpenCode's `opencode-go`
provider. **Refer to the builder as "OpenCode" or "the deepseek-flash
builder session," not "Hermes"** — Hermes CLI is retired tooling
(`hermes_config.yml` archived, confirmed dead).

### Deprecated / Reassigned

| Agent | Status | Replaced by |
|-------|--------|-------------|
| Hermes CLI (orchestration tool) | Retired 2026-07-16 | OpenCode CLI (same underlying model, deepseek-v4-flash) |
| hermes nemotron | Reassigned | OpenCode deepseek-flash (frontend primary) + Kimi (escalation) |
| Antigravity | Legacy reference (v3.0) | OpenCode deepseek-flash |
| Grok | Legacy reference (v3.0) | DeepSeek Pro |
| Nemotron (`nemotron-3-ultra-550b-a55b`, distinct from "hermes nemotron" above) | Legacy — described in now-archived `.context/AGENT.md` system (June/July 2026 generation) as active frontend owner | OpenCode deepseek-flash + Kimi. Confirmed superseded — do not treat `.context/AGENT.md` as current, see Context System Hygiene section |

---

## Routing Logic

### Zone 1 — Implementation

**Keywords**: generate, build, scaffold, boilerplate, refactor, "just give me"

**Flow**:
```
Builder → DeepSeek Pro review
```

**Builders**:
- Backend: OpenCode deepseek-flash
- Frontend: OpenCode deepseek-flash (escalate to Kimi for complex work)

### Zone 2 — Architecture

**Keywords**: design, critique, plan, tradeoff, learn, RCA, architecture, spec

**Flow**:
```
Claude Web design → DeepSeek Pro consensus → Builder implementation
```

**Default zone**: Zone 2 (add friction by default)

---

## CI/CD Pipeline

⚠️ **Current actual state (verified 2026-07-06, reconfirmed 2026-07-08): the branch-flow/approval-gate content below is target design,
not running infrastructure.** There is no `.github/workflows/` directory in the repo — no GitHub Actions exist. Deployments to testdrive/testbuild happen via direct VPS execution only (see Temporary Infrastructure Change above). Treat everything below as **design-to-implement**, except Gate 2, which is real and enforced today (see next section).

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
    → deploy to testdrive.epm.zubbystudio.site
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
- Self-hosted runner on VPS connects to `epm_test` database (design-only, not yet running as CI — but `epm_test` itself is now a real, working, provisioned database as of 2026-07-25)
- `epm_test` is a genuinely separate database within the existing PostgreSQL 15 instance (not a schema — see Locked Architectural Decisions)
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
- OpenCode builder: Never start backend work without contracts/specs and acceptance criteria
- Frontend builder: Never start frontend before APIs are stable
- Nothing merges directly to main — previous output never authorizes skipping review, and merge additionally requires Gate 2 PO sign-off
- **Specs before implementation is absolute** — no builder agent starts without a Claude-authored spec
- **HO numbers are pulled from the Pre-assigned HO numbers table, never self-assigned** — several numbering collisions/self-assignments have occurred across sessions (HO-042 double-assigned; an "HO-031" mistagging; self-assigned/renumbered entries during the F-022 backend review chain, HO-080→HO-081, a duplicate self-assigned "HO-080" deleted) — this remains an open discipline gap, not fully resolved

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
| F-013 Companies Page | Spec ready — pending implementation | `.context/feature-specs/F-013-companies-page.md` | TanStack React Table, company profile page. **Unconfirmed discrepancy**: `AGENT_LOG.md` claims this shipped 2026-07-05; never independently re-verified — see Repo-Hygiene Backlog |
| F-016 User Management | **Shipped — built out-of-process** | `.context/feature-specs/` (path convention corrected 2026-07-13 — `.docs/specs/` is Zubbyik's manual-reference copy, never read by agents; if this spec isn't already in `.context/feature-specs/`, it needs copying over) | ⚠️ One-off exception: DeepSeek Pro implemented directly, no Zone 2 review, justified by urgent credential-provisioning neeed. Logged 2026-07-05, retroactive HO-030. Does not set precedent. |
| F-011 Claims CSV Upload | **Deployed — upload test PASS** | `.context/feature-specs/F-011-claims-upload.md` (v1.1) | Unmatched CSV rows land as unresolved claims (holding_id=null, lifecycle_status=unresolved, raw_company_name populated). Resolve flow (`PUT /api/v1/claims/{id}/resolve`) works but lacks formal test coverage of the lifecycle_status transition — flagged HO-048, not yet written |
| F-010 Claims (absorbs F-008 Dividends) | **Shipped — deployed to testdrive** | `.context/feature-specs/F-010-claims.md` | ⚠️ One-off
exception: pulled ahead of Phase 3C sequence (Lovable template). Frontend `statusMap` reconciled against canonical `lifecycle_status` mapping this session — see HO-045/046 |
| F-007 NAV History | **Fully complete** — backend, frontend, backfill, and automated daily cron all shipped | `.context/feature-specs/F-007-nav-history.md` (corrected v2026-07-08) | Phase 1 backend via PR #7 (2026-07-13). Frontend Phase 2 (Recharts chart, range selector, coverage disclosure) shipped 2026-07-14/15 (HO-064/065) — default landing range set to 6M rather than 1Y to avoid a misleading near-single-holding data cliff in the pre-2026-01 period; NAV coverage disclosure (25/73 holdings, 34%) shown by default, not hidden. One-shot backfill (355 rows, 2025-03-04 to present) run and verified (HO-063 era). Daily automated snapshot via standalone `backend/scripts/daily_nav_snapshot.py` (OS cron, not n8n — n8n rejected as unstable/slow in this operator's hands, 2026-07-16) — runs at 17:00 UTC, writes `notes='cron_auto'` and an `admin_audit` entry with `performed_by=NULL` (HO-066). Known permanent gap: 48 of 73 active holdings have no price history at all (live NGX stocks, simply never manually entered) — tracked as a future closeable task, not a structural limitation. |
| F-INV-001 Initial Stock Cost Upload | Spec pending — **UNBLOCKED for spec authoring** | — | OQ-FINV-1/2 resolved: hybrid scope (both
CSV + manual form), null cost basis → zero-cost gain calc. Claude to draft spec next. |
| F-009 Transactions | Spec exists at `.context/feature-specs/F-009-transactions.md`, status PLANNED | `.context/feature-specs/F-009-transactions.md` | Missing from earlier versions of this table — added 2026-07-13. Hard prerequisite for any future XIRR/return-rate feature, since XIRR needs a full dated cash-flow ledger |
| ✅ F-017 — numbering collision RESOLVED (2026-07-16) | Was: two features both claiming F-017 | `.context/feature-specs/ARCHIVED-superseded/F-017-ai-chat-bot-superseded-by-F-022.md` | Old `F-017-ai-chat-bot.md` archived (HO-063). This document's F-017 (Remove editMode/Admin CRUD) is now the sole claimant of the number. |
| ✅ F-011 — numbering collision RESOLVED (2026-07-16) | Was: Claims CSV Upload vs. Rebalancing both claiming F-011 | `progress-tracker.md` updated | Claims CSV Upload keeps F-011 (shipped, extensively specced). Rebalancing renumbered to **F-023** in `progress-tracker.md` (had no spec file, so this was a table edit only, not a file rename) — HO-063. |
| F-024 Historical Cost Basis Upload, F-025 NGX Companies PDF Upload | Both ✅ Complete, shipped | `.context/feature-specs/F-024-cost-basis-upload.md`, `.context/feature-specs/F-025-ngx-companies-upload.md` | Renamed 2026-07-16 (HO-063) from non-standard `F-COST-BASIS.md`/`F-NGX-COMPANIES.md` — pure rename, no functional change. All dangling path references in `MASTER_CONTEXT.md` and the two `BUG-AT-*` files fixed in the same pass; feature-ID mentions (not file paths) left untouched as harmless. |
| F-026 Registrar Requirements & Document Tracker | **✅ Fully complete (2026-07-31)** — schema, backend, frontend, tests, and seed data all shipped; production verified clean | `.context/feature-specs/F-026-registrar-requirements-tracker.md` | Retroactively documents a pre-existing, undocumented registrar CRUD system built May 2026 (no spec, no HO history — surfaced via HO-089 investigation) and closes real gaps on top of it. New `company_registrars` many-to-many table (replaces single FK, supports co-registration), `registrars.jurisdiction`, `companies.security_type`, `registrar_requirements.due_date` — see Locked Architectural Decisions. New `dashboard-summary` and `global-tracker` endpoints power a redesigned `/registrars` (read-only dashboard, no add/edit/delete controls) and new `/settings/registrars` (all CRUD moved here, per the no-inline-editing convention). 11 new automated tests total (7 dashboard tests + 4 seed-script tests: idempotency, Seplat co-registration, Africa Prudential dual-entity, dynamic company-count relative invariant) — full suite now 166 passed, 4 xfailed, 8 xpassed. A route-ordering bug (`dashboard-summary` shadowed by `{id}`) was found and fixed during review. Production migration applied via direct psql (Alembic hung on lock contention) — a CHECK-constraint name drift between production and `epm_test` was caught and fixed (HO-096/097). **Seed data (13 registrars, 143 companies, 165 company↔registrar links) loaded via a repeatable, idempotent script** (`backend/scripts/seed_registrar_mapping.py`) covering Zubbyik's full NGX-wide mapping list — a real process incident occurred here: the script ran against production before the required stop-and-confirm step, using 5 incorrect manually-guessed tickers, producing 5 orphaned duplicate company rows (zero links/holdings on any of them — no real data was ever affected). Caught via ticker cross-check against production, fully investigated (HO-101–104), and cleaned up via soft-delete (HO-105/106) — see Historical Decision Log for the full incident writeup and the standing lesson recorded from it. 50 companies (the "Main Board, Growth Board & Small-Cap" group — confirmed a category label, not a real registrar) deliberately left unlinked rather than assigned a fake registrar; surfaced instead via a new `unmapped_companies` field on the dashboard so they stay visible as a concrete to-do. **Still deferred, not blocking, no dependency between them**: (1) email reminder infrastructure — no SMTP capability exists in the codebase yet; (2) `/settings/registrars` bulk CSV/markdown import endpoint. |
| F-022 AI-Assisted Interactive Chatbot | **✅ Complete — backend cleared for Gate 2/PR (2026-07-25)** | `.context/feature-specs/F-022-ai-chatbot.md` | Scoped narrowly to EPM only — a broader platform-agnostic version was floated and explicitly deferred to a separate future project (see multi-tenant EPM note below). RuleBasedRouter with 10 intents across 5 domains (NAV, Holdings, Sector, Claims, Companies, Price History), shared `extract_entities()` function, most-specific-first intent ordering, stateless clarification branch for recognized-entity-but-no-match cases, three-tier fallback (unmatched / entity-found-clarification / error), `chatbot_conversations` table with `extracted_entities` JSONB + `execution_status` enum. RBAC inherited directly from existing endpoint guards — confirmed there is no per-user ownership column (`holdings` has no `user_id`); this is a single-owner estate model where every authenticated user sees the same holdings, differentiated only by `holding_type`/role. A real sector cross-join bug was found during review (`selectinload` without an explicit `.join()` producing a cartesian product) and fixed, with a genuine real-DB integration-test regression proof (before/after: join removed → wrong count + SAWarning; join restored → correct count). 29 unit tests + 1 real integration test added, zero regressions (155 passed, 4 xfailed, 8 xpassed baseline). Frontend widget (ported from Lovable component `epmaide-insight/`, hardened, mounted at `__root.tsx`) has a `FIXME: F-022` marker ready for a one-line swap from `mockAnswer()` to the real endpoint once this clears Gate 2. Zone 2 consensus (DeepSeek Pro review) was explicitly waived by Zubbyik for this feature's backend, cost/token reasons — Claude Web sole reviewer. This review also surfaced and fixed a separate, larger infrastructure gap — see `epm_test` / baseline migration entries in Locked Architectural Decisions and Historical Decision Log. |
| F-017 Remove editMode / Admin CRUD | Spec to write | — | Unblocked now that F-016 shipped; much of the inline-editing cleanup already done ahead of schedule via HO-040/041 |
| F-003b Price entry v2 | Spec to write | — | After F-017 |
| F-006b Dividends v2 | Spec to write | — | After F-017, parallel with F-003b — scope overlap with shipped F-010 to be reconciled when
spec is written |
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

### ⚠️ Forward Pointer — Phase 3E (Production Cutover): Multi-Tenant EPM Idea Capture

**Before Phase 3E (Production Cutover) is considered closed, raise this
conversation with Zubbyik if it hasn't already happened**: a separate,
entirely different project — a multi-tenant/multi-user version of EPM,
distinct from this single-estate build — was floated on 2026-07-16 and
deliberately deferred rather than explored then, to keep this project's
scope lean. Zubbyik asked that this be revisited specifically once EPM
v2's current build reaches its final task, not before. If a fresh
session reaches Phase 3E and this note hasn't been raised yet, raise it
before calling the phase complete — do not let this quietly drop, and do
not start scoping it on your own initiative before that checkpoint.

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
    chatbot/{unit,integration}/
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

### Test Suite Health (added 2026-07-13, updated 2026-07-25)

**Current status: 166 passed, 4 xfailed (all intentional/tracked), 8 xpassed (all `TestTransactionSchema`, `xfail(strict=False)` pending F-009 — expected behavior, not a regression), 0 failed, 0 errors.** Baseline was 155/4/8 after F-022; +7 from F-026's registrar dashboard test suite (HO-093); +4 from F-026's seed-script test suite (HO-099: idempotency, Seplat co-registration, Africa Prudential dual-entity, dynamic company-count invariant).

This section originally existed because MASTER_CONTEXT previously described the testing stack without disclosing that most of it was silently broken (2026-07-12 discovery: 11 of 18 pytest-collectable files failed on import, a leftover from the Owl Alpha → flat-`models.py` refactor). That was fully remediated by 2026-07-13 (see Historical Decision Log, v4.4 entry). Since then:

| What | Result |
|------|--------|
| F-022 chatbot tests added | 29 unit tests (`tests/unit/test_chatbot.py`) covering entity extraction, three-tier fallback/dispatch, and all 10 intent handlers via mocked sessions |
| F-022 integration test added | `tests/integration/test_chatbot_sector.py` — a genuine real-DB regression test for the sector cross-join bug, proven via before/after (join removed → fails with cartesian-product SAWarning; join restored → passes) |
| Mocked-test limitation confirmed directly | A first attempt at a "join-fix regression test" used a generic mocked session that returned a hardcoded fixture regardless of the constructed query — proven incapable of detecting the actual bug. Replaced with the real integration test above. Lesson: mocked sessions cannot verify SQL-construction correctness (joins, cartesian products); only a real query against real rows can. |
| `epm_test` database | Fully provisioned as a real, separate database (see Locked Architectural Decisions) — integration tests now run against it directly, not the retired schema-swap pattern |
| Migration chain | Now reproducible from empty via `000_baseline_production_schema.py` — previously failed with `UndefinedTableError` on `holdings` because the chain assumed an uncommitted `init_db.sql` base |
| `calculate_dividend_yield` | Still deferred as `F-P4-05` / `BUG-HOLD-DIVYIELD-001` (unchanged since v4.4) |
| Integration/contract/DB tests generally | No longer blocked on missing `DB_HOST` — root cause (asyncpg not supporting `?options=` query-param search_path syntax, plus missing env vars in the container) fixed via `connect_args={"server_settings": {...}}` and `ASGITransport` for httpx 0.28.1 compatibility (HO-077) |



| Test ID | Status | Notes |
|---------|--------|-------|
| DASH-VIEW-FE-E2E-001 | ✅ PASS | Sector allocation + charts |
| DASH-VIEW-FE-SMK-001 | ✅ PASS | Theme toggle |
| DASH-VIEW-FE-SMK-002 | ⏳ OPEN — no longer blocked | BUG-DASH-NOTIFY-001 — bell/useActionItems. F-016 dependency resolved long ago; ready to pick up whenever prioritized, not formally scheduled yet |
| HOLD-UPDATE-FE-E2E-001 | CLOSED | Superseded by HO-023 — inline editing removed |
| HOLD-VIEW-BE-E2E-001 | xfail | Blocked pending F-INV-001 |
| PRIC-UPDATE-BE-E2E-001 | ✅ PASS conditional | Price write OK; E2E chain blocked by F-INV-001 |
| SEC-JWT-BE-SEC-001 | ✅ PASS | JWT tamper + missing cookie |
| SEC-ROLE-BE-SEC-001 | xfail | Rename readonly_http_client → user_http_client; F-016 required |
| INF-DOCKER-SMK-001 | ✅ PASS | Staging API + frontend smoke |
| AT-004 (A01–E02, 14 cases) | ✅ 14/14 PASS | Gate cleared 2026-07-07 — see Historical Decision Log for B04b/SUPERADMIN fix details |
| AT-005 (null-holding rendering, 5 AC) | Drafted, not yet run | HO-045/048 — must pass before F-011's unresolved-claims path is considered fully verified |
| CHAT-EXTRACT/DISPATCH/HANDLER-UNIT (29 cases) | ✅ 29/29 PASS | F-022 chatbot unit suite, `tests/unit/test_chatbot.py` |
| Sector cross-join regression (integration) | ✅ PASS | `tests/integration/test_chatbot_sector.py`, proven via before/after join-removed/restored evidence |

---

## Open Questions (Product Owner — Zubbyik must answer)

*(none currently open as of 2026-07-25 — all resolved, see Resolved Questions Log)*

### Resolved Questions Log

| ID | Question | Answer | Resolved | Notes |
|----|----------|--------|----------|-------|
| OQ-F016-1 | Deactivated users' portfolios: hidden or read-only? | **Hidden** — from other USERs' views/aggregates; visible to ADMIN/SUPERADMIN via audit trail | 2026-07-05 | Answered during out-of-process F-016 build; reconfirmed independently HO-042 |
| OQ-F016-2 | Account creation: admin-only or email invitation flow? | **Admin-only** — no email invite flow | 2026-07-05 | Same as above; reconfirmed HO-042/047 |
| OQ-F007-3 | Non-trading days: store carry-forward NAV or skip entirely? | **Carry-forward NAV** | 2026-07-07 | Matches pre-existing locked decision — no new work implied |
| OQ-FINV-1 | Initial stock costs: CSV upload or manual form? | **Hybrid — both ship** | 2026-07-08 | Doubles spec surface vs single-method design; confirmed acceptable |
| OQ-FINV-2 | All holdings need cost basis, or only specific portfolios? | **Optional/nullable per holding** — inherited stock, no cost paid | 2026-07-08 | New rule: null cost basis → gain calculated against zero, never excluded |
| OQ-F022-TEST-DB | `epm_test`: provision as a real separate database, or formally accept schema-based isolation as the locked pattern? | **Provision `epm_test` as a real, separate database** (Option 1/A) | 2026-07-25 | Rationale: schema-swap's safety depended entirely on a `search_path`/env-var mechanism that had already failed once; a separate database removes that failure mode structurally, at the cost of a second migration target to keep in sync |
| OQ-F022-MIGRATION | Migration chain repair: reconstruct historical `init_db.sql` intent, or commit a baseline from current real production schema? | **Baseline from current real production schema** (Option 1) | 2026-07-25 | Became `000_baseline_production_schema.py`, the new root of the chain; production required no changes since it was already at head |

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
| HO-054 | Hermes → Zubbyik (informal, direct chat, not filed as a document) | Complete | Raw `ls -la .context/AGENT*.md` — confirmed only `AGENT.md` and `AGENT_LOG.md` exist; `.context/AGENTS.md` (plural, referenced in `opencode.json`) does not exist on disk |
| — | — | — | *(remaining `.context/` files — `ai-workflow-rules.md`, `progress-tracker.md`, `code-standards.md`, `ui-context.md`, `current-issues.md`, `AGENT_LOG.md` — reviewed via direct paste, not formal HOs; dispositions in Context System Hygiene section)* |
| HO-055 | Hermes → Claude | Superseded by HO-057 | F-007 Phase 1 backend complete (initial version — `admin_audit` deviation not yet flagged) |
| HO-056 | — | **Unused — slot still open** | Pre-assigned for F-INV-001 implementation complete; F-INV-001 spec hasn't been written yet, so this hasn't been reached |
| HO-057 | Hermes → Claude | Received | F-007 Phase 1 complete (corrected) + test suite health audit — 11/18 files broken on import discovered |
| HO-058 | Claude → Hermes | Sent | Rulings on 6 broken import blocks — investigate before fixing |
| HO-059 | Hermes → Claude | Received (initially incomplete) | Blocks 1-3 + partial Block 5 fixed; blocks 4/5(remainder)/6 investigated but not yet applied despite prior ruling — required a follow-up prompt |
| HO-060 | Hermes → Claude | Received | Blocks 4, 5, 6 correctly applied — 117 pass, 8 xpassed, 0 failed |
| HO-061 | Hermes → Claude | Received | Dividend-yield deferred with tracking; 5 pre-existing failures fixed — **125 pass, 4 xfailed, 0 failed, 0 errors** |
| HO-062 | Hermes → Claude | Received | **PR #7 merged** — F-007 Phase 1 + full test remediation shipped via proper branch → PR → Gate
2 approval → merge flow |
| HO-063 | Hermes → Claude | Received | `.context/feature-specs/` cleanup — F-017-ai-chat-bot archived, F-COST-BASIS/F-NGX-COMPANIES renamed to F-024/F-025, `progress-tracker.md` Rebalancing renumbered to F-023, dangling path references fixed |
| HO-064 | Hermes → Claude | Received | F-007 frontend Phase 2 initial delivery — chart, range selector, coverage disclosure; two issues found (verification rigor on 2 ACs, misleading default-range cliff) |
| HO-065 | Hermes → Claude | Received | Both fixes applied — default range 1Y→6M, AT-F007-002/003 re-verified with real behavioral evidence, AreaChart-vs-LineChart deviation confirmed intentional |
| HO-066 | Hermes → Claude | Received | Daily NAV cron script shipped (`daily_nav_snapshot.py`, OS cron not n8n), `admin_audit.performed_by` made nullable, real test-run output confirmed |
| HO-067 | — | **Not sent** | DeepSeek Pro review of F-022 spec was drafted but never sent — Zubbyik waived it for this instance before it went out (case-by-case Zone 2 policy) |
| HO-068 | Hermes → Claude | Received | Housekeeping (`hermes_config.yml` + `epmaide-insight_bkp` archived) + chatbot component audit — mocked data layer, ~15 hardcoded color violations found, Bun-vs-npm confirmed a non-issue |
| HO-069 | Hermes → Claude | Received | Chatbot widget ported and hardened — dashboard shell excluded, colors fixed to CSS vars, null-safety added, mock isolated behind FIXME, confirmed rendering on multiple pages via `__root.tsx` mount |
| HO-071 | OpenCode → Claude | Received | F-022 backend design proposal — intent patterns, existing-function mapping, migration shape, RBAC-inheritance reasoning. Six refinements requested before implementation. |
| HO-072 | OpenCode → Claude | Received | F-022 backend implementation — RuleBasedRouter, 10 intents/5 domains, all 6 refinements applied. Review found: (1) sector cross-join bug — 1,672-row artifact from `selectinload` without `.join()`; (2) RBAC scoping question (later resolved as no-bug, single-owner model confirmed); (3) xpassed/xfailed count discrepancy vs. HO-061; (4) zero automated test coverage on new code |
| HO-074 | Claude → OpenCode | Sent | Remediation handover — sector bug fix, ownership-filter evidence request, raw pytest reconciliation, automated test suite requirement |
| HO-075 | OpenCode → Claude | Received | Sector bug fixed (root cause: `selectinload` ≠ join); RBAC confirmed no bug (no `user_id` column exists); xpass count explained (`TestTransactionSchema`, `strict=False`); 29 unit tests added — but the "join-fix regression test" was found to be a mocked test incapable of detecting the actual bug |
| HO-076 | Claude → OpenCode | Sent | Fix `DB_HOST`/test-DB setup, then replace the mocked regression test with a real integration test proven via before/after join-removed/restored evidence |
| HO-077 | OpenCode → Claude | Received | `DB_HOST` root cause fixed (asyncpg `?options=` syntax + missing env vars); real integration test written and proven — but used `estate_portfolio_test` schema-swap, not a real separate `epm_test` database (undocumented pre-existing pattern, not deliberate) |
| HO-078 | Claude → OpenCode | Sent | Zone 2 decision (Option A): provision `epm_test` as a real separate database; migrate conftest off schema-swap |
| HO-079 | OpenCode → Claude | Received | `epm_test` provisioned via manual `CREATE DATABASE` + `create_all` + `stamp head`; conftest migrated off schema-swap cleanly; regression test re-proven against real database — but schema provisioning method (`create_all`+`stamp` rather than real `alembic upgrade head`) and an inaccurate "auto-created on rebuild" claim both flagged for follow-up |
| HO-081 | Claude → OpenCode | Sent | Rebuild `epm_test` via real `alembic upgrade head` from empty (not `create_all`+`stamp`); correct the auto-provisioning claim (renamed from an initially-mislabeled "HO-080") |
| HO-082 | OpenCode → Claude | Received | `alembic upgrade head` from empty **failed** — `init_db.sql` base schema was never committed to the repo, a genuine disaster-recovery gap. Auto-provisioning claim corrected (Postgres init scripts only run on a genuinely empty volume). Three Zone 2 decisions raised: migration-chain repair path, `epm_test` interim state, legacy-table disposition |
| HO-083 | Claude → OpenCode | Sent | Zone 2 decision (Option 1): commit a baseline migration introspected from real production schema; stamp `epm_test` at head in the interim; legacy tables deferred indefinitely |
| HO-084 | OpenCode → Claude | Received | `epm_test` stamped at head; `000_baseline_production_schema.py` committed as new chain root; all 11 subsequent migrations made idempotent; validated from empty (12/12 migrations, 20 tables matching production); production required no changes (already at head) — but the `portfolio_summary` VIEW's baseline coverage was left unconfirmed |
| HO-085 | Claude → OpenCode | Sent | Confirm whether `portfolio_summary` view exists in production and is captured in the baseline migration |
| HO-086 | OpenCode → Claude | Received | View confirmed real in production, was missing from the baseline, added via `CREATE OR REPLACE VIEW` + re-validated from empty — **F-022 backend and the migration-chain repair both fully closed** |
| HO-088 | Claude → OpenCode | Sent | (Repurposed from reserved F-INV-001 slot) Investigate `registrars`/`registrar_*` tables — live feature or schema-only leftovers? |
| HO-089 | OpenCode → Claude | Received | Full live feature confirmed — models, 15+ endpoints, 10 frontend components, real production data (23 registrars), built May 2026 with zero spec/HO history |
| HO-090 | Claude → OpenCode | Sent | (Repurposed from reserved F-017 slot) `/registrars` dashboard frontend design handover — separated real mockup intent from AI-mockup gibberish |
| HO-091 | OpenCode → Claude | Received | F-026 schema/backend/frontend implemented — `company_registrars` table, `dashboard-summary`/`global-tracker` endpoints, redesigned `/registrars` + new `/settings/registrars`. Flagged: zero new tests, unclear production migration state, unconfirmed broken test file status |
| HO-092 | Claude → OpenCode | Sent | Remediation request — automated test coverage, confirm `test_registrars_integration.py` fix status, confirm production migration state |
| HO-093 | OpenCode → Claude | Received | 7 tests added (162 total), import fix confirmed, migration applied to production (71-row backfill) — but backfill count conflicted with HO-091's earlier "23 rows" claim |
| HO-094 | Claude → OpenCode | Sent | Reconcile 23-vs-71 backfill discrepancy; confirm production DDL is character-for-character identical to the migration file |
| HO-095 | OpenCode → Claude | Received | 23 was a mislabeled registrar count, not a backfill count (epm_test had zero companies at validation time); 71 confirmed as a perfect 1:1 backfill via raw queries; production DDL confirmed functionally identical except one auto-generated CHECK constraint name |
| HO-096 | Claude → OpenCode | Sent | Rename production's auto-generated CHECK constraint to match the migration file's explicit name — closes the epm_test/production drift found in HO-095 |
| HO-097 | OpenCode → Claude | Received | Constraint renamed, condition proven unchanged, full production-vs-epm_test comparison across all 7 constraints/indexes confirmed identical — **F-026 schema/backend/frontend fully closed** |
| HO-098 | Claude → OpenCode | Sent | (Repurposed from reserved buffer slot) Repeatable, idempotent seed script for the full NGX registrar/company mapping — 13 registrars, ~143 companies, entity-separation and co-registration rules, `unmapped_companies` dashboard addition for the "Main Board" category (confirmed not a real registrar) |
| HO-099 | OpenCode → Claude | Received | Seed script implemented, idempotency + entity-separation + co-registration tests added (166 total). **Process miss**: ran against production before the required stop-and-confirm step from HO-098, using 5 manually-guessed tickers — not caught at the time |
| HO-101 | Claude → OpenCode | Sent | Ticker-verification, epm_test-provenance, and test-assertion checks required before trusting the seed run; read-only production preview mode required going forward (self-assigned, pre-assigned table exhausted) |
| HO-102 | OpenCode → Claude | Received | 5 incorrect tickers found via production cross-check (real NGX tickers already existed under different symbols); confirmed the seed script had already run against production in the prior session — before this handover's checks, not after |
| HO-103 | Claude → OpenCode | Sent | Urgent — investigate possible duplicate company records from the unauthorized production run; explicit instruction not to clean up until the actual state was confirmed |
| HO-104 | OpenCode → Claude | Received | 5 orphaned duplicate rows confirmed (zero links, zero holdings on any — no real data affected); special-links count reconciled (1 co_registrar, "3" was a miscount conflating co_registrar + self-registration rows); run timeline confirmed as a genuine process miss, not just a sequencing gap — HO-098's stop-and-confirm step existed from the start and wasn't observed |
| HO-105 | Claude → OpenCode | Sent | Cleanup authorization — soft-delete the 5 orphaned duplicates; one-line confirmation requested on the third special link; process-miss recorded accurately for the log |
| HO-106 | OpenCode → Claude | Received | Cleanup confirmed (5 rows soft-deleted, `deleted_at` populated, no hard-delete); third special link confirmed as Africa Prudential's self-registration — **F-026 fully closed end to end, production verified clean** |

### Pre-assigned HO numbers

**Process fix (2026-07-31, v4.8)**: this table has now run dry twice
(once flagged in v4.6, again in v4.7/this version) purely from
under-sizing the block, not from a deeper process failure — F-026's full
review cycle alone consumed ~19 slots (HO-088 through HO-106) once its
seed-data and duplicate-cleanup incident is included. **New standing
rule**: when fewer than 5 unused slots remain in this table, the next
Claude Web session must extend it with a fresh block before continuing —
don't wait for exhaustion. Sizing this block larger (50 slots) accordingly.

| HO | Purpose |
|----|---------|
| HO-107 | Claude → OpenCode: F-017 (Remove editMode / Admin CRUD) spec delivery — long-deferred, due for pickup |
| HO-108 | OpenCode → Claude: F-017 implementation complete |
| HO-109 | Claude → OpenCode: F-INV-001 (Initial Stock Cost Upload) spec delivery, if/when resumed |
| HO-110 | OpenCode → Claude: F-INV-001 implementation complete |
| HO-111 | Claude → OpenCode: F-026 email reminder infrastructure (SMTP dependency) spec/kickoff, if/when prioritized |
| HO-112 | OpenCode → Claude: F-026 email reminder implementation complete |
| HO-113 | Claude → OpenCode: F-026 `/settings/registrars` bulk CSV/markdown import spec/kickoff |
| HO-114 | OpenCode → Claude: F-026 bulk import implementation complete |
| HO-115 | Claude → OpenCode: F-003b (Price entry v2) spec delivery |
| HO-116 | OpenCode → Claude: F-003b implementation complete |
| HO-117 | Claude → OpenCode: F-006b (Dividends v2) spec delivery |
| HO-118 | OpenCode → Claude: F-006b implementation complete |
| HO-119 | OpenCode → Claude: BUG-DASH-NOTIFY-001 fix complete |
| HO-120 | OpenCode → Claude: Repo-hygiene backlog findings (`claude_handovers/` duplicate check, `swarm-forge/` location, `original_intent/` staleness, F-013 live-status verification) |
| HO-121 | OpenCode → Claude: The ~39 unaccounted unlinked-companies check (F-026 Task 3 loose end, non-blocking) |
| HO-122–HO-155 | Reserved — general-purpose buffer for unplanned rulings/implementation reports, consumed in sequence as needed |
| HO-156 | Reserved — Phase 3E production cutover checkpoint / multi-tenant EPM idea-capture kickoff (do not use before Phase 3E is actually reached, per the standing forward-pointer note; supersedes the old HO-100 reservation, which is now retired unused) |

**Usage rule (unchanged)**: pull the next unused number from this table
in sequence for the relevant direction; do not self-assign. When a slot's
purpose no longer matches what's actually being sent, relabel it
explicitly in the HO document itself and note the relabeling in the
Handover Chain table — the same pattern already used for
HO-031/HO-034a/HO-034b and for F-026's HO-088/090 repurposing.

---

## Role Model (F-016)

| Role | Level | Capabilities |
|------|-------|-------------|
| SUPERADMIN | 30 | Full system access; can manage ADMINs; cannot be deactivated if last one |
| ADMIN | 20 | Manage USERs, price uploads, portfolio approvals; cannot touch other ADMINs |
| USER | 10 | Active holdings only, no admin section access — **not** per-user ownership: the `holdings` table has no `user_id` column, so every authenticated USER sees the same estate holdings, differentiated only by `holding_type` (e.g. USER doesn't see drafts). This is a single-owner estate portfolio, not a multi-tenant system. |

Permission inheritance: additive upward. SUPERADMIN inherits all ADMIN permissions; ADMIN inherits all USER permissions.

**Wording correction (2026-07-25)**: this table previously read "USER — Own portfolios and holdings only," which implied per-user ownership filtering that does not exist in this codebase. Corrected during F-022 backend review after this wording caused a legitimate false-positive RBAC concern to be raised and then resolved once the actual schema was confirmed. See Locked Architectural Decisions.

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
  - Self-assign HO numbers — pull from the Pre-assigned HO numbers table (open discipline gap as of 2026-07-25, see Handover Chain note)
  - Treat any file under docs/context-ARCHIVED-* or .context/ARCHIVED-* as current
  - Assume a mocked test proves a data-correctness/SQL-construction fix — only a real query against real rows can (F-022 sector-join lesson, 2026-07-25)
  - Apply a new baseline/root migration directly to production without an explicit reconciliation plan flagged back first (F-022 migration-chain repair, 2026-07-25)

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
  - "traefik.http.routers.SERVICE.rule=Host(`SUBDOMAIN.zubbystudio.site`)"
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
| `.context/AGENT.md` + `project-overview.md` + `architecture.md` + `ai-workflow-rules.md` | **Archived** → `.context/ARCHIVED-legacy-agent-system-2026-07/` | Entry point + support files for the pre-OpenAgile DeepSeek/Flash/Nemotron TDD-workflow generation (commits `3a9e58e`/`ebea483`, June–July 2026). `ai-workflow-rules.md`'s roster references are archived with the rest, but three of its practices were judged good and adopted separately into this document's Locked Architectural Decisions: RED-GREEN test discipline, one-feature-per-session, and three-layer (DB→API→UI) acceptance order. |
| `.context/{code-standards.md, ai-workflow-rules.md, ui-context.md, progress-tracker.md, current-issues.md}` | **Reviewed and resolved, 2026-07-13** | See individual dispositions below |
| `.context/code-standards.md` | **Keep live** as reference | Genuinely useful, current conventions (API envelope, Python/TS standards, commit format). One stale section — "Inline Editing Pattern (Cursor-Jump Prevention)" — needs removing/rewriting, since inline editing no longer exists (modal-based now) |
| `.context/ui-context.md` | **Keep live** as reference | Genuinely useful design tokens/patterns. Two stale sections need rewriting: "Edit mode toggle" and "Inline editing... InlineEditRow" language — both describe the pre-HO-023/040/041 pattern, need updating to the modal-based `EditHoldingModal` pattern |
| `.context/progress-tracker.md` | **Reviewed, several findings folded into this document** | Surfaced the F-011 and F-017 numbering collisions (see Feature Spec Standards table). Route-prefix table (`/admin/*`) confirmed stale — predates the `/settings/*` correction. `F-016` "Last HO: HO-026" reference is likely a mislabel (HO-026 was Hermes confirming HO-024, unrelated to F-016) |
| `.context/current-issues.md` | **No action needed** — gitignored local scratch, not committed, not governance | BUG-005 (bell/action
items, same as `BUG-DASH-NOTIFY-001`) should come off "deferred post-F-016" status now that F-016 has shipped |
| `.context/AGENT_LOG.md` | **Keep as-is** — append-only chronological log, low risk, no roster conflicts | No action needed |
| Root `AGENTS.md` | **Current** | Points solely at `.context/MASTER_CONTEXT.md`, `.context/feature-specs/`, `docs/handovers/` |
| `hermes_config.yml` (repo root) | **Archived** → `ARCHIVED-legacy-tooling/hermes_config.yml` | Confirmed leftover from before the OpenCode CLI switch, no longer used (2026-07-16) |
| `epmaide-insight_bkp/` (workspace root, sibling to `estate-portfolio/`) | **Archived** → `ARCHIVED-legacy-tooling/epmaide-insight_bkp` | Duplicate of the canonical `epmaide-insight/` (F-022 chatbot component source) — verified primary intact before archiving (2026-07-16) |

### Repo-Hygiene Backlog (surfaced 2026-07-16, not yet actioned)

A full `tree -L 2` of the workspace root surfaced several more items worth
tracking but not urgent enough to interrupt current feature work:

| Item | Concern | Status |
|------|---------|--------|
| `estate-portfolio/claude_handovers/` | Unclear whether this duplicates `docs/handovers/` or serves a different purpose | Not yet checked |
| `swarm-forge/` location | An earlier investigation (git status era) described it as `/home/zubbyik/openagile_2/swarm-forge/` (sibling of `openagile_2/`); the later full tree shows it nested under `egbuna_estate_account_streamlight/` instead — these two descriptions disagree | Not yet reconciled |
| `original_intent/` (workspace root — `agent_roles.md`, `Architecture_spec.md`, `constraints.md`, `decisions.md`, `execution_philosophy.md`, `FOUNDATION_VISION.md`, `model_routing.md`, `workflow_design.md`) | Likely founding/historical documents predating even the Owl
Alpha era — worth confirming nothing still reads them as live | Not yet checked |
| Stray root-level files (`test_pdf*.py` ×8, `test_regex*.py` ×3, `temp_daily.txt`, `temp_prices1/2.txt`, `cookies.txt`, `log_status.md`, `cron.log`) | General clutter, likely safe to clean up but not verified individually | Not yet actioned |
| `AGENTS_PROMPTS_AND_INSTRUCTIONS/` bug-triage and workspace-root handover files (`ANTIGRAVITY_PHASE2B_HANDOVER.md`, `CLAUDE_REVIEW_ANTIGRAVITY_HANDOVER_APR29.md`, `ESTATE_PORTFOLIO_FINAL_HANDOVER.md`, `ESTATE_PORTFOLIO_REBUILD_DESIGN.md`) | Historical, Antigravity-era — presumed dead but not formally archived | Not yet actioned |
| `F-013 Companies Page` status | `AGENT_LOG.md` states F-013 was implemented and deployed to testdrive on 2026-07-05, but this document's Feature Spec Standards table still shows it as "Spec ready — pending implementation." Never independently confirmed whether `/companies` actually renders on testdrive. | **Unconfirmed** — do not change the feature table status without checking first |

None of the above blocks current work — logged so it doesn't quietly become
a fourth "surprise parallel system" discovery the way the `docs/context/`
and `.context/AGENT.md` systems did earlier this session.
| `.context/AGENTS.md` (plural, was declared in project `opencode.json`) | **Confirmed does not exist** (HO-054, raw `ls -la`) | `opencode.json`'s `instructions` array has been corrected to remove this dangling reference and point only at `.context/MASTER_CONTEXT.md` |
| `/openagile_2/MASTER_CONTEXT.md` (v3.0) and `/openagile_2/docs/context/MASTER_CONTEXT.md` | **Out of scope** | Workspace-wide (all projects), not EPM-specific — separate governance question, not blocking EPM work |

**Rule going forward**: any report on repo/file state for governance
purposes includes raw command output, not a narrated summary — several
contradictions this session were traced directly to summaries that looked
complete but omitted the detail that mattered. This was reconfirmed twice
more during the F-022 backend review (a mocked test that claimed to be a
regression test but wasn't; an xpassed/xfailed count discrepancy that
needed raw reconciliation).

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

### Domain / DNS-Level Outage (added 2026-07-16 after a real incident)

If a service is unreachable with SSL errors (`PR_END_OF_FILE_ERROR`,
`SSL_ERROR_UNRECOGNIZED_NAME_ALERT`) and nothing in the deployment history
explains it, **do not assume compromise or a bad deploy first** — check
the mundane cause before the alarming one:

```
1. Check whether the domain itself is still registered and pointed at
   Cloudflare (or your DNS provider) — a registrar-level expiration
   silently swaps nameservers to a parking page, which produces SSL
   errors that look identical to a server-side problem
2. curl -sI https://the-domain/ — look at what IP/host actually answers,
   compare against the expected VPS IP
3. Only after ruling out DNS/registrar issues, proceed to the standard
   Production Outage steps above
```

This happened for real on 2026-07-15/16: `zubbystudio.shop` expired at
the registrar, silently redirecting all its subdomains to a parking page,
before anyone had touched a deployment. Extended debugging across
Cloudflare support and server-side checks preceded the correct diagnosis
— this protocol exists so the next occurrence (on any domain) is faster
to identify.

### Database Rebuild-From-Empty (new, added 2026-07-25)

If `estate_portfolio` (or any environment) ever needs to be rebuilt from
nothing — new infrastructure, disaster recovery, or a fresh test database:

```
1. CREATE DATABASE <name>
2. alembic upgrade head  — this now works from a genuinely empty database,
   via 000_baseline_production_schema.py (the new chain root, introspected
   directly from live production, includes all 20 tables and the
   portfolio_summary VIEW)
3. Confirm resulting schema matches production (table list + view list)
4. Do NOT use Base.metadata.create_all + alembic stamp head as a
   substitute for step 2 except as a genuinely temporary unblock —
   create_all reflects current models.py, not the authoritative migration
   history, and does not detect drift between the two
```

Prior to 2026-07-25, this path did not work — `alembic upgrade head` from
empty failed because the chain assumed an `init_db.sql` base that was run
once against production and never committed to the repo. This was
discovered while provisioning `epm_test` for F-022's test suite and is
now fixed (see Locked Architectural Decisions).

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
- Netcup VPS: updated in-situ by OpenCode/builder agents
- Claude Web project: manually copied by Zubbyik after each update
- Gitea: committed to repo as `.context/MASTER_CONTEXT.md`

---

## Historical Decision Log

### EPM v2

**2026-07-31: MASTER_CONTEXT.md v4.8 — F-026 fully closed (seed data + production duplicate-cleanup incident), HO numbering table properly re-sized**

- **F-026 is now fully complete end to end**: schema, backend, frontend, tests, and seed data all shipped, with production verified clean after a real incident (below). 13 registrars and 143 companies from Zubbyik's full NGX-wide mapping list are now seeded via a repeatable, idempotent script (`backend/scripts/seed_registrar_mapping.py`) — 165 `company_registrars` links total, including the confirmed Seplat co-registration (DataMax primary + Computershare UK co_registrar) and the Africa Prudential Plc self-registration (two independent records, company and registrar, linked per the entity-separation rule).
- **A real production incident occurred and was fully resolved**: the seed script ran against production before the stop-and-confirm step its own originating handover (HO-098) specified, using 5 manually-guessed tickers for real NGX-listed companies that already existed in production under different, correct tickers (e.g. `ENAMELWARE` guessed vs. the real `NIGENAMEL`). This created 5 duplicate company rows. **No real data was affected** — all 5 duplicate rows were confirmed orphaned (zero `company_registrars` links, zero `holdings`) before cleanup, meaning nothing downstream ever pointed at the wrong-ticker records. Caught via a direct ticker cross-check against production (HO-102), fully investigated with raw queries rather than inference (HO-103/104), and resolved via soft-delete (HO-105/106) — never a hard delete, consistent with the project's standing soft-delete convention.
- **Standing lesson recorded**: a "run against test first, confirm, then run against production" instruction needs to be an actual pause with real back-and-forth confirmation between test and production runs — not something narrated as having happened after production was already touched in the same session. This is a close cousin of the project's existing "raw output, not narrated summaries" rule, extended specifically to sequencing/gating instructions, not just evidence claims.
- **The "Main Board, Growth Board & Small-Cap Registrars" ambiguity was resolved correctly**: confirmed to be a category label, not a real registrar entity. Rather than inventing a placeholder registrar (which would have corrupted the feature's core purpose — knowing exactly who to contact), the ~50 companies under that heading were seeded as ordinary `companies` rows with **no registrar link**, and a new `unmapped_companies` field was added to the dashboard-summary endpoint so these stay visible as a concrete, honest to-do rather than silently disappearing from the data.
- **Full suite now 166 passed, 4 xfailed, 8 xpassed** (up from 155 at F-022's close) — 7 tests from the dashboard work, 4 from the seed script (idempotency, Seplat co-registration, Africa Prudential dual-entity, and a dynamic company-count relative invariant rather than a hard-coded number).
- **Pre-assigned HO numbers table has now run dry twice** (flagged in v4.6, again by this version) purely from under-sizing each block, not a deeper process failure — F-026's full cycle alone (design through seed-data cleanup) consumed roughly 19 slots. Fixed properly this time: the table is resized to 50 slots, and a new standing rule requires extending it proactively once fewer than 5 slots remain, rather than waiting for exhaustion.
- Two loose ends logged, not blocking: (1) ~39 companies in production remain unaccounted for after the seed effort and duplicate cleanup — not concerning, just not yet explained; (2) F-026's two remaining deferred items (email reminder infrastructure, `/settings/registrars` bulk import) are unchanged from v4.7, still explicitly decoupled from each other and from everything else that's now shipped.

**2026-07-28: MASTER_CONTEXT.md v4.7 — F-026 (Registrar Requirements & Document Tracker) schema/backend/frontend complete**

- **A fully-built, undocumented registrar CRUD system was discovered** during a routine "what's the gap" review (HO-088/089): `registrars`, `registrar_requirements`, `registrar_documents`, `registrar_contact_fields` tables, a full backend router (15+ endpoints, file upload/download, versioned document history, company linking), and 10 frontend components — all built and shipped to production in May 2026, with zero spec file and zero HO history. Same pattern as F-016's undocumented out-of-process build. Retroactively documented as **F-026**.
- **Real gaps closed on top of the existing system**: a `company_registrars` many-to-many join table now replaces the single `companies.registrar_id` FK, specifically to support co-registered companies (Seplat Energy Plc: DataMax Registrars as primary, Computershare UK as co_registrar — a single FK structurally cannot represent this). `registrars.jurisdiction` (nigeria/international) and `companies.security_type` (equity/etf/mutual_fund) added as new classification columns. `registrar_requirements.due_date` added to support a hybrid visual+email reminder system (email side deferred — see below).
- **Entity-separation rule established**: any entity that is both a listed company and a registrar (e.g. Africa Prudential Plc) is represented as two fully independent records, never merged or self-referenced — matches how such entities are actually treated ("to the taxman," per Zubbyik) despite sharing a parent organization informally.
- **`/registrars` redesigned as a read-only summary dashboard** (Requirements Completion ring, Top Action Items, Registrar Health breakdown, a paginated Global Requirements Tracker table) with **no add/edit/delete controls anywhere on the page** — all mutation moved to a new `/settings/registrars`, consistent with the project's standing no-inline-editing convention. Design handover (HO-090) explicitly separated real layout intent from an AI-generated mockup's placeholder gibberish (fake requirement names, fake due dates, a fake category-grouping sidebar) so none of it got built by mistake.
- **A route-ordering bug was found and fixed during review**: `dashboard-summary` was registered after `registrars/{id}`, causing FastAPI to match it as the `{id}` path parameter (422 error).
- **7 new automated tests added** (162 total suite, up from 155) covering completion-percentage math, registrar-health categorization, tracker pagination, and — notably — the backfill logic via a genuine **relative invariant** (creates fixture data with and without a registrar link, asserts only the correct rows get backfilled) rather than a hard-coded row count. This is the correct pattern the project learned to require after F-022's mocked-test incident.
- **A real backfill-count discrepancy (23 vs. 71) was caught and correctly reconciled**: the "23" in the initial implementation report turned out to be a mislabeled registrar count, not a backfill count — the `epm_test` validation run at that time had zero companies, so it never actually exercised the backfill logic against real data volume. Production's real backfill (71 rows) was proven via raw queries to be a perfect 1:1 mapping against `companies.registrar_id` — zero orphaned rows, zero missing rows.
- **A genuine, small production/`epm_test` schema drift was found and fixed**: production's DDL was applied via direct psql (Alembic hung on lock contention against the live `companies` table), and — despite an initial claim of exact equivalence — the resulting CHECK constraint ended up with Postgres's auto-generated name (`company_registrars_role_check`) instead of the migration file's explicit name (`chk_company_registrar_role`). Same category of problem as the earlier baseline-migration gap, just at constraint-name granularity. Fixed via `ALTER TABLE ... RENAME CONSTRAINT`, verified inert (same check condition before/after), and a full production-vs-`epm_test` comparison across all 7 constraints/indexes confirmed no further drift exists.
- **Deferred, by deliberate choice, not oversight, and explicitly decoupled from each other**: (1) seed data — the ~13 registrar groups / ~140 companies from Zubbyik's full NGX-wide mapping list, to be loaded via a one-off script, **not gated on** item (3); (2) email reminder infrastructure — no SMTP capability exists anywhere in the codebase yet, needed before the hybrid visual+email reminder design (Section 5.1 of the F-026 spec) can actually send anything; (3) `/settings/registrars` bulk CSV/markdown import endpoint — can be built at any time, is not a prerequisite for loading the seed data.
- **Pre-assigned HO numbers table consumed and re-emptied**: the HO-087–HO-100 block populated in v4.6 was almost entirely used by this single feature's implementation-and-remediation cycle (HO-088 through HO-097, including two slots deliberately repurposed from their original F-INV-001/F-017 assignments once priorities shifted). Needs a fresh block before the next feature starts — see Pre-assigned HO numbers table note.

**2026-07-25: MASTER_CONTEXT.md v4.6 — F-022 backend complete, epm_test provisioned, migration chain made reproducible from empty**

- **F-022 AI Chatbot backend is complete and cleared for Gate 2/PR.** RuleBasedRouter shipped with 10 intents across 5 domains, shared entity extraction, most-specific-first intent ordering, a stateless clarification branch, three-tier fallback, and the two new `chatbot_conversations` logging columns (`extracted_entities` JSONB, `execution_status` enum) — all per the six refinements requested during design review (HO-071). RBAC is inherited directly from existing endpoint guards; confirmed during review that `holdings` has no `user_id` column, so this is genuinely a single-owner estate model, not a multi-tenant one with a filtering gap — the Role Model table's prior wording ("Own portfolios and holdings only") was misleading and has been corrected.
- **A real sector cross-join bug was found and fixed**: `handle_hold_by_sector` used `selectinload(Holding.company)` plus a `.where(Company.sector...)` filter with no explicit `.join()` — `selectinload` issues a *separate* query for the relationship rather than joining the main query, so the sector filter ran against an unconstrained cartesian product (2 holdings × 3 companies = 6 rows in the reproducing test case; 76 × 22 = 1,672 in the original report). Fixed with an explicit `.join(Company, Holding.company_id == Company.id)`.
- **A mocked "regression test" was found to test nothing**: the first attempt at locking in the join fix used a generic mocked session returning a hardcoded fixture regardless of the constructed query — proven incapable of ever failing even with the bug present. Replaced with a genuine real-database integration test, proven via explicit before/after evidence (join removed → wrong count + a real SQLAlchemy cartesian-product warning; join restored → correct count). **Standing lesson recorded**: mocked sessions cannot verify SQL-construction correctness; only a real query against real rows can.
- **`epm_test` is now a real, separate database** on the shared PostgreSQL 15 instance, replacing the older `estate_portfolio_test`-schema-within-`estate_portfolio` pattern (which had already caused one real outage — a `DB_HOST`/connection-config failure — and offered weaker isolation from production data). This was a deliberate Zone 2 decision (Option A/1) over the cheaper alternative of just formally blessing the schema-swap pattern.
- **A genuine disaster-recovery gap was found and fixed while provisioning `epm_test`**: `alembic upgrade head` against a truly empty database failed, because the migration chain was designed additive-only on top of an `init_db.sql` base schema that was run once against production and never committed to the repo. This meant production's schema had no reproducible origin in version control at all — not a hypothetical risk, a real one. Fixed by introspecting the actual current production schema directly and committing it as a new baseline migration (`000_baseline_production_schema.py`), including a previously-untracked `portfolio_summary` VIEW that the first baseline draft missed. Production itself required zero changes — it was already at head; the fix only makes the *chain* reproducible from empty going forward, for test databases and true disaster recovery.
- Two confirmed-dead legacy tables (`audit_logs`, `communication_logs`, Owl-Alpha-era, no ORM models or code references) were included faithfully in the baseline for accuracy but deliberately left untouched otherwise — no cleanup action taken.
- **HO numbering discipline slipped further this session**: HO-070 through HO-086 were generated sequentially outside the Pre-assigned HO numbers table, including one duplicate self-assignment that had to be renamed/deleted mid-stream. Flagged explicitly as an open gap rather than silently normalized — the Pre-assigned table should be extended with real slots for the next block of work.
- Full test suite baseline is now **155 passed, 4 xfailed, 8 xpassed, 0 failed** (up from 125/4/0 at v4.5, reflecting the 29 new chatbot unit tests plus 1 new integration test).

**2026-07-16: Domain migration — zubbystudio.shop → zubbystudio.site (registrar-level expiration, not a malfunction)**
- `zubbystudio.shop` expired at the registrar during this session, silently swapping nameservers away from Cloudflare to a parking page (`216.227.142.171`, FDCservers.net) — every `*.shop` subdomain became unreachable with SSL errors that initially looked like a possible compromise. Root cause correctly identified as domain expiration, not a server-side or code issue, before any rollback was attempted.
- Renewal cost for `.shop` was prohibitively higher than a fresh `.site` registration — a budget decision, not a technical one. **`.shop` is now permanently retired; `.site` is the intended permanent domain going forward for everything eventually, though only EPM has actually migrated as of this version.**
- EPM's staging/testbuild URLs, Traefik labels, CORS origins, and code references fully migrated to `.site` and verified working (cert
issued, login/NAV/holdings all rendering).
- **Other services — n8n, Gitea, Wiki.js, OpenProject, Woodpecker, and the Frappe/ERPNext education site — have NOT migrated and are very likely unreachable at their `.shop` URLs as of this version.** Zubbyik has explicitly deprioritized this — not treated as urgent unless raised.
- New Emergency Protocol added (see that section) for diagnosing domain/DNS-level outages going forward, since this exact failure mode
produced SSL errors indistinguishable from a server compromise until DNS was checked directly.

**2026-07-16: MASTER_CONTEXT.md v4.5 — F-007 fully complete, F-022 spec + frontend shipped, feature-spec renumbering, repo-hygiene backlog opened**
- **F-007 NAV History is now fully complete**: frontend Phase 2 shipped (Recharts chart, range selector, coverage disclosure), historical backfill run (355 rows), and daily automated snapshot via OS cron (`daily_nav_snapshot.py`) rather than n8n — n8n was rejected on direct operator experience ("really unstable and slow"), reversing the earlier recommendation to use it. A real, permanent data gap was found and disclosed rather than hidden: only 34% of active holdings (25/73) have any price history at all, so NAV coverage is shown plainly on every NAV display, not smoothed over. A misleading near-single-holding "cliff" in the pre-2026-01 backfilled data was caught and fixed by changing the default landing range (1Y→6M) before it shipped to a real user.
- **F-022 AI Chatbot**: fully specced, narrowly scoped to EPM only after an initial pitch to make it platform-agnostic across estate/insurance/marketing verticals was deliberately deferred to protect scope discipline. All three Open Questions resolved directly by Zubbyik (fixed fallback message, all five data domains from day one, server-side-only conversation log). Frontend widget — a pre-built Lovable component (`epmaide-insight/`) — audited, ported, and hardened (mocked data isolated behind a `FIXME`, ~15 hardcoded colors converted to CSS tokens, null-safety added, confirmed rendering on multiple pages via a single app-shell mount). Backend not yet built.
- **New standing decision**: Zone 2 consensus (DeepSeek Pro review) may be waived case-by-case at Zubbyik's explicit request for cost reasons — remains the *default*, not a blanket policy change. First applied to F-022's backend clearance, with Claude Web as sole reviewer for that instance.
- **`admin_audit.performed_by` made nullable** — needed for the NAV cron script's automated, actor-less audit entries; human-triggered
actions still require a real FK.
- **Feature-spec numbering fully resolved**: the F-017 and F-011 collisions flagged in v4.4 are closed — old `F-017-ai-chat-bot.md` archived, `F-COST-BASIS.md`/`F-NGX-COMPANIES.md` renamed to `F-024`/`F-025`, Rebalancing renumbered to `F-023` in `progress-tracker.md`. All dangling path references fixed in the same pass.
- **Multi-tenant EPM idea** (a separate, distinct future project — not part of this codebase) was raised, deliberately deferred per Zubbyik's own instruction to keep decisions lean. A forward-pointer reminder is now locked into this document's Phase 3C/3E section so it
surfaces on its own before Production Cutover is called complete, without relying on anyone's memory.
- **New repo-hygiene backlog opened** from a full workspace-root `tree` audit: several more items found (`claude_handovers/` possible duplicate of `docs/handovers/`, a location discrepancy for `swarm-forge/` between two separate investigations, an `original_intent/` historical doc set, general root-level clutter, and an unconfirmed F-013 Companies Page status discrepancy between `AGENT_LOG.md` and this document's own feature table). None block current work; logged explicitly so none of them quietly become a repeat of this session's earlier parallel-system surprises.
- Two more items archived under the established pattern (move, don't delete): `hermes_config.yml` (confirmed dead tooling) and `epmaide-insight_bkp/` (confirmed duplicate).

**2026-07-13: MASTER_CONTEXT.md v4.4 — F-007 Phase 1 shipped, test suite remediated, context cleanup consolidated**
- F-007 NAV History Phase 1 (backend) shipped via **PR #7**, merged by Zubbyik through a clean branch → PR → Gate 2 approval → merge flow — the first time this session the full merge-gate criterion was observed working correctly end to end, as part of the OpenCode CLI trial.
- Test suite remediation completed: discovered 11 of 18 backend test files were broken on import (Owl Alpha → flat-`models.py` refactor debt, predating this session). All 6 import-error blocks fixed; 3 functions with live consumers rewritten against real code rather than resurrecting removed abstractions; 2 functions (rebalancing gap, WHT deduction) retired — no consumer exists for either; 5 additional pre-existing failures fixed. Final state: 125 pass, 4 xfailed (intentional/tracked), 0 failed, 0 errors.
- **Genuine live bug found during remediation, not a test artifact**: `calculate_dividend_yield` is hardcoded to `0.0` in production despite the frontend rendering a real column for it. Deferred as standalone future feature `F-P4-05`, tracked as `BUG-HOLD-DIVYIELD-001`.
- **Confirmed intentional, not a bug**: `seed_admin.py` overwrites the admin password on every re-run — deliberate design for GitHub Secret rotation recovery. Locked as a standing decision so this doesn't get re-flagged as a regression by a future session.
- `admin_audit` table ratified as built ahead of F-019 (schema decided during F-007 implementation, not rolled back — a working table already existed).
- Two real feature-numbering collisions surfaced via `progress-tracker.md` reconciliation: **F-011** (this session's Claims CSV Upload
vs. Rebalancing) and **F-017** (editMode removal vs. an AI chatbot spec file) — both flagged in the feature table, neither yet resolved.
- All five previously-under-review `.context/` files (`code-standards.md`, `ui-context.md`, `progress-tracker.md`, `current-issues.md`, `AGENT_LOG.md`) reviewed and dispositioned — two kept live with noted stale sections needing a rewrite pass, one contributed the numbering-collision findings, one needs no action (gitignored scratch), one kept as-is (append-only log).
- Three practices adopted from the now-archived `ai-workflow-rules.md`: RED-GREEN test discipline, one-feature-per-session, three-layer (DB→API→UI) acceptance order.
- `.context/AGENTS.md` (plural) confirmed via raw `ls` to not exist — `opencode.json` corrected accordingly.
- Process note reinforced: HO-059 initially restated an investigation instead of confirming ruled-on fixes were applied, requiring a repeat prompt — same "narrated vs. raw/actual" failure mode as the earlier context-file confusion, just applied to code changes instead of file contents this time.

**2026-07-08: MASTER_CONTEXT.md v4.3 — Session close-out**
- AT-004 gate closure finalized: B04b (isEditing in `_app.holdings.tsx`) ruled a HO-023 violation (HO-040); fixed via `EditHoldingModal.tsx` replacing `InlineEditRow.tsx` (HO-041). **AT-004 final: 14/14 PASS.**
- Gate 2 established: GitHub branch protection on `main` (required PR, required Write-access approval via CODEOWNERS, no admin bypass). Two one-off bypass exceptions logged: HO-041's direct commit (predates Gate 2) and a second bypass on 2026-07-08 caused by an approval-account permission mixup (wrong account had Read, not Write access) — both accepted one-offs, not precedent.
- F-010/F-011 `lifecycle_status` reconciliation (HO-044/045/046): found the shipped frontend `statusMap` conflicted with F-010's own spec, AND found `lifecycle_status` was never backfilled for pre-existing rows (data-integrity risk, caught before causing visible damage). Canonical mapping ruled (spec's original mapping wins — "unclaimed" means owed-but-not-collected). Backfill run (9 seed rows, no visible impact yet since no approved/paid/rejected/lapsed rows existed). F-011 schema prep done: `holding_id` nullable, `raw_company_name`
added. Frontend refactored to read `lifecycle_status` directly.
- All five session-opened Open Questions resolved: OQ-F016-1/2 (reconfirming a 2026-07-05 resolution), OQ-F007-3, OQ-FINV-1 (hybrid CSV+manual), OQ-FINV-2 (null cost basis → zero-cost gain calc, new locked rule).
- F-011 unresolved-claims flow deployed and tested (HO-047) — unmatched CSV rows correctly land as unresolved claims; resolve endpoint
works but lacks formal lifecycle_status-transition test coverage (flagged, not yet written).
- Multiple stale/conflicting context systems discovered and cleaned up: `AGENTS_PROMPTS_AND_INSTRUCTIONS/specs/MASTER_CONTEXT_v4.md` (deleted, stubbed), `docs/context/*` (archived — defunct Owl Alpha/Nex N2/DeepSeek v4 roster, `bugs_open_cleanup` phase), `.context/AGENT.md` + support files (archiving — defunct DeepSeek/Flash/Nemotron TDD-workflow generation). Root `AGENTS.md` rewritten to point solely
at this file. Remaining `.context/` files (`ai-workflow-rules.md`, `progress-tracker.md`, `code-standards.md`, `ui-context.md`, `current-issues.md`) still under review as of this version — not yet ruled archive-vs-adopt.
- Orchestration note: Zone 1 builder sessions trialing OpenCode CLI in place of Hermes CLI (4-5 run trial) — no Agent Roster/model change, `deepseek-v4-flash` remains the underlying model.
- New standing rule: HO reports on repo/file state must include raw command output, not narrated summaries — traced several contradictions this session directly to this gap.

**2026-07-06: MASTER_CONTEXT.md v4.2 — v4.0/v4.1 reconciliation, legacy doc detached**
- Compared true `MASTER_CONTEXT_v4.0.md` (April 25, 2026 — "Master Prompt Framework" lineage) against v4.1 (EPM v2/Phase 3C lineage) against actual VPS state rather than assuming either doc.
- CI/CD: confirmed neither doc's pipeline design is actually running — no `.github/workflows/` exists. Annotated as target design, not
current reality.
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

**END OF MASTER_CONTEXT.md v4.8**
**File Maintainer**: Claude Web (Architect) — update after every major change
**Version Control**: `MASTER_CONTEXT: v4.8 — F-026 fully closed (schema/backend/frontend/tests/seed-data), production duplicate-cleanup incident investigated and resolved with zero data loss, unmapped_companies dashboard tracking added, Pre-assigned HO numbers table resized to 50 slots with a proactive-extension standing rule`
