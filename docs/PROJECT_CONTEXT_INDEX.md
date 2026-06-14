---
type: INDEX
id: OPENAGILE-PROJECT-CONTEXT-INDEX
title: OpenAgile Project Context Index
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# OpenAgile Project Context Index

Use this file when an agent lands in the OpenAgile monorepo and needs to find
the relevant workflow, context engine, handovers, and project-local rules.

## First-Contact Protocol

1. Read root `AGENTS.md`.
2. Resolve the target subproject using the trigger rules below.
3. Read that subproject's local `docs/context/MASTER_CONTEXT.md`, if present.
4. Read local `WORKFLOW.md`, `DELEGATION_REGISTRY.md`, and `AGENT_STATE.yaml`.
5. Read the latest relevant handover or acceptance test.
6. Lock edits to that target project unless the user explicitly expands scope.
7. Only then edit files.

## Target Resolution Triggers

Use these triggers in order:

| Priority | Trigger | Example | Result |
|---|---|---|---|
| 1 | Explicit project name | "work on Estate Portfolio" | Use that project's path. |
| 2 | File path in prompt | `egbuna_estate_account_streamlight/estate-portfolio/backend/app/models.py` | Use the owning project root. |
| 3 | Active/open IDE file | Active file under `estate-portfolio/docs/context/` | Use Estate Portfolio Manager. |
| 4 | Handover or AT id | `HO-018-1`, `AT-003-2` | Read the matching docs and infer project. |
| 5 | Service/domain name | `demo.estate.zubbystudio.shop` | Map via project table below. |

If two projects match, stop and ask for clarification.

If no project matches, stop and ask: "Which OpenAgile subproject should I work
on?"

## Project Write Locks

After resolving the target project:

- Edit only inside that project's root path.
- Root coordination docs may be edited only when the user asks for cross-project
  workflow, context, or documentation routing changes.
- Do not edit sibling subprojects opportunistically.
- If a fix truly requires another subproject, pause and ask for scope expansion.

## Project Context Engines

| Project | Trigger names | Path | Context Engine | Notes |
|---|---|---|---|---|
| Estate Portfolio Manager | estate, EPM, demo.estate, portfolio | `egbuna_estate_account_streamlight/estate-portfolio/` | `egbuna_estate_account_streamlight/estate-portfolio/docs/context/` | Active EPM v2 context engine. |
| Thrive Tech Hub | thrive, tech hub | `thrive-tech-hub/` | Pending | Has local `AGENTS.md`; context engine not normalized here yet. |
| Frappe Docker | frappe, erpnext, edu_theme | `frappe_docker/` | Pending | Follow root AGENTS Frappe-specific rules. |
| YouTube Shorts | youtube, shorts | `you-tube-shorts/` | Pending | Has project artifacts; context engine not normalized here yet. |
| WireGuard | wireguard, vpn | `wireguard/` | Pending | Has local `AGENTS.md`; infrastructure-sensitive. |

## Estate Portfolio Manager Quick Links

- Context: `egbuna_estate_account_streamlight/estate-portfolio/docs/context/MASTER_CONTEXT.md`
- Workflow: `egbuna_estate_account_streamlight/estate-portfolio/docs/context/WORKFLOW.md`
- Delegation: `egbuna_estate_account_streamlight/estate-portfolio/docs/context/DELEGATION_REGISTRY.md`
- State: `egbuna_estate_account_streamlight/estate-portfolio/docs/context/AGENT_STATE.yaml`
- Docs index: `egbuna_estate_account_streamlight/estate-portfolio/docs/README.md`
- Current handover: `egbuna_estate_account_streamlight/estate-portfolio/docs/handover/HO-018-1-claude-to-deepseek-antigravity-grok.md`
- Migration proposal: `egbuna_estate_account_streamlight/estate-portfolio/docs/context/DOCUMENT_MIGRATION_MAP.md`

## Rule Of Thumb

Root documents answer: "What is true for all OpenAgile projects?"

Project context engines answer: "What is true for this subproject right now?"

Documentation shape is defined in `docs/DOCUMENTATION_STRUCTURE.md` and should
be mirrored by each child project that has a `docs/` directory.

