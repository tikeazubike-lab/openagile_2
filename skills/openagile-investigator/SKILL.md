---
name: openagile-investigator
description: Perform read-only forensic analysis of OpenAgile infrastructure and target projects. Use when Codex needs to inspect working patterns, reconstruct deployment, Traefik, network, database, Frappe, and CI/CD rules, produce `INFRASTRUCTURE_CONTRACT.md`, or separate confirmed facts from inferred constraints before planning changes.
---

# Investigator

## Overview

Inspect the current workspace and a target project to extract the operating contract that downstream planning and implementation should follow.

## Operating Mode

Stay read-only. Do not modify files or run state-changing commands while using this skill.

## Workflow

1. Read `MASTER_CONTEXT.md` first, then inspect the root `docker-compose.yml`, the target project, and relevant GitHub Actions workflows.
2. Collect direct evidence for networks, Traefik labels, shared services, volume patterns, secrets usage, and deployment flow.
3. Mark every uncertain statement as `[INFERRED]` or `[UNKNOWN]`.
4. Produce `INFRASTRUCTURE_CONTRACT.md` with confirmed patterns, deviations, implicit rules, and a handoff summary for the Orchestrator.

## Investigation Focus

- network names and `external: true` declarations
- Traefik routing labels, entrypoints, TLS, and certresolver
- shared PostgreSQL and Redis reuse
- GitHub Actions deployment flow and deployment-law violations
- Frappe-specific bench, apps, assets, and build requirements
- target-project-specific risks or drift

## Reporting Rules

- Base conclusions on evidence, not assumptions.
- Flag violations of the GitHub-Actions-only deployment law explicitly.
- Distinguish current facts from recommended follow-up work.

Read `references/investigator-protocol.md` for the detailed checklist, output structure, and target-specific investigation guidance.
