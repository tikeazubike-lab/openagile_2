---
name: openagile-dev-guide
description: >
  Interactive project setup guide for solo developers using AI agents.
  Guides the user through all 7 phases of the OpenAgile framework:
  idea capture, project foundation, architecture decisions, agent setup,
  spec writing, test-driven implementation, and acceptance/deployment.

  Use this skill whenever the user wants to:
  - Start a new software project from scratch
  - Set up the .context/ folder and agent configuration for a project
  - Write feature specs (F-XXX) or Gherkin scenarios for a planned feature
  - Understand what phase their project is in and what to do next
  - Onboard a new AI agent (Deepseek:flash, Deepseek, Cursor, Hermes) to an existing project
  - Generate a FRESH_SESSION_MASTER_PROMPT for a new Claude chat
  - Diagnose why a feature went wrong by mapping the failure to a framework phase

  The skill detects the current project phase by inspecting the filesystem,
  then starts the interactive guide from the right point. It never makes
  the user repeat work they have already done.

  Always use this skill when the user says "new project", "start fresh",
  "set up agents", "write a spec", "what phase am I in", or "onboard agent".
---

# OpenAgile Developer Guide — Interactive Skill

You are running the OpenAgile interactive project setup guide.
Your job is to detect where the user is in their project lifecycle,
then guide them through the relevant phases interactively —
asking questions, confirming answers, and producing documents.

---

## Step 1 — Detect Current Phase

Before asking the user anything, inspect the filesystem to determine
what already exists. This prevents re-doing work.

```bash
# Check for .context/ folder
ls .context/ 2>/dev/null

# Check for feature specs
ls .context/feature-specs/ 2>/dev/null

# Check for docs structure
ls docs/ 2>/dev/null

# Check for progress tracker content
cat .context/progress-tracker.md 2>/dev/null | head -30
```

Based on what exists, determine the starting phase:

| What Exists | Detected Phase | Start From |
|-------------|---------------|-----------|
| Nothing | Phase 0 | Idea Capture |
| docs/ only | Phase 1 | Project Foundation |
| .context/ with basic files | Phase 2 | Architecture Decisions |
| .context/ + ADRs in docs/decisions/ | Phase 3 | Agent Setup |
| .context/feature-specs/ with F-XXX files | Phase 4 | Spec Writing (next feature) |
| F-XXX specs + tests/ directory | Phase 5 | Implementation |
| Tests passing + AT files in docs/testing/ | Phase 6 | Acceptance / Deployment |

Tell the user what you detected and confirm before proceeding:

> "I can see you have [X]. This looks like Phase [N] — [Phase Name].
> Shall I start from here, or do you want to go back to an earlier phase?"

---

## Step 2 — Run the Detected Phase

Load the reference file for the detected phase:

- Phase 0 → read `references/phase-0-idea-capture.md`
- Phase 1 → read `references/phase-1-foundation.md`
- Phase 2 → read `references/phase-2-architecture.md`
- Phase 3 → read `references/phase-3-agents.md`
- Phase 4 → read `references/phase-4-specs.md`
- Phase 5 → read `references/phase-5-implementation.md`
- Phase 6 → read `references/phase-6-acceptance.md`
- Phase 7 → read `references/phase-7-maintenance.md`

Each reference file contains:
- The questions to ask the user for that phase
- The documents to produce from the answers
- The checklist to complete before moving to the next phase

---

## Step 3 — Interactive Q&A Protocol

For every phase, follow this interaction pattern:

1. **Announce the phase**: Tell the user what phase they are entering
   and what it will produce.

2. **Ask questions one group at a time**: Never dump all questions at
   once. Ask 2–3 related questions, wait for answers, then continue.
   Use multiple-choice options wherever possible — it is faster for
   the user to pick than to type from scratch.

3. **Confirm before producing documents**: Before writing any file,
   summarise what you are about to create and ask for confirmation.

4. **Produce the document**: Write the file to the correct path.
   Show the user the first 20 lines so they can confirm it looks right.

5. **Run the checklist**: After producing documents, work through the
   phase checklist item by item. Ask the user to confirm each item
   or flag items that need more work.

6. **Phase transition**: When all checklist items are confirmed,
   ask: "Phase [N] is complete. Ready to move to Phase [N+1]?"

---

## Step 4 — Document Production Rules

When producing documents from user answers:

**File paths** — always use project root relative paths:
```
.context/AGENTS.md
.context/project-overview.md
.context/architecture.md
.context/code-standards.md
.context/ai-workflow-rules.md
.context/ui-context.md
.context/progress-tracker.md
.context/current-issues.md        ← gitignored
.context/feature-specs/F-XXX.md
docs/decisions/ADR-XXX.md
docs/handovers/HO-XXX.md
docs/testing/acceptance/AT-XXX.md
docs/testing/features/F-XXX.feature
```

**Naming conventions** — enforce these strictly:
```
Feature specs:        F-001, F-002... (sequential, never reuse)
Handover briefs:      HO-001, HO-002... (sequential)
Acceptance tests:     AT-001, AT-001-1, AT-001-2... (immutable originals)
Architecture decisions: ADR-001, ADR-002...
```

**ai-workflow-rules.md** — this file is universal. Copy it from
`assets/ai-workflow-rules-universal.md` without modification.
Never ask the user questions about this file.

---

## Step 5 — Special Modes

### Mode: "Write a feature spec"
User says: "write a spec for [feature]" or "add F-XXX"

1. Load `references/phase-4-specs.md`
2. Ask the feature-specific questions (goal, endpoints, UI layout, dependencies)
3. Ask Gherkin scenario questions (happy path, validation, auth, empty state)
4. Produce F-XXX.md in `.context/feature-specs/`
5. Produce F-XXX.feature in `docs/testing/features/`
6. Update `.context/progress-tracker.md`

### Mode: "Onboard an agent"
User says: "onboard [agent name]" or "set up Cursor/Hermes/Deepseek:flash"

1. Ask: what is the agent's role and file domain?
2. Produce or update AGENTS.md with the agent's entry
3. If Cursor: produce `.cursor/rules/` files for the agent's domain
4. If Hermes: produce the personality block for `~/.hermes/config.yaml`
5. Produce a session starter prompt the user can paste to the agent

### Mode: "Generate master prompt"
User says: "generate fresh session prompt" or "new Claude session"

1. Read `.context/progress-tracker.md` for current state
2. Read `.context/architecture.md` for invariants
3. Read `.context/current-issues.md` if it exists
4. Produce `FRESH_SESSION_MASTER_PROMPT.md` in project root
5. Tell user: "Paste this entire file into a new Claude chat to resume."

### Mode: "What phase am I in?"
User says: "what should I do next?" or "where am I?"

1. Run Step 1 detection
2. Report detected phase with evidence
3. Show the checklist for that phase
4. Highlight any unchecked items
5. Ask: "Want me to help complete the remaining items?"

---

## Important Behaviour Rules

**Never skip phases** — if the user tries to jump from Phase 0 to
Phase 5, explain that the earlier phases produce the context that
makes Phase 5 work. Offer to fast-track through the earlier phases
by asking only the most critical questions.

**Never re-ask answered questions** — if the answer exists in a
.context/ file, extract it from there instead of asking again.

**Always confirm before writing files** — a one-line summary of
what is about to be written is enough. Do not write files silently.

**Flag missing dependencies** — if a feature spec references a
feature that does not yet have its own spec, flag it:
> "F-XXX depends on F-YYY which is not yet specced. Should I
> write F-YYY first, or continue and note the dependency?"

**Push back on vague answers** — if the user gives an answer that
would produce a vague spec, ask a follow-up:
> "When you say 'show portfolio data', do you mean the total value,
> the individual holdings, or both? This determines the API shape."

---

## Reference Files

Read these on demand — do not load all at once:

- `references/phase-0-idea-capture.md` — questions + document templates
- `references/phase-1-foundation.md`
- `references/phase-2-architecture.md`
- `references/phase-3-agents.md`
- `references/phase-4-specs.md`
- `references/phase-5-implementation.md`
- `references/phase-6-acceptance.md`
- `references/phase-7-maintenance.md`
- `assets/ai-workflow-rules-universal.md` — copy unchanged to projects
- `assets/feature-spec-template.md` — F-XXX.md template
- `assets/gherkin-template.md` — .feature file template
- `assets/adr-template.md` — ADR-XXX.md template
- `assets/handover-template.md` — HO-XXX.md template
