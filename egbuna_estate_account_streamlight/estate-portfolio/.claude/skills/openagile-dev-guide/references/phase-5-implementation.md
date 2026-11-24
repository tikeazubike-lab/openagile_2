# Phase 5 — Implementation (Red → Green → Refactor)

**Goal**: write the minimum production code needed to turn the failing tests from Phase 4
green, then refactor. This phase is gated — do not enter it for a feature that hasn't cleared
Phase 4.

## Step A — Verify the gate is open

Before writing any implementation code:

```bash
# confirm the .feature and test files exist for this F-XXX
ls docs/testing/features/F-XXX.feature 2>/dev/null
grep -r "F-XXX" tests/ 2>/dev/null
```

If either is missing, **stop** and route back to Phase 4. Tell the user: "F-XXX doesn't have a
spec/test pair yet — implementing now would be vibecoding. Let's go back to Phase 4 first."

## Step B — Implement to green

1. Run the generated test suite and confirm it fails for the expected reason (missing
   implementation, not a broken test).
2. Write the minimal code to satisfy the first failing test. Do not implement ahead of the
   tests — no speculative generality.
3. Re-run tests after each small change. Repeat until all tests for this feature are green.
4. If a test reveals the spec itself was wrong or ambiguous, stop and go back to
   gherkin-spec-agent to refine the `.feature` file — don't quietly change test expectations to
   match broken code.

## Step C — Refactor

Once green, refactor for clarity/duplication with tests as the safety net. Re-run tests after
refactoring; they must stay green.

## Step D — Update tracking

Update `.context/progress-tracker.md`: mark Implemented = ✅ for this feature. Leave Accepted
unchecked until Phase 6.

If anything unusual came up during implementation (a workaround, a deviation from the ADR, a
new dependency), log it in `.context/current-issues.md` so the next session or agent has
context.

## Checklist before moving to Phase 6

- [ ] Implementation gate was confirmed open before coding started
- [ ] All tests for this feature are green
- [ ] No implementation exists without a corresponding test
- [ ] Refactor pass complete, tests still green
- [ ] `.context/progress-tracker.md` updated
