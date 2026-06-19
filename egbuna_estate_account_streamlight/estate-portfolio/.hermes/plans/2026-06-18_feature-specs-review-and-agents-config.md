# Feature Specs Review + Model Automation Config Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** (1) Fix inconsistencies in the newly added feature spec files, and (2) create the agent-to-model routing config file that automates the use of the three models defined in AGENTS.md.

**Architecture:** Feature specs use YAML frontmatter fields that must stay consistent with `.context/progress-tracker.md`. The model automation file is a YAML config that Hermes (or any orchestrator) can read to route subagent work to the correct provider/model pair.

**Tech Stack:** YAML config file; markdown frontmatter parsing.

---

## Context / Assumptions

- `.context/` is the single source of truth over `.cursor/rules/`.
- Feature specs are created only after a feature has gone through the full RED→GREEN cycle and passed acceptance tests. The existing F-001–F-006 specs were written retroactively (the features exist in code), so their checklists may reflect what *should* be tested rather than what was actually verified.
- The three models in AGENTS.md need a machine-readable mapping so the orchestrator can dispatch `delegate_task` or `mixture_of_agents` calls without hardcoding model names in every prompt.

---

## Part A: Feature Spec Fixes

### A1: Fix F-005 title field

**Objective:** F-005 frontmatter `title` says "Bugs Open" but should be "Price History".

**Files:**
- Modify: `.context/feature-specs/F-005-price-history.md:5`

**Change:**
```yaml
# Before
title: Bugs Open

# After
title: Price History
```

**Verification:** `head -6 .context/feature-specs/F-005-price-history.md` shows `title: Price History`.

---

### A2: Fix F-005 status field

**Objective:** F-005 frontmatter `status` says "COMPLETE" but progress-tracker.md says "⚠️ Bugs open".

**Files:**
- Modify: `.context/feature-specs/F-005-price-history.md:6`

**Change:**
```yaml
# Before
status: COMPLETE

# After
status: BUGS-OPEN
```

**Verification:** Confirm F-005 frontmatter matches progress-tracker.md status.

---

### A3: Fix F-006 status field

**Objective:** F-006 frontmatter `status` says "COMPLETE" but progress-tracker.md says "⚠️ Bugs open".

**Files:**
- Modify: `.context/feature-specs/F-006-registrars.md:5`

**Change:**
```yaml
# Before
status: COMPLETE

# After
status: BUGS-OPEN
```

**Verification:** Confirm F-006 frontmatter matches progress-tracker.md status.

---

### A4: Align status values across all frontmatter

**Objective:** Ensure all F-001–F-006 frontmatter `status` values use a consistent enum: `COMPLETE` or `BUGS-OPEN` (matching the convention already used by F-002 and F-003).

**Files:**
- Check: `.context/feature-specs/F-001-authentication.md:7` — currently `Complete` (wrong case)
- Check: `.context/feature-specs/F-004-price-entry.md:7` — currently `COMPLETE` (correct)

**Change for F-001:**
```yaml
# Before
status: Complete

# After
status: COMPLETE
```

**Verification:** All six specs use either `COMPLETE` or `BUGS-OPEN`.

---

### A5: Verify F-001 sign-off is accurate

**Objective:** F-001 sign-off says "All checklist items verified" and "No open bugs" — confirm this matches reality. If acceptance tests were not actually run, add a note.

**Files:**
- Review: `.context/feature-specs/F-001-authentication.md:121-125`

**Action:** If the user confirms F-001 was never formally acceptance-tested, add a note:
```markdown
## Sign-Off
- [x] Feature code exists and is functional
- [ ] Formal acceptance test (API + UI) not yet run under RED-GREEN cycle
```

**Verification:** Sign-off reflects actual testing state.

---

## Part B: Model Automation Config File

### B1: Create `.context/agents.yaml`

**Objective:** Create a machine-readable config that maps agent roles to their model providers, so the orchestrator can auto-dispatch subagent work.

**Files:**
- Create: `.context/agents.yaml`

**Complete content:**

```yaml
# Agent-to-Model Routing Configuration
# Single source of truth for multi-agent model assignments.
# Referenced by: AGENTS.md, .cursor/rules/, ai-workflow-rules.md
#
# Last verified: 2026-06-18

agents:
  owl-alpha:
    role: backend-executor
    model: openrouter/owl-alpha
    owns:
      - backend/
      - docker-compose.v2.yml
      - deploy.sh
    never_touches:
      - estate-portfolio-manager/src/
    responsibilities:
      - API development
      - Database logic
      - Test writing (unit + integration)
      - Bug fixing based on RCA
    workflow_gate: Implements ONLY after DeepSeek approval and failing tests exist

  kimi-k25:
    role: frontend-executor
    model: moonshotai/kimi-k2.5
    owns:
      - estate-portfolio-manager/src/
    never_touches:
      - backend/
    responsibilities:
      - UI implementation
      - Component design
      - Frontend state logic
      - API integration on UI layer
      - UI test validation
    workflow_gate: Must not modify backend logic. UI only.

  deepseek:
    role: reviewer-architect
    model: deepseek/deepseek-v4-flash
    owns: []  # No code execution
    responsibilities:
      - Architecture validation
      - Feature spec interpretation
      - Test plan approval
      - Code review gatekeeping
      - Final correctness validation
      - Detect logic inconsistencies
    workflow_gate: No implementation allowed. Only review, decide, approve, or reject.

routing:
  # When dispatching work, use these rules:
  backend_task:
    primary: owl-alpha
    reviewer: deepseek
  frontend_task:
    primary: kimi-k25
    reviewer: deepseek
  complex_analytical:
    primary: deepseek  # Routes to mixture_of_agents for multi-model reasoning
```

**Step 2: Verify file is valid YAML**
Run: `python3 -c "import yaml; yaml.safe_load(open('.context/agents.yaml'))"`
Expected: No output (valid YAML)

**Step 3: Cross-reference with AGENTS.md**
Confirm the three agent names in AGENTS.md match the keys in agents.yaml:
- `Owl Alpha` → `owl-alpha` ✓
- `Kimi K2.5` → `kimi-k25` ✓
- `DeepSeek` → `deepseek` ✓

---

## Part C: Update References

### C1: Add agents.yaml reference to AGENTS.md

**Objective:** Add a line in AGENTS.md pointing to the new config file.

**Files:**
- Modify: `.context/AGENT.md:11-19` (Before Every Session section)

**Change:** Add line after the existing file list:
```
8. .context/agents.yaml          (agent-to-model routing)
```

---

### C2: Add agents.yaml reference to ai-workflow-rules.md

**Objective:** Add a reference in ai-workflow-rules.md so agents know where to find model assignments.

**Files:**
- Modify: `.context/ai-workflow-rules.md:1-6` (after title)

**Change:** Add after the first line:
```
> Model assignments: see .context/agents.yaml
```

---

## Execution Order

1. Part A (A1–A5) — Fix frontmatter inconsistencies (5 min)
2. Part B (B1) — Create agents.yaml (5 min)
3. Part C (C1–C2) — Add references (2 min)

## Verification

- [ ] All F-001–F-006 frontmatter `status` values are `COMPLETE` or `BUGS-OPEN`
- [ ] F-005 title is "Price History" (not "Bugs Open")
- [ ] F-005 and F-006 status is `BUGS-OPEN` (matching progress-tracker.md)
- [ ] `.context/agents.yaml` exists and is valid YAML
- [ ] agents.yaml keys match AGENTS.md agent names
- [ ] AGENTS.md references agents.yaml
- [ ] ai-workflow-rules.md references agents.yaml

## Risks

- **Risk:** F-001/F-004 "COMPLETE" status may be inaccurate if acceptance tests were never formally run. **Mitigation:** User should confirm which features have actually passed acceptance.
- **Risk:** agents.yaml model names may become stale when providers update. **Mitigation:** File includes "Last verified" date; update when config changes.

## Open Questions

1. Should the `status` enum also include `IN-PROGRESS` for features currently being worked on?
2. Should agents.yaml include provider API base URLs, or keep it model-only?
3. Does the orchestrator (Hermes) natively support YAML agent configs, or should this be a reference doc only?
