---
type: STANDARD
id: OPENAGILE-DOCUMENTATION-STRUCTURE
title: OpenAgile Documentation Structure Standard
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# OpenAgile Documentation Structure Standard

This standard applies to root `docs/` and every subproject `docs/` directory.

## Required Directory Shape

```text
docs/
├── README.md
├── context/
│   ├── MASTER_CONTEXT.md
│   ├── AGENT_STATE.yaml
│   ├── DELEGATION_REGISTRY.md
│   └── WORKFLOW.md
├── architecture/
├── requirements/
├── testing/
│   └── acceptance-tests/
├── onboarding/
├── handover/
└── archive/
```

Projects may add extra directories, but should not invent alternate homes for
the document types above.

## Required Front Matter

Markdown docs should start with YAML front matter:

```yaml
---
type: CONTEXT
id: UNIQUE-ID
title: Human Readable Title
status: ACTIVE
version: 1.0
updated: YYYY-MM-DD
---
```

Use these `type` values consistently:

| Type | Directory |
|---|---|
| `CONTEXT` | `docs/context/` |
| `HO` | `docs/handover/` |
| `AT` | `docs/testing/acceptance-tests/` |
| `BR` | `docs/requirements/` |
| `ADR` | `docs/architecture/` |
| `OB` | `docs/onboarding/` |
| `ARCHIVE` | `docs/archive/` |
| `INDEX` or `STANDARD` | Root or project `docs/` |

## First-Contact Rule

Every project with a `docs/` directory should expose the same first-contact
path:

```text
docs/README.md
docs/context/MASTER_CONTEXT.md
docs/context/WORKFLOW.md
docs/context/DELEGATION_REGISTRY.md
docs/context/AGENT_STATE.yaml
```

Root-level agents should use `docs/PROJECT_CONTEXT_INDEX.md` to find the target
project context engine.

## Scope Lock Rule

Project docs must state their project root and write boundary. Agents must not
edit outside that boundary unless the user explicitly expands the task scope.

