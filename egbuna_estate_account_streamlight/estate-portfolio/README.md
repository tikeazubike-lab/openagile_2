# Estate Portfolio Manager (EPM)

A self-hosted Nigerian stock portfolio tracker for managing NGX equities, claims
(delisted/defunct stocks), dividend tracking, registrar relationships, and
administrative documents. All data stays on a self-hosted Netcup VPS.

**Environment**: `testdrive.epm.zubbystudio.shop` (Phase 3 staging)

---

## Three North Star Goals

Every feature serves one of these:

1. **NET WORTH** — "What do I own and what is it worth today?"
2. **ADMINISTRATION** — "What paperwork is outstanding? What dividends uncollected?"
3. **PERFORMANCE** — "Is my portfolio growing over time?"

---

## Asset Scope

| Current (Phase 2-3) | Future (Phase 4) |
|---|---|
| NGX listed equities | Nigerian Eurobonds |
| NGX delisted/defunct (claims) | Real estate / property |
| NGX merged equities | Treasury bills, fixed deposits, mutual funds |

---

## Document Type Codes — Where to Find Them

The naming convention is governed by `Epm_governance_sdlc_stlc·md`
(project root of `openagile_2`).

| Code | Meaning | Location |
|------|---------|----------|
| **BR-NNN** | Business Requirement — what the system must do | `docs/requirements/BR-001-*.md` |
| **FR-NNN** | Functional Requirement — how the system does it | `docs/requirements/` (often inlined into BR specs) |
| **ADR-NNN** | Architecture Decision Record — why a technical choice was made | `docs/architecture/ADR-001-*.md` |
| **TC-NNN** | Test Case / Test Plan — how a feature is verified | `docs/testing/test-plans/TC-001-*.md` |
| **AT-NNN** | Acceptance Test — UAT pass/fail results | `docs/testing/acceptance-tests/AT-001-*.md` |
| **HO-NNN** | Handover Brief — agent-to-agent context transfer | `docs/handovers/HO-*.md` |
| **OB-NNN** | Onboarding — getting started guides | `docs/onboarding/OB-001-*.md` |
| **F-NNN** | Feature Spec — implementation specification | `.context/feature-specs/F-001-*.md` |
| **SC-NNN** | Gherkin Scenario — numbered acceptance scenario | `docs/testing/features/BR001_GHERKIN_SPEC.md` (SC-001 to SC-046) |
| **BUG-NNN** | Bug Tracker Entry | `.context/progress-tracker.md` (Open Bugs table) |
| **OQ-FXXX-N** | Open Question — blocking question for product owner | `.context/MASTER_CONTEXT.md` (Open Questions table) |
| **REQ-XXX-NNN** | Requirement ID — traceability from feature to test | `AGENTS_PROMPTS_AND_INSTRUCTIONS/docs/testing/taxonomy/EPM_TEST_TAXONOMY.md` |
| **DOMAIN-WF-LAYER-TYPE-NNN** | Test ID — e.g. `AUTH-LOGIN-BE-INT-001` | Same taxonomy doc above |

---

## Documentation Map

### Context & Governance (agent-facing, source of truth)

| File | Purpose |
|------|---------|
| `.context/MASTER_CONTEXT.md` | Operating contract: feature specs table, handover chain, open questions, architecture decisions, phase sequencing |
| `.context/progress-tracker.md` | Feature status by phase, open bugs, priority order, missing dependencies |
| `.context/project-overview.md` | High-level scope, north star goals, success criteria, out-of-scope items |
| `.context/AGENT_LOG.md` | Chronological agent activity log |
| `.context/feature-specs/` | Feature specs (F-001-authentication.md, F-010-claims.md, etc.) |

### Requirements & Architecture

| Path | Contents |
|------|----------|
| `docs/requirements/` | Business requirements (BR-001-portfolio-tracking.md, BR-002-price-entry.md, etc.) |
| `docs/architecture/` | Architecture decision records (ADR-001-single-container.md, etc.) |

### Testing

| Path | Contents |
|------|----------|
| `docs/testing/features/BR001_GHERKIN_SPEC.md` | Gherkin spec — all SC-001 through SC-046 scenarios |
| `docs/testing/acceptance-tests/` | AT-001, AT-002, AT-003, AT-004 acceptance test results |
| `docs/testing/test-plans/` | TC-001 through TC-004 test plans |
| `AGENTS_PROMPTS_AND_INSTRUCTIONS/docs/testing/taxonomy/EPM_TEST_TAXONOMY.md` | Full test naming convention, folder structure, migration map, traceability matrix |

### Handovers

| Path | Contents |
|------|----------|
| `docs/handovers/` | HO-* agent handover briefs (chronological) |
| `.context/MASTER_CONTEXT.md` (Handover Chain table) | Current handover status and pre-assigned HO numbers |

### Agent Instructions & Process

| Path | Contents |
|------|----------|
| `AGENTS_PROMPTS_AND_INSTRUCTIONS/` | Agent role definitions, process docs, workflow design, fresh-session master prompt |
| `AGENTS.md` | Repository guidelines (in repo root) |

### Onboarding

| Path | Contents |
|------|----------|
| `docs/onboarding/` | OB-001-onboarding.md, OB-002-agent-delegation.md |

---

## Technology Stack

**Backend**: FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL
**Frontend**: React 18 + TanStack Router + TanStack Query + Zustand + Recharts
**Auth**: 30-day httpOnly cookie (`epm_token`), bcrypt-hashed passwords
**Deployment**: Docker Compose on single Netcup VPS
**Agents**: Hermes (governance), OpenCode/DeepSeek (implementation)

---

## Feature Status Summary

| Phase | Features |
|-------|----------|
| Phase 2-3A (Foundation) | F-001 Auth ✅, F-002 Dashboard ⚠️, F-003 Holdings ⚠️, F-004 Price Entry ✅, F-005 Price History ✅, F-006 Registrars ✅ |
| Phase 3B (Admin Restructure) | F-NGX-COMPANIES ✅, F-COST-BASIS ✅, F-003b PLANNED, F-006b PLANNED, F-017 PLANNED |
| Phase 3C (New Core) | F-016 User Mgmt ✅, F-010 Claims ✅, F-011 CSV Upload ✅, F-007 PLANNED, F-009 PLANNED, F-012 PLANNED |
| Phase 3D (Companies) | F-013 PLANNED, F-018 PLANNED, F-019 PLANNED |
| Phase 3E (Settings) | F-014 PLANNED, F-015 PLANNED, F-020 PLANNED, F-021 PLANNED |

See `.context/progress-tracker.md` and `.context/MASTER_CONTEXT.md` for full status details and sequencing.

---

## Architecture Notes

- **Monetary values**: Always strings in API responses (e.g. `"₦1,234.56"`) — never floats
- **Soft delete**: `deleted_at` timestamp, never hard delete
- **Draft/Live**: `status: 'draft' | 'live'` on holdings/transactions; read-only role filters to `live` only
- **Cookie auth**: 30-day httpOnly cookie, never localStorage
- **Price audit**: `PriceAudit` row written before every `Company.current_price` update (single transaction)
- **Claim holdings**: Use `cost_basis_override` for cost basis calculation instead of `total_cost`
- **lifecycle_status**: Canonical values are `pending/unresolved`, `approved/unclaimed`, `paid/claimed`
