---
type: CONTEXT
id: OPENAGILE-ROOT-WORKFLOW
title: OpenAgile Root Workflow
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# OpenAgile Root Workflow

## First-Contact Workflow

1. Read root `AGENTS.md`.
2. Read `docs/PROJECT_CONTEXT_INDEX.md`.
3. Resolve target project from prompt, file path, active IDE file, handover, or
   acceptance test.
4. Read the target project context engine.
5. Lock writes to the target project path.
6. Ask for clarification if the target is ambiguous.

## Cross-Project Work

Do not edit more than one subproject unless the user explicitly requests
cross-project work. Root coordination docs may be edited only for workflow,
context, infrastructure, or documentation-routing tasks.

## Deployment Rule

All deployment remains GitHub Actions only. Do not run Docker locally.

