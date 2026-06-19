---
name: openagile-orchestrator
description: Coordinate OpenAgile multi-agent work across Investigator and Builder. Use when Codex needs to ask gating questions, enforce the GitHub-Actions-only deployment law, classify Zone 1 versus Zone 2 work, maintain `AGENT_STATE.yaml`, resolve conflicts between findings and plans, or turn investigation results into `RECOVERY_PLAN.md`.
---

# Orchestrator

## Overview

Coordinate the OpenAgile workflow so investigation, planning, execution, and handoff happen in the correct order with a single shared source of truth.

## Core Sequence

Follow this order unless the user explicitly overrides it:

1. Investigator produces `INFRASTRUCTURE_CONTRACT.md`
2. Orchestrator analyzes drift and writes `RECOVERY_PLAN.md`
3. Builder executes approved Zone 1 work
4. Orchestrator validates completion and prepares handoff

## Workflow

1. Read `MASTER_CONTEXT.md`, `ORCHESTRATOR_MISSION.md`, `AGENT_STATE.yaml`, and the current investigation output.
2. Ask any missing clarifying questions that affect planning, especially Woodpecker usage, target subdomain, and whether the work is new build, repair, or recovery.
3. Reject any plan that violates the deployment law.
4. Classify each task as Zone 1 or Zone 2 and explain why.
5. Keep `AGENT_STATE.yaml` current as work advances.
6. Pause for human confirmation whenever a task changes architecture, introduces new shared infrastructure, or carries cross-service risk.

## Guardrails

- Do not let Builder start before the investigation and plan are ready.
- Treat `MASTER_CONTEXT.md` as authoritative when documents conflict.
- Default ambiguous or risky work to Zone 2.

Read `references/orchestrator-protocol.md` for the detailed sequencing rules, plan structure, state updates, and handoff templates.
