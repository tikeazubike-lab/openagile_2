# Phase 3 — Agent Setup

**Goal**: produce `.context/AGENTS.md`, `.context/ai-workflow-rules.md`,
`.context/ui-context.md` (if relevant), and `.context/progress-tracker.md`.

## Questions to ask (2–3 at a time)

Round 1:
1. Which AI agents/tools will work on this project? (Claude, Cursor, Antigravity, Hermes,
   Deepseek, other — multi-select)
2. Will one agent own the whole codebase, or should domains be split (e.g. frontend vs backend)?

Round 2:
3. Is `gherkin-spec-agent` (spec-first Gherkin discipline) already available in this
   environment? If yes, it will be the required gate before any Phase 5 implementation.
4. Any existing agent config files to preserve (`.cursor/rules/`, `~/.hermes/config.yaml`)?

## Output

Write `.context/AGENTS.md` — one entry per agent:

```markdown
# Agents

## <Agent Name>
- Role: <domain owned>
- File domain: <paths this agent may touch>
- Spec discipline: routes all new features through gherkin-spec-agent before implementation
```

Copy `assets/ai-workflow-rules-universal.md` to `.context/ai-workflow-rules.md` **unmodified**.
Never ask questions about this file's content.

If there's a UI: write `.context/ui-context.md` with component library, design tokens, and
page inventory (ask only if not already answered in Phase 2).

Initialize `.context/progress-tracker.md`:

```markdown
# Progress Tracker

## Phase Status
- [x] Phase 0 — Idea Capture
- [x] Phase 1 — Project Foundation
- [x] Phase 2 — Architecture Decisions
- [x] Phase 3 — Agent Setup
- [ ] Phase 4 — Spec Writing
- [ ] Phase 5 — Implementation
- [ ] Phase 6 — Acceptance / Deployment
- [ ] Phase 7 — Maintenance

## Features
| ID | Name | Spec | Tests | Implemented | Accepted |
|----|------|------|-------|-------------|----------|
```

## Checklist before moving to Phase 4

- [ ] `.context/AGENTS.md` written with at least one agent entry
- [ ] `.context/ai-workflow-rules.md` copied unmodified
- [ ] `.context/progress-tracker.md` initialized
- [ ] Confirmed whether gherkin-spec-agent is available (affects Phase 4 handoff)
