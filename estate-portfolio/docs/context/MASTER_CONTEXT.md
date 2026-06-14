---
type: CONTEXT
id: EPM-MASTER-CONTEXT
title: Estate Portfolio Manager Context Engine
status: ACTIVE
version: 1.0
updated: 2026-05-23
scope: egbuna_estate_account_streamlight/estate-portfolio
---

# Estate Portfolio Manager Context Engine

This directory is the project-local context engine for Estate Portfolio Manager
EPM v2. It complements, but does not replace, the workspace-level
`/MASTER_CONTEXT.md` and root `AGENTS.md`.

## Authority Order

When documents conflict, use this order:

1. Workspace `AGENTS.md` and `/MASTER_CONTEXT.md` for OpenAgile-wide rules.
2. `/docs/PROJECT_CONTEXT_INDEX.md` for first-contact project discovery.
3. This file for EPM-local rules and current project direction.
4. `docs/context/WORKFLOW.md` for agent sequencing.
5. `docs/context/DELEGATION_REGISTRY.md` for current agent ownership.
6. Latest handover in `docs/handover/`.
7. Requirements, ADRs, onboarding, and acceptance tests.

## First-Contact Sequence

Any agent entering EPM cold should read, in order:

1. Root `AGENTS.md`
2. Root `docs/PROJECT_CONTEXT_INDEX.md`
3. This file
4. `docs/context/WORKFLOW.md`
5. `docs/context/DELEGATION_REGISTRY.md`
6. `docs/context/AGENT_STATE.yaml`
7. Latest relevant handover or acceptance test

## EPM Target Triggers

An agent launched from the OpenAgile root should select this EPM project when
the prompt, active file, handover, or acceptance test mentions any of:

- `egbuna_estate_account_streamlight/estate-portfolio/`
- `Estate Portfolio Manager`
- `EPM`
- `demo.estate.zubbystudio.shop`
- `estate-portfolio-manager`
- `backend/app/routers/holdings.py`
- `AT-003`, `AT-003-1`, `AT-003-2`
- `HO-018`, `HO-018-1`

If another project is also mentioned, pause and ask for the intended target.

## Project Boundary

Project root:

```text
egbuna_estate_account_streamlight/estate-portfolio/
```

Primary EPM v2 code:

```text
backend/                         FastAPI, SQLAlchemy, Alembic, tests
estate-portfolio-manager/src/    React, Vite, TanStack, UI state
docker-compose.v2.yml            EPM v2 deployment composition
Dockerfile.v2                    EPM v2 single-container build
docs/                            EPM documentation and context engine
```

Legacy Streamlit code remains in the project and must not be removed unless an
approved migration says it is obsolete.

## Write Boundary

Default write scope for EPM work:

```text
egbuna_estate_account_streamlight/estate-portfolio/
```

Do not edit sibling projects from an EPM task. Root coordination docs may be
edited only when the user explicitly asks for cross-project routing,
documentation structure, or OpenAgile-wide context changes.

## Documentation Structure

EPM follows the root documentation standard:

```text
docs/DOCUMENTATION_STRUCTURE.md
```

EPM-local docs should keep this structure:

```text
docs/
├── README.md
├── context/
├── architecture/
├── requirements/
├── testing/acceptance-tests/
├── onboarding/
├── handover/
└── archive/
```

## Non-Negotiable Rules

- Work on the `test` branch.
- Do not run Docker locally on the Fedora workstation.
- Deploy only by git push to GitHub Actions.
- Reuse shared PostgreSQL; do not add a Postgres container.
- Keep HTTP/HTTPS behind Traefik.
- Keep monetary API response values as JSON strings.
- Preserve original handovers; write amendments such as `HO-018-1` instead of
  mutating prior handovers, prior to working on the next phase of the project.
- Archive questionable docs under `docs/archive/`; do not delete project memory
  without explicit human approval.

## Current Sprint Direction

The active correction is documented in:

- `docs/handover/HO-018-1-claude-to-deepseek-antigravity-grok.md`

Current ownership:

- Deepseek v4 owns backend fixes and final integration push.
- Antigravity using Gemini owns React frontend fixes.
- Grok acts as read-only spotter.
- Codex acts as context/orchestration reviewer unless explicitly assigned build
  work.

## External Root References

These files previously lived at the OpenAgile root and have been consolidated
into EPM docs:

- `docs/handover/HO-018-claude-to-both-agents.md`
- `docs/testing/acceptance-tests/AT-003-1-followup-test.md`
- `docs/archive/2026-05-23-root-cleanup/root-context/DEEPSEEK_CONTEXT.md`
- `docs/handover/HO-016-antigravity-to-claude.md`
- `docs/testing/acceptance-tests/AT-003-dashboard-holdings-registrars-pricehist-root-copy.md`
