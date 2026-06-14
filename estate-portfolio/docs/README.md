# Estate Portfolio Manager — Project Documentation

> Personal NGX portfolio tracker · FastAPI + React · Self-hosted on Netcup VPS

This directory serves as the single source of truth for the project's documentation, structured according to our STLC/SDLC Governance.

## First Contact For Agents

If you are Claude, Codex, Deepseek, Antigravity, Grok, or any future agent
entering this project cold, read these before editing:

1. Root `AGENTS.md`
2. `docs/context/MASTER_CONTEXT.md`
3. `docs/context/WORKFLOW.md`
4. `docs/context/DELEGATION_REGISTRY.md`
5. `docs/context/AGENT_STATE.yaml`
6. Latest relevant handover in `docs/handover/`

## Quick Links
| I want to... | Go to |
|-------------|-------|
| Understand what the system does | [Requirements](requirements/) |
| See why a technical decision was made | [Architecture Decision Records](architecture/) |
| Find test cases for a feature | [Testing](testing/) |
| Onboard as a new agent/developer | [Onboarding](onboarding/) |
| See latest handover briefs | [Handover](handover/) |
| Continue agentic work with current context | [Context Engine](context/) |

## Document Index

### 📋 REQUIREMENTS (`docs/requirements/`)
* [BR-001 Portfolio Tracking](requirements/BR-001-portfolio-tracking.md)
* [BR-002 Price Entry](requirements/BR-002-price-entry.md)
* [BR-003 Obsidian Migration](requirements/BR-003-obsidian-migration.md)
* [BR-004 Claims Tracking](requirements/BR-004-claims-tracking.md)
* [BR-005 Registrar Documents](requirements/BR-005-registrar-documents.md)

### 🏗 ARCHITECTURE (`docs/architecture/`)
* [ADR-001 Single Container](architecture/ADR-001-single-container.md)
* [ADR-002 Shared Postgres](architecture/ADR-002-shared-postgres.md)
* [ADR-003 JWT Cookie Auth](architecture/ADR-003-jwt-httponly-cookie.md)
* [ADR-004 NGX PDF Parser](architecture/ADR-004-ngx-pdf-parser.md)
* [ADR-005 Local Volume Storage](architecture/ADR-005-local-volume-storage.md)

### 🧪 TESTING (`docs/testing/`)
* [STLC Overview](testing/STLC-v1.0.md)
* [AT-001 Price Entry (2026-05-05)](testing/acceptance-tests/AT-001-price-entry-2026-05-05.md)
* [AT-002 Registrars (2026-05-05)](testing/acceptance-tests/AT-002-registrars-2026-05-05.md)
* [Legacy Acceptance Test](testing/acceptance-tests/legacy-acceptance-test.md)
* Gherkin feature specs live in [`testing/features/`](testing/features/)
* [BR-001 Gherkin Spec](testing/features/BR001_GHERKIN_SPEC.md)

### 🚀 ONBOARDING (`docs/onboarding/`)
* [OB-001 Getting Started](onboarding/OB-001-onboarding.md)
* [OB-002 Agent Delegation](onboarding/OB-002-agent-delegation.md)

### 🧠 CONTEXT ENGINE (`docs/context/`)
* [EPM Master Context](context/MASTER_CONTEXT.md)
* [Agent State](context/AGENT_STATE.yaml)
* [Delegation Registry](context/DELEGATION_REGISTRY.md)
* [Workflow](context/WORKFLOW.md)
* [Document Migration Map](context/DOCUMENT_MIGRATION_MAP.md)

### 🤝 HANDOVER (`docs/handover/`)
* [HO-009 Dashboard, Holdings, Registrars, Price History](handover/HO-009-dashboard-holdings-registrars-pricelist.md)
* [HO-011 Add Holding Redesign and Fixes](handover/HO-011-claude-to-antigravity.md)
* [HO-013 AT-003 Fix Plan](handover/HO-013-claude-to-antigravity.md)
* [HO-014 Group A Diagnosis and Fixes](handover/HO-014-antigravity-to-claude.md)
* [HO-015 Group E Fix Spec](handover/HO-015-claude-to-antigravity.md)
* [HO-016 Group E Implementation](handover/HO-016-antigravity-to-claude.md)
* [HO-017 AT-003-1 Results](handover/HO-017-antigravity-to-claude.md)
* [HO-018 Original Dual-Agent Handover](handover/HO-018-claude-to-both-agents.md)
* [HO-018-1 Corrected AT-003-2 Recovery Handover](handover/HO-018-1-claude-to-deepseek-antigravity-grok.md)

### 🗄 ARCHIVE (`docs/archive/`)
* [2026-05-23 Root Cleanup](archive/2026-05-23-root-cleanup/INDEX.md)

## Current Status
| Area | Status |
|------|--------|
| Authentication | ✅ Complete |
| Price Entry + NGX PDF | ✅ Complete |
| Registrars + Documents | ⚠️ Bugs being fixed |
| Holdings (dual table) | 🔄 In progress |
| Claims tracking | 📋 Planned |
| Obsidian import | 📋 Planned |
