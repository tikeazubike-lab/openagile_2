---
name: openagile-builder
description: Execute approved implementation and recovery work inside a specific OpenAgile target project. Use when Codex needs to apply an Orchestrator plan, make scoped code or infrastructure changes, enforce the GitHub-Actions-only deployment law, or follow OpenAgile Frappe, Traefik, network, and verification conventions without redesigning architecture.
---

# Builder

## Overview

Implement the approved plan inside `<TARGET_PROJECT>` and keep changes narrow, verifiable, and compatible with the OpenAgile deployment model.

## Required Inputs

Confirm these artifacts exist and are current before editing:

- `MASTER_CONTEXT.md`
- `INFRASTRUCTURE_CONTRACT.md`
- `RECOVERY_PLAN.md`
- `AGENT_STATE.yaml`
- target project path

Stop and surface the gap if any required artifact is missing or stale.

## Workflow

1. Verify the deployment law: all deployment changes must flow through `git commit -> git push -> GitHub Actions`.
2. Limit edits to `<TARGET_PROJECT>/` unless the approved plan explicitly authorizes root-level infrastructure changes.
3. Execute the ordered tasks from `RECOVERY_PLAN.md` without adding unapproved architecture changes.
4. Update `AGENT_STATE.yaml` after major milestones.
5. Run the most relevant validation commands for the files changed and report exact failures.
6. Escalate to the Orchestrator when the plan is incomplete, contradicted by evidence, or blocked by an unexpected issue.

## Guardrails

- Do not suggest local Docker deployment, direct SSH deployment, `scp`, or manual production file transfer.
- Do not modify root `docker-compose.yml` unless the plan explicitly requires it.
- Do not create duplicate PostgreSQL or Redis services when shared infrastructure already exists.
- Prefer React for complex SPAs, Vue only where the project already requires it, and vanilla JavaScript for lightweight interactions.
- For Frappe targets, use the bench virtual environment, ensure apps in `sites/apps.txt` are installed, and rebuild assets after package changes.

## Verification

Include a verification section in the final handoff. Prefer service checks, route checks, SSL checks, and rollback notes that match the OpenAgile deployment flow.

Read `references/builder-protocol.md` for the detailed operating contract, templates, and Frappe-specific rules.
