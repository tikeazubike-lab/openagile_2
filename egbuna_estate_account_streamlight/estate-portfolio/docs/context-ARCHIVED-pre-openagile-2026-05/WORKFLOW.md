---
type: CONTEXT
id: EPM-WORKFLOW
title: EPM Agentic Workflow
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# EPM Agentic Workflow

## Standard Flow

1. Resolve EPM as the target project from root `docs/PROJECT_CONTEXT_INDEX.md`.
2. Read `docs/context/MASTER_CONTEXT.md`.
3. Read `docs/context/AGENT_STATE.yaml`.
4. Read `docs/context/DELEGATION_REGISTRY.md`.
5. Read the latest relevant handover in `docs/handover/`.
6. Confirm file ownership before editing.
7. Implement only within assigned EPM scope.
8. Validate with non-Docker local checks or GitHub Actions, depending on task.
9. Report verification using the required OpenAgile format.

## Scope Lock

For EPM tasks, write only under:

```text
egbuna_estate_account_streamlight/estate-portfolio/
```

Exceptions require explicit user approval:

- root `AGENTS.md`
- root `docs/PROJECT_CONTEXT_INDEX.md`
- root documentation standards
- GitHub Actions or root infrastructure files
- sibling project files

## Documentation Flow

- New handovers go in `docs/handover/`.
- Acceptance tests go in `docs/testing/acceptance-tests/`.
- Architecture decisions go in `docs/architecture/`.
- Business requirements go in `docs/requirements/`.
- Agent onboarding goes in `docs/onboarding/`.
- Context engine files go in `docs/context/`.
- Redundant or superseded project docs move to `docs/archive/` only after the
  migration map is approved.

## Archive Rule

Archive, do not delete, unless the user explicitly approves deletion. Archived
documents should keep enough path context in their filename or archive index for
future recovery.

## Verification Template

Every implementation handover must include:

```markdown
## Verification Steps

1. **Test Command**: [exact command to test]
2. **Expected Output**: [what success looks like]
3. **If It Fails**: [diagnostic steps]
4. **Rollback**: [how to undo if broken]
```
