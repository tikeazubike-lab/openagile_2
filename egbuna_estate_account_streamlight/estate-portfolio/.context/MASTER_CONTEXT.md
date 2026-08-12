# MASTER_CONTEXT.md — Single Source of Truth

**DO NOT EDIT WITHOUT HANDOVER PROTOCOL**

**Version**: 4.2
**Last Updated**: 2026-07-06
**Maintained By**: Claude Web (The Brain / Architect)
**Previous Version**: 4.1 (2026-07-05)

---

## ⚠️ Temporary Infrastructure Change (Active)

**Reason**: Developer workstation (Fedora 42 laptop) has crashed.
**Duration**: Temporary — reverts when workstation is restored.
**Status**: Code remains committed to GitHub; project is intact and pullable.

### What changed (temporary only)

| Area | Normal state | Temporary state |
|------|-------------|-----------------|
| Docker commands | Forbidden on local machine — GitHub Actions only | Permitted — executed directly on Netcup VPS server via SSH |
| Local execution | No Docker, no Python, no Node on Fedora | All execution done on VPS directly |
| Deployment trigger | git push → GitHub Actions → VPS | Direct VPS execution permitted until workstation restored |

### What did NOT change

- Code is still committed and pushed to GitHub
- CI/CD pipeline (GitHub Actions) remains the canonical deployment path
- All other infrastructure constraints remain in force
- This exception reverts automatically when the Fedora workstation is back

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

Frontend:
  - React 18
  - TypeScript
  - Tailwind v4
  - TanStack Router (URL-first routing)
  - TanStack React Table (data tables)
  - Recharts (charting)

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
| No editMode toggle | Role-based guards only, admin section for all CRUD | HO-023 permanent decision |
| `admin_audit` table | All CRUD operations logged here | Audit trail |
| `get_session()` naming | Function naming locked | Breaking change risk |
| Migrations | Additive only — `ADD COLUMN IF NOT EXISTS` | Never drop or rename in production |
| No new Postgres instances | Reuse shared PostgreSQL 15 only | Resource constraint |
| All monetary API values | Strings | Decimal precision |
| RuleBasedRouter first | For AI chatbot feature F-022 | Architecture decision |
| NAV carry-forward | Use most recent prior price when date missing | F-007 calculation rule |
| Deactivated user portfolios | Hidden — visible only to SUPERADMIN | OQ-F016-1, resolved 2026-07-05 |
| Account creation flow | Admin-only — no email invitation flow | OQ-F016-2, resolved 2026-07-05 |

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
| Codex / Owl Alpha | Test executor | — | Runs AT-XXX acceptance tests, reports via HO |
| hermes opencode-zen | Hermes governance | — | Governance plans, no implementation |

**Frontend escalation rule**: hermes deepseek-flash handles all frontend work. Escalate to Kimi k2.0 only for complex frontend build/implementation situations. Document the escalation reason in the handover.

### Deprecated / Reassigned

| Agent | Status | Replaced by |
|-------|--------|-------------|
| hermes nemotron | Reassigned | hermes deepseek-flash (frontend primary) + Kimi (escalation) |
| Antigravity | Legacy reference (v3.0) | hermes deepseek-flash |
| Grok | Legacy reference (v3.0) | DeepSeek Pro |

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

⚠️ **Current actual state (verified 2026-07-06): this entire section is target design, not running infrastructure.**
There is no `.github/workflows/` directory in the repo — no GitHub Actions exist. Everything below (branch flow, approval gate, self-hosted runner, `epm_test` isolation) is the intended pipeline once CI is rebuilt, not something currently enforcing anything. Deployments to testdrive/testbuild are happening via direct VPS execution only (see Temporary Infrastructure Change above), with no automated test gate in between. Treat every rule below as **design-to-implement**, not **currently-enforced** — when CI work resumes, this is the spec to build against, and test isolation strategy (schema vs. separate database) should be decided fresh at that point rather than assumed from either this doc or the retired legacy doc.

### Branch Flow

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
    → approval gate (/approve comment — three-factor: authorized commenter
                     + ci-verified label + HEAD SHA staleness check)
    → deploy to production
    → e2e tests
```

### CI Rules

- No direct merge to main — review required every cycle
- Self-hosted runner on VPS connects to `epm_test` database
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

### Execution Path (temporary — workstation offline)

```
Direct VPS execution via SSH permitted
    ↓
Code still committed to GitHub
    ↓
GitHub Actions still canonical deployment path
```

### Anti-Patterns (permanent — even during temporary exception)

```
❌ Bypass Traefik — all HTTP/HTTPS must go through it
❌ Create new Postgres instance
❌ Use ephemeral DB containers in CI
❌ Unquoted SSH heredocs
❌ System pip installs (use containers or isolated envs)
❌ Direct merge to main without review
❌ Implement before spec exists (Zone 1 cannot start without AT-XXX criteria)
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
| Builders | Claude Web | `HO-*.md` | Structured, numbered, status-aware |
| Claude Web | User | Decisions, tradeoffs, clarifications | Max 3 questions at once |

### Handover Rules

- DeepSeek Pro: Never implement before design approval
- hermes deepseek-flash: Never start backend work without contracts/specs and acceptance criteria
- Frontend builder: Never start frontend before APIs are stable
- Nothing merges directly to main — previous output never authorizes skipping review
- **Specs before implementation is absolute** — no builder agent starts without a Claude-authored spec

---

## Feature Spec Standards

### Spec File Convention

```
F-NNN-feature-name.md
Location: .context/feature-specs/ or .docs/specs/
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
| F-016 User Management | **Shipped — built out-of-process** | `.docs/specs/F-016-user-management.md` | ⚠️ One-off exception: DeepSeek Pro implemented directly, no Zone 2 (Claude Web) design review. Urgency: security requirement to provision individual login credentials. See Historical Decision Log 2026-07-05. |
| F-010 Claims (absorbs F-008 Dividends) | **Shipped — deployed to testdrive** | `.context/feature-specs/F-010-claims.md` | ⚠️ One-off exception: pulled ahead of Phase 3C sequence (Lovable template made it cheap to build). Does not set precedent — standing gate order below still applies to F-INV-001/F-007/F-017/F-003b/F-006b. |
| F-011 Claims CSV Upload | **Implementation complete — awaiting AT-004 merge gate** | `.context/feature-specs/F-011-claims-upload.md` | v1.1 with HO-036 conditions implemented. 7/7 phases: migration, fuzzy matcher, upload endpoints (preview/commit/template), registrar_id filter, frontend upload tab, registrar widget. All deployed to testdrive. Merge blocked on AT-004 14/14 green. |
| F-007 NAV History | Spec complete | `.docs/specs/F-007-nav-history.md` | Gherkin SC-025–031 written; OQ-F007-3 open |
| F-INV-001 Initial Stock Cost Upload | Spec to write | — | One-off admin task; OQ-FINV-1/2 open |
| F-017 Remove editMode / Admin CRUD | Spec to write | — | Claude writes; unblocked now that F-016 shipped |
| F-003b Price entry v2 | Spec to write | — | After F-017 |
| F-006b Dividends v2 | Spec to write | — | After F-017, parallel with F-003b — scope overlap with shipped F-010 to be reconciled when spec is written |
| F-TD-001 Test Checklist + Teardown | Spec ready — pending implementation | `.context/feature-specs/F-TD-001-test-checklist-teardown.md` | Teardown testbuild.zubbystudio.shop |
| F-019 Audit Log | Spec TBD | — | Receives events from F-016 |
| F-008 Dividends | **Superseded by F-010** | — | Original stub route `/dividends` left in place, hidden from nav |

### Phase 3C Sequencing (strict — standing rule)

```
HO-026 filed (hermes confirms HO-024 done — OUTSTANDING)
    ↓
AT-004 — 14/14 green (Codex runs — hard chokepoint)
    ↓
F-016 implementation (OQ-F016-1 and OQ-F016-2 must be answered first)
    ↓
F-INV-001 spec (Claude) → implementation (OQ-FINV-1/2 must be answered)
F-007 implementation (OQ-F007-3 must be answered)
    ↓
F-017 spec (Claude) → implementation
    ↓
F-003b + F-006b (parallel, each needs spec first)
    ↓
BUG-DASH-NOTIFY-001 (bell/useActionItems — deferred standalone)
```

**Actual execution to date (deviates from the above — documented exceptions, not a rule change):**

```
F-016 shipped out-of-sequence, out-of-process (DeepSeek Pro direct-to-build,
    no Zone 2 review, no AT-004 gate check confirmed)
F-010 Claims shipped out-of-sequence (pulled ahead via Lovable template port)
F-011 Claims Upload proposed — product-owner originated, spec written by
    hermes deepseek-flash (builder), architect-reviewed by DeepSeek Pro.
    Pending Claude Web governance review via HO-035.
    ↓
Remaining standing-sequence work still queued in original order:
    AT-004 confirmation → F-INV-001 → F-007 → F-017 → F-003b/F-006b
```

Both deviations are one-off exceptions per product-owner confirmation (2026-07-05). Neither authorizes future features to skip the gate; AT-004 must still be confirmed 14/14 green before further admin-route work proceeds, and F-017 must still precede F-003b/F-006b.

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

---

## Open Questions (Product Owner — Zubbyik must answer)

| ID | Question | Blocks |
|----|----------|--------|
| OQ-F007-3 | Non-trading days: store carry-forward NAV or skip entirely? | F-007 implementation |
| OQ-FINV-1 | Initial stock costs: CSV upload or manual form? | F-INV-001 spec |
| OQ-FINV-2 | All holdings need cost basis, or only specific portfolios? | F-INV-001 spec |

### Resolved Questions Log

| ID | Question | Answer | Resolved | Notes |
|----|----------|--------|----------|-------|
| OQ-F016-1 | Deactivated users' portfolios: hidden or read-only? | **Hidden** — visible only to SUPERADMIN | 2026-07-05 | Answered during out-of-process F-016 build; recorded here retroactively, not confirmed against a formal HO |
| OQ-F016-2 | Account creation: admin-only or email invitation flow? | **Admin-only** — admins create accounts directly, no email invite flow | 2026-07-05 | Same as above |

---

## Handover Chain — Current

| HO | Direction | Status | Contents |
|----|-----------|--------|----------|
| HO-024 | Claude → hermes nemotron | Complete | Admin restructure, editMode removal |
| HO-025 | Claude → Owl Alpha | Complete — executed by hermes nemotron | Test taxonomy migration |
| HO-026 | hermes → Claude | **OUTSTANDING** | Must confirm HO-024 done; include grep + pytest output |
| HO-027 | Claude → hermes nemotron | Sent | Spec delivery F-016, F-007, AT-004; next actions |
| HO-028 | Claude → Hermes governance | Sent | Answers to 3 OQs; Phase B sequencing; HO-029–033 pre-assigned |
| HO-029 | Hermes → Claude | Received | Phase A acceptance fixes; F-013 + F-TD-001 specs ready |
| HO-030 | DeepSeek Pro → Claude | **Retroactive — no prior Zone 2 review** | F-016 implementation complete, out-of-process. Urgency: security requirement, individual login credential provisioning. OQ-F016-1/2 answered as part of this build (see Resolved Questions Log). |
| HO-034a | Hermes → Claude | Complete | F-010 Claims dashboard (renumbered from a document originally issued as "HO-031" — see 2026-07-05 renumbering note below) |
| HO-035 | Hermes → Claude | Complete | F-011 Claims CSV Upload — spec, decisions, implementation plan, product owner decisions on 3-state lifecycle, fuzzy matching, registrar integration; ClaimRecord model change needed |
| HO-036 | Claude → Hermes | Complete — implementation finished, awaiting AT-004 | F-011 Governance Ruling — APPROVED WITH CONDITIONS (lifecycle_status column, preview response shape, thresholds, no Operator→Registrar fuzzy match, parallel track) |
| HO-035a | Hermes → log | Logged | Spec authorship exception logged — builder wrote F-011 spec with PO present + DeepSeek Pro concurrent review |

### Pre-assigned HO numbers

| HO | Purpose |
|----|---------|
| HO-030 | Hermes → Claude: F-016 implementation complete — **FULFILLED, retroactive, see Handover Chain above** |
| HO-031 | Hermes → Claude: F-017 implementation complete — **still open** (slot vacated after renumbering the Claims HO out of it) |
| HO-032 | Hermes → Claude: F-003b implementation complete |
| HO-033 | Hermes → Claude: F-006b implementation complete |
| HO-034a | Hermes → Claude: F-010 Claims dashboard complete — **FULFILLED** (renumbered from original errant "HO-031") |
| HO-034b | Hermes → Claude: Phase C deployment verification (renumbered from original "HO-034" to avoid collision with HO-034a) |
| HO-035 | Hermes → Claude: F-011 Claims CSV Upload — **COMPLETE** (Claude issued HO-036 governance ruling) |
| HO-036 | Claude → Hermes: F-011 Governance Ruling — **COMPLETE** |
| HO-037 | Hermes → Claude: AT-004 Execution Report — **COMPLETE** (Hermes deepseek-flash ran AT-004 against testdrive, 11/14 PASS, 3 pre-existing failures documented) |
| HO-038+ | Available — covers next feature |

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
  - Merge directly to main without review
  - Start implementation without a Claude-authored spec and acceptance criteria
  - Create or run code locally on Fedora during temporary offline period

ALWAYS:
  - Check existing services before adding new ones
  - Use openagile_network for inter-service communication
  - Follow Traefik label convention
  - Quote SSH heredocs: ssh user@host <<'EOF' ... EOF
  - Deploy via GitHub Actions (canonical path — even during VPS-direct exception)
  - Update MASTER_CONTEXT.md after every major infrastructure or architectural change
  - Increment version number on every update
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

## Historical Decision Log

### EPM v2

**2026-07-06: MASTER_CONTEXT.md v4.2 — v4.0/v4.1 reconciliation, legacy doc detached**
- Compared true `MASTER_CONTEXT_v4.0.md` (dated April 25, 2026 — "Master Prompt Framework" lineage: Obsidian vault sync, fast-path/full-path CI, Zero-Load Workflow) against v4.1 (EPM v2 / Phase 3C lineage). Checked each contradiction against actual VPS state rather than assuming either doc.
- **CI/CD pipeline**: Neither the fast-path/full-path split (v4.0) nor the branch-flow-with-approval-gate (v4.1) is actually running — confirmed no `.github/workflows/` in the repo. Both documents describe target design, not current reality. CI section above annotated accordingly; test isolation strategy (schema vs. separate database — the two docs disagreed) is undecided and will be chosen fresh when CI work resumes.
- **Staging URLs resolved**: `testdrive.epm.zubbystudio.shop` and `testbuild.zubbystudio.shop` both currently point to the same running container (a fork of the old `demo.estate` container, referred to as `_v3`). `testbuild` additionally fronts an nginx checklist page + API proxy forwarding to the same container. F-TD-001 teardown removes the testbuild nginx/proxy layer, not `_v3` itself. Documented in Active Services on VPS above.
- **Obsidian vault sync**: v4.0 documented a full vault-sync.yml architecture; confirmed no such workflow exists in the repo. Treated as a one-off historical seed (the original 85-company import), not an ongoing sync mechanism. Not carried forward into v4.2 as active infrastructure.
- **Agent roster, VPS-direct-execution exception, locked decisions (bcrypt pin, soft delete, monetary strings, cookie auth)**: v4.0 and v4.1 agree or v4.1 is confirmed current — no changes needed.
- **Legacy `MASTER_CONTEXT_v4_0.md` detached from project** per product-owner decision — retained only as historical reference outside the active project, not a governing document.

**2026-07-06: F-011 Governance Ruling received (HO-036) — implementation approved**
- Claude Web reviewed HO-035 and issued HO-036 with APPROVED WITH CONDITIONS ruling.
- Additive migration: `lifecycle_status` column (unresolved/unclaimed/claimed) coexists with existing `claim_status`.
- Operator CSV column is display-only — NOT fuzzy-matched against Registrar model. Registrar derived through company→registrar FK chain.
- Two-phase upload (preview/commit) confirmed matching cost_basis pattern. Preview response shape specified.
- Match thresholds: MATCH_THRESHOLD=90, AMBIGUOUS_THRESHOLD=70 — named constants.
- Spec authorship exception logged as HO-035a (builder wrote spec with PO present + DeepSeek Pro concurrent review).
- F-011 runs in PARALLEL with Phase 3C — does not block/blocked by AT-004 gate. Feature branch held pending AT-004 green before main merge.
- Implementation proceeding — next HO from hermes is HO-037 (implementation complete).
- **2026-07-06: F-011 implementation complete — awaiting AT-004 merge gate**
  - All 7 phases implemented by hermes deepseek-flash and deployed to testdrive.
  - Phase 1 (Backend): migration applied, fuzzy matcher with named constants, upload preview/commit/template endpoints, registrar_id filter.
  - Phase 2 (Frontend): claims upload tab in Data Upload, registrar unclaimed dividends widget.
  - **2026-07-06: AT-004 executed (HO-037) — 11/14 PASS, 3 pre-existing failures**
  - Hermes (deepseek-flash) designated as Codex fallback for manual acceptance testing per Zubbyik approval.
  - AT-004 failures (all pre-existing, not F-011-caused):
    1. A03/D02: SUPERADMIN role excluded from require_admin/isAdmin → 403
    2. B04: Residual isEditing in holdings.tsx (inline row editing variable)
  - Merge gate status: **BLOCKED** — AT-004 must pass 14/14 before F-011 merges to main.
  - HO-037 handover committed to docs/handovers/ for Claude Web visibility.
  - Container rebuilt (`--no-cache`) and restarted successfully. Template endpoint returns 401 (requires auth — correct).
  - Product-owner action: ready to upload SEC CSV at any time; F-011 is functional on testdrive.
  - Merge blocked on AT-004 14/14 green.
- Product owner originated this feature: SEC-scraped CSV of unclaimed dividends needs to populate the claims dashboard.
- Hermes (builder) wrote the spec — exceptions to the "Claude writes all specs" rule documented because the architect (DeepSeek Pro) was dispatched simultaneously to review and validated it; and because the CSV structure was confirmed by the product owner during the spec-writing session rather than deferred to a separate architect-led stakeholder interview. See HO-035 for full details.
- Spec at `.context/feature-specs/F-011-claims-upload.md` v1.1.
- CSV columns confirmed: `Account#`, `Shareholder`, `Company`, `Operator`.
- Three-state claim lifecycle defined by PO: unresolved / unclaimed / claimed.
- ClaimRecord model needs `claim_status` constraint updated to accept the three new values.
- Registrar widget requested: unclaimed dividends card on registrar detail page (markdown-file structure as read-only display).
- Pending Claude Web governance review before implementation begins.

**2026-07-06: F-010 Claims refactor — new claim_status values**
- HO-034a documented F-010 Claims dashboard as complete and deployed to testdrive.
- ClaimRecord model uses `pending/approved/rejected/partially_paid/paid/lapsed` claim_status with a CHECK constraint.
- F-011 introduces a parallel lifecycle: unresolved / unclaimed / claimed. These are not replacements — they are a different dimension: the estate's progress toward recovery, as opposed to the registrar's response status. Both status fields may coexist or one may subsume the other; HO-035 proposes a resolution.

**2026-07-05: MASTER_CONTEXT.md v4.1**
- F-016 (User Management) confirmed shipped, built out-of-process: DeepSeek Pro implemented directly with no Zone 2 (Claude Web) design review, justified by an urgent security requirement to provision an individual's own login credentials. Logged as a one-off exception, not a routing-rule change.
- OQ-F016-1 resolved: deactivated users' portfolios are hidden, visible only to SUPERADMIN.
- OQ-F016-2 resolved: account creation is admin-only; no email invitation flow.
- F-010 Claims (subsuming F-008 Dividends) confirmed shipped and deployed to testdrive, pulled ahead of the Phase 3C gate sequence as a one-off exception (cheap build via ported Lovable template). Standing gate order for F-INV-001 → F-007 → F-017 → F-003b/F-006b remains unchanged.
- Handover renumbering: a document originally issued as "HO-031" reporting F-010 Claims was renumbered to HO-034a (its content did not match the pre-assigned HO-031 slot, which is reserved for F-017 completion). The original "HO-034" (Phase C deployment verification) was renumbered to HO-034b to avoid collision.
- HO-030 recorded retroactively against the F-016 out-of-process build; no formal HO document exists for this build, only this after-the-fact log entry.
- Neither exception authorizes skipping Zone 2 consensus or the AT-004 gate for any future feature.

**2026-07-05: MASTER_CONTEXT.md v4.0**
- Rebuilt from v3.0 to reflect EPM v2 FastAPI/React architecture
- Added agent roster changes (nemotron → deepseek-flash primary, Kimi escalation)
- Added temporary workstation-offline exception
- Added Phase 3C feature sequence, locked decisions, role model, HO chain
- Added test taxonomy and active test status

**2026-07-03: Phase A acceptance testing (HO-029)**
- SPA routing fix: removed `app.mount("/", StaticFiles(...))` — catch-all `@app.get("/{full_path:path}")` serves index.html; `/assets/` on dedicated mount
- Price history default range: changed from 30 → 365 days (OKOMUOIL records Dec 2025)
- Companies page: scaffold stub confirmed — F-013 spec produced
- F-TD-001: Test checklist persistence + testbuild teardown spec produced
- Merged to main (commits a5cee42, c788b85)

**2026-06-30: Phase 3C specs (this session)**
- F-016 User Management spec produced (PRIMARY GATE)
- F-007 NAV History spec produced
- AT-004 Admin Restructure acceptance test produced (14 cases)
- BUG-TRIAGE-001 disposition: 2 closed, 1 deferred (BUG-DASH-NOTIFY-001), 1 superseded, 2 xfail
- F-INV-001 identified as required one-off spec

**2026-06-25: Test taxonomy migration (HO-025)**
- EPM_TEST_TAXONOMY.md adopted: DOMAIN-WORKFLOW-LAYER-TYPE-NNN
- New folder structure created under tests/
- Existing tests migrated from backend/tests/
- New security + smoke tests added

**2023-06-XX: HO-023 — editMode removal (locked)**
- All inline editing removed system-wide
- All CRUD operations moved to Admin section
- No editMode toggle anywhere in codebase

### Legacy (from v3.0 — preserved for reference)

**2026-03-28: Migrated Nginx → Traefik**
- Automatic SSL, better Docker integration
- All services now use Traefik labels

**2026-03-15: Shared PostgreSQL Strategy**
- Resource efficiency (<4GB RAM available per service at the time)
- New services MUST check if Postgres exists before creating

**2025-12: Estate Portfolio Streamlit Integration (superseded by EPM v2)**
- Original Streamlit app at estate.zubbystudio.shop
- Replaced by EPM v2 FastAPI + React rebuild

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
```

### Workstation Restored

```
1. Remove temporary VPS-direct execution permission from this file
2. Confirm all changes made during offline period are committed to GitHub
3. Increment MASTER_CONTEXT.md version
4. Resume normal GitHub Actions deployment flow
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
- Netcup VPS: updated in-situ by Hermes agents
- Claude Web project: manually copied by Zubbyik after each update
- Gitea: committed to repo as `.context/MASTER_CONTEXT.md`

---

**END OF MASTER_CONTEXT.md v4.2**
**File Maintainer**: Claude Web (Architect) — update after every major change
**Version Control**: `MASTER_CONTEXT: v4.2 — v4.0/v4.1 reconciliation + F-011 (implemented, awaiting AT-004 merge)`
