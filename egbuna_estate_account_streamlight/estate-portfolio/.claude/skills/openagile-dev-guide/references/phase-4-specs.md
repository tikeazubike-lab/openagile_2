# Phase 4 — Spec Writing (Hybrid: OpenAgile + gherkin-spec-agent)

**Goal**: produce a feature brief (`F-XXX.md`) and then hand off to `gherkin-spec-agent` to
produce the formal Gherkin spec, IR, and generated test suite. OpenAgile does **not** write
Given/When/Then scenarios itself when gherkin-spec-agent is available — that's a deliberate
separation of concerns: OpenAgile owns "what and why", gherkin-spec-agent owns "prove it".

## Step A — Feature brief questions (2–3 at a time)

Round 1:
1. Feature name (one line, verb-first, becomes the F-XXX title)?
2. What's the user-facing goal — what can a user do after this ships that they couldn't before?

Round 2:
3. Any API endpoints, UI screens, or data model changes involved?
4. Does this feature depend on another feature that doesn't exist yet? (check
   `.context/feature-specs/` — flag if so, per the "Flag missing dependencies" rule in SKILL.md)

## Step B — Write F-XXX.md

Use `assets/feature-spec-template.md`. Assign the next sequential F-XXX number by checking
existing files in `.context/feature-specs/` — never reuse a number, even for abandoned features.

## Step C — Hand off to gherkin-spec-agent

Tell the user: "Handing this off to gherkin-spec-agent to write the formal spec and generate
tests — this is the part where we make sure nothing gets implemented without proof it works."

Pass gherkin-spec-agent:
- The F-XXX.md content (goal, endpoints, data model)
- The happy path, at least one edge case, and any auth/permission variations to cover

gherkin-spec-agent will:
1. Author `docs/testing/features/F-XXX.feature` (Given/When/Then, quality-gated)
2. Parse it to IR and validate
3. Detect the stack and generate the test suite
4. Produce the traceability matrix
5. Report whether the implementation gate is open

**Do not proceed to Phase 5 until gherkin-spec-agent confirms the gate is open** (tests exist,
are wired up, and are currently red — not yet passing, since no implementation exists yet).

## Step D — Update tracking

Update the Features table in `.context/progress-tracker.md`:
mark Spec = ✅ and Tests = ✅ (red) for this feature. Implemented/Accepted stay unchecked.

## Fallback: no gherkin-spec-agent

If gherkin-spec-agent is not installed or unreachable, tell the user explicitly you're using
the degraded inline path, then:

1. Write the `.feature` file yourself using standard Gherkin (Feature / Background / Scenario /
   Given / When / Then), applying the same quality gates: every `Then` observable, no scenario
   over 5 steps, no ambiguous verbs ("handles", "manages").
2. Generate a minimal test skeleton in the detected stack's test framework, one test per
   scenario, each currently failing (no implementation yet).
3. Note in `.context/current-issues.md` that gherkin-spec-agent was unavailable, so the user
   knows the spec discipline was self-applied rather than delegated.

## Checklist before moving to Phase 5

- [ ] F-XXX.md written and confirmed
- [ ] `.feature` file exists in `docs/testing/features/`
- [ ] Test suite generated and currently failing (red)
- [ ] Traceability matrix produced
- [ ] Implementation gate confirmed open
- [ ] `.context/progress-tracker.md` updated
