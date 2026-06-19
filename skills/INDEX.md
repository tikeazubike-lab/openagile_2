# OpenAgile Skills Index

This repository currently defines and installs these Codex skills:

## `openagile-builder`

Purpose:
Implement approved OpenAgile changes inside a target project while following the deployment law and project guardrails.

Use it when:

- you already have a plan and need implementation
- the task belongs in a target project rather than root-level architecture
- the work must follow OpenAgile Frappe, Traefik, network, and verification rules

Example prompt:

```text
Use $openagile-builder to implement the approved recovery plan for frappe_docker_edu.
```

Local source:

- `skills/openagile-builder/`

## `openagile-investigator`

Purpose:
Inspect the workspace and derive the infrastructure contract for a target project using read-only analysis.

Use it when:

- you need to reconstruct working infrastructure patterns
- you want `INFRASTRUCTURE_CONTRACT.md`
- you need confirmed facts separated from inferred constraints before planning changes

Example prompt:

```text
Use $openagile-investigator to analyze estate-portfolio and produce the infrastructure contract.
```

Local source:

- `skills/openagile-investigator/`

## `openagile-orchestrator`

Purpose:
Coordinate the OpenAgile workflow across investigation, planning, execution, and handoff.

Use it when:

- you need zone classification
- you need `RECOVERY_PLAN.md`
- you need to enforce the GitHub-Actions-only deployment law and sequence work correctly

Example prompt:

```text
Use $openagile-orchestrator to create a recovery plan for wireguard after the investigation is complete.
```

Local source:

- `skills/openagile-orchestrator/`

## Notes

- Installed global copies live in `~/.codex/skills/`.
- Repo-local source-of-truth copies live under `skills/`.
- If you update a repo-local skill, copy it back into `~/.codex/skills/` to refresh the installed version.
