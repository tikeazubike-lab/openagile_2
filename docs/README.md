---
type: INDEX
id: OPENAGILE-DOCS-README
title: OpenAgile Root Documentation
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# OpenAgile Root Documentation

This directory is the parent documentation hub for the OpenAgile monorepo.

## First Contact For Agents

Agents launched from the OpenAgile root should read:

1. Root `AGENTS.md`
2. `docs/PROJECT_CONTEXT_INDEX.md`
3. Target subproject `docs/context/MASTER_CONTEXT.md`
4. Target subproject `docs/context/WORKFLOW.md`
5. Target subproject `docs/context/DELEGATION_REGISTRY.md`
6. Target subproject `docs/context/AGENT_STATE.yaml`

If the target subproject is unclear, ask before editing.

## Root Documentation Structure

- `context/` — root context pointers and workflow.
- `architecture/` — OpenAgile-wide architecture notes.
- `requirements/` — OpenAgile-wide requirements and specs.
- `testing/` — OpenAgile-wide testing standards.
- `onboarding/` — OpenAgile-wide onboarding, including
  [OpenAgile Setup Guide](onboarding/OPENAGILE_SETUP_GUIDE.md).
- `handover/` — OpenAgile-wide handovers.
- `archive/` — superseded root docs.
- `PROJECT_CONTEXT_INDEX.md` — project routing table.
- `DOCUMENTATION_STRUCTURE.md` — documentation structure standard.

Subprojects should mirror this same shape inside their own `docs/` directory.
