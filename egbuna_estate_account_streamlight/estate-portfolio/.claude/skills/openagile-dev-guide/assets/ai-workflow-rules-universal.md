# AI Workflow Rules

These rules apply to every AI agent (Claude, Cursor, Antigravity, Hermes, Deepseek, or other)
working on this project. They are copied unmodified from the OpenAgile skill — do not edit per
project.

## The Core Rule

No production code is written for a feature that does not have:
1. A feature brief (`F-XXX.md`)
2. A formal Gherkin spec (`.feature` file)
3. A generated, currently-failing test suite proving the spec is testable

If you are an agent about to write implementation code and this chain doesn't exist for the
feature you're touching, stop and route the request back through the OpenAgile Phase 4 spec
workflow instead of writing code directly.

## Test Discipline

- Tests are written before implementation, not after.
- A test that was never seen to fail (red) before the implementation made it pass (green) is
  not trustworthy — don't skip the red step even when the fix seems obvious.
- Refactors must not change test expectations to match new code; if a refactor breaks a test,
  either the refactor is wrong or the spec needs revisiting — decide explicitly, don't silently
  edit the assertion.

## Documentation Discipline

- Any non-trivial architectural decision gets an ADR in `docs/decisions/`, not just a code
  comment. Comments explain the how; ADRs explain the why and the alternatives considered.
- `.context/progress-tracker.md` is the source of truth for project state. Update it as part of
  finishing a unit of work, not as an afterthought.
- Never let `.context/architecture.md` drift from what's actually deployed. If a decision
  changes, update the doc in the same session as the code change.

## Agent Boundaries

- Respect the file domains declared in `.context/AGENTS.md`. If your task requires touching
  another agent's domain, flag it rather than silently crossing the boundary.
- When picking up a session, read `.context/progress-tracker.md` and
  `.context/current-issues.md` before doing anything else — don't re-derive context that's
  already been captured.

## No Vibecoding

"Vibecoding" here means writing implementation code from a natural-language description without
an intervening formal spec and test. It is not permitted on this project, regardless of how
small or obvious the change seems. Small changes still get a scenario added to the relevant
`.feature` file, even if it's a single Given/When/Then.
