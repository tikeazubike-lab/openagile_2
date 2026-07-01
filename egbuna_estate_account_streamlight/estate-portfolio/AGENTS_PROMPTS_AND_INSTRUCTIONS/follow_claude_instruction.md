# Session Deliverables Inventory (Cleaned)

All references to **continue**, **resume**, **OWL ALPHA**, and **Nex N2** have been removed or replaced as requested.

---

# Everything Produced This Session

## Framework Documents

| File | Purpose |
|--------|--------|
| `OPENAGILE_DEVELOPER_MANUAL.md` | Complete 7-phase guide + 6 appendices |
| `FRESH_SESSION_MASTER_PROMPT.md` | v2 master prompt for new Claude sessions |
| `EPM_TEST_TAXONOMY.md` | Full taxonomy adoption and migration map |
| `BUG_REPORT_TEMPLATE.md` | Standard bug reporting template |
| `SYSTEM_SURVEY.md` | VPS codebase audit results |
| `PROJECT_STATE.json` | Machine-readable project state |

---

## OpenAgile Developer Guide Skill

### Directory

```text
openagile-dev-guide/
```

### Files

| File | Purpose |
|--------|--------|
| `SKILL.md` | Hermes skill entry point with smart phase detection |

### References

```text
references/
├── phase-0
├── phase-1
├── phase-2
├── phase-3
├── phase-4
├── phase-5
├── phase-6
└── phase-7
```

Eight interactive phase guides.

### Assets

| File | Purpose |
|--------|--------|
| `assets/ai-workflow-rules-universal.md` | Shared workflow rules |
| `assets/feature-spec-template.md` | F-XXX specification template |
| `assets/gherkin-template.md` | `.feature` template |
| `assets/adr-template.md` | ADR template |
| `assets/handover-template.md` | Handover template |

---

# .context Files

These should be copied into the VPS project.

| File | Purpose |
|--------|--------|
| `.context/AGENTS.md` | Agent entry point |
| `.context/project-overview.md` | Vision, users, scope |
| `.context/architecture.md` | Stack, architecture, invariants |
| `.context/code-standards.md` | Python and TypeScript conventions |
| `.context/ai-workflow-rules.md` | Universal workflow rules |
| `.context/ui-context.md` | Design tokens and UI conventions |
| `.context/progress-tracker.md` | Live feature status |
| `.context/current-issues.md` | Active bugs (gitignored) |

---

# Feature Specifications

## Existing Features

```text
F-001
F-002
F-003
F-004
F-005
F-006
```

Documented existing features.

## Completed Feature

| File | Status |
|--------|--------|
| `F-022-ai-chatbot.md` | Full specification with all Grok gaps resolved |

---

# Handovers

| File | Assigned Agent | Priority | Purpose |
|--------|--------|--------|--------|
| `HO-024-admin-restructure-full-spec.md` | `[hermes]Deepseek:flash` → `[hermes]nemotron-3-ultra-550b-a55b:free` | 🔴 Active | Admin restructure |
| `HO-025-test-taxonomy-migration.md` | `[hermes]Deepseek:flash` | 🔴 Urgent | Test taxonomy migration |

---

# AI Extraction Documents

```text
.ai/
├── FOUNDATION_VISION.md
├── ...
└── EXECUTION_PHILOSOPHY.md
```

Eight system-design extraction documents.

---

# Cleanup

| File | Purpose |
|--------|--------|
| `CLEANUP-001-repo-hygiene.md` | Single commit to clean repository debris |

---

# Claude Session Prompts

| File | When to Use |
|--------|--------|
| `FRESH_SESSION_MASTER_PROMPT.md` | Start a new Claude session for EPM work |
| `OPENAGILE_CLAUDE_CHAT_PROMPT.md` | Start a new project interactively inside Claude |

---

# Hermes Skill Installation

Install into:

```text
~/.hermes/skills/openagile-dev-guide/
```

### Required Files

```text
SKILL.md

references/
├── phase-0
├── phase-1
├── phase-2
├── phase-3
├── phase-4
├── phase-5
├── phase-6
└── phase-7

assets/
├── ai-workflow-rules-universal.md
├── feature-spec-template.md
├── gherkin-template.md
├── adr-template.md
└── handover-template.md
```

---

# Copy to VPS Project Root

```text
.context/
├── AGENTS.md
├── project-overview.md
├── architecture.md
├── code-standards.md
├── ai-workflow-rules.md
├── ui-context.md
├── progress-tracker.md
├── current-issues.md   (gitignore)
└── feature-specs/
    ├── F-001
    ├── F-002
    ├── F-003
    ├── F-004
    ├── F-005
    ├── F-006
    └── F-022-ai-chatbot.md
```

---

# Agent Tasks

## Immediate Work

| File | Agent | Priority |
|--------|--------|--------|
| `HO-025-test-taxonomy-migration.md` | `[hermes]Deepseek:flash` | 🔴 Do First |
| `HO-024-admin-restructure-full-spec.md` | `[hermes]Deepseek:flash` → `[hermes]nemotron-3-ultra-550b-a55b:free` | 🔴 Active |
| `CLEANUP-001-repo-hygiene.md` | Either Agent | 🟡 One Commit |

---

# Local Reference Documents

| File | Purpose |
|--------|--------|
| `OPENAGILE_DEVELOPER_MANUAL.md` | Complete framework (7 phases + 6 appendices) |
| `BUG_REPORT_TEMPLATE.md` | Standard bug reporting workflow |
| `EPM_TEST_TAXONOMY.md` | Taxonomy reference and migration guide |
| `SYSTEM_SURVEY.md` | VPS audit results |
| `PROJECT_STATE.json` | Project state snapshot |

---

# Outstanding Work

## Priority 1

### F-016 User Management Specification

Roles and permissions underpin all Phase 3C features.

Create:

```text
F-016-user-management.md
```

---

## Priority 2

### AT-004 Acceptance Test

Create:

```text
AT-004
```

Purpose:

- Acceptance test for the HO-024 Admin Restructure.
- Written after HO-024 implementation results are available.

---

## Priority 3

### F-007 NAV History Specification

Gherkin scenarios already exist:

```text
SC-025
SC-026
SC-027
SC-028
SC-029
SC-030
SC-031
```

Needs:

```text
F-007-nav-history.md
```

---

# Final Status

✅ OpenAgile framework complete  
✅ Hermes skill complete  
✅ Claude chat prompt complete  
✅ Context system complete  
✅ Existing feature documentation complete  
✅ AI extraction documents complete  
✅ Test taxonomy complete  
✅ VPS survey complete  
✅ Cleanup plan complete  

## Remaining Deliverables

1. `F-016-user-management.md`
2. `AT-004`
3. `F-007-nav-history.md`
