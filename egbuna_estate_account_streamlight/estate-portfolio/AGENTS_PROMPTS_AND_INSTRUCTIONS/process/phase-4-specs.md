# Phase 4 — Spec Writing

## What This Phase Produces (Per Feature)
- F-XXX.md in .context/feature-specs/
- F-XXX.feature in docs/testing/features/
- Updated .context/progress-tracker.md

---

## Step 1 — Feature Identification

If entering Phase 4 fresh (no features listed yet):

> "Let's build your feature list. Name every capability the finished
> system needs — don't worry about order yet. Just brainstorm.
>
> Think in terms of: what can the user DO in the finished system?
>
> Examples:
> - Log in and stay logged in for 30 days
> - View all holdings with current market values
> - Upload NGX price PDF to update prices
> - Add a new stock holding
>
> List yours:"

After the list is given, help number them:
> "I count [N] features. Let me suggest an ordering based on dependencies.
> Features that everything else depends on should come first."

Produce the feature list in progress-tracker.md with all statuses = PLANNED.

---

## Step 2 — Spec Questions Per Feature

Ask these for each F-XXX feature in sequence.
Do one feature at a time — do not ask about F-003 until F-002 is done.

### Group A — Goal and Scope

> "Feature [F-XXX]: [feature name]
>
> 1. In one sentence: what does this feature produce when it is complete?
>    (Not what it does — what tangible output or state change results?)
>
> 2. Does this feature depend on any other feature being complete first?
>    If yes, which ones and why?
>
> 3. Who can use this feature?
>    a) Admin only
>    b) All authenticated users (admin + read-only)
>    c) Public (no auth required)"

### Group B — Backend (if applicable)

> "Backend for F-XXX:
>
> 1. What database table(s) does this feature need?
>    - New tables to create?
>    - Existing tables to modify?
>
> 2. What API endpoints are needed?
>    For each endpoint, tell me:
>    - Method (GET/POST/PATCH/PUT/DELETE)
>    - Path (e.g. /api/v1/holdings)
>    - What it does (one sentence)
>    - Auth required? (admin only / any authenticated / public)
>
> 3. What does the API response look like?
>    Show me the JSON structure — even approximately."

If the response is approximate, refine it:
> "Let me lock this down. For the [field], is it:
>   a) A string ('12345.50')  b) A number (12345.50)  c) A boolean  d) Null when empty"

### Group C — Frontend (if applicable)

> "Frontend for F-XXX:
>
> 1. What does the user see when they open this page?
>    Describe the layout — top to bottom, left to right.
>
> 2. What happens when the page loads?
>    (What API call fires? What shows while loading? What if empty?)
>
> 3. What actions can the user take?
>    For each action: what triggers it, what happens, what is the result?
>
> 4. What does the empty state look like?
>    (When there is no data to show — not a blank page)"

### Group D — Acceptance Criteria

> "How do we know this feature is done? For each layer:
>
> [DB] Database:
>   What SQL query confirms the data was stored correctly?
>
> [API] Contract:
>   What curl command proves the endpoint works?
>   What response field proves the contract is correct?
>
> [UI] Interface:
>   What do you see in the browser that confirms it works?
>   What does the empty state look like?
>   What happens when a read-only user visits?
>   What happens when an unauthenticated user visits?"

---

## Step 3 — Gherkin Scenarios

After the spec questions, generate Gherkin scenarios:

> "Now let's write the test scenarios. I'll generate them from
> your spec and you confirm each one.
>
> I always write scenarios for these categories — tell me if any
> don't apply:
>   1. Happy path (normal successful case)
>   2. Validation error (bad input rejected)
>   3. Auth/role check (wrong role gets 403)
>   4. Empty state (no data exists yet)
>   5. Data persistence (DB actually changed)
>   6. [Feature-specific edge cases]"

Generate the scenarios, then ask:
> "Does this cover everything you want to test? Any edge cases
> I missed that burned you before?"

---

## Common Pushbacks to Apply

**If the goal is vague**:
> "When you say 'show portfolio data', do you mean:
>   a) The total value only
>   b) The breakdown by holding
>   c) Both, on the same page
> This determines whether it's one API call or two."

**If the API shape is approximate**:
> "I need the exact JSON. Is 'current_value' a string '45000.00'
> or a number 45000.0? This is enforced in the acceptance test."

**If dependencies are missing**:
> "This feature uses the Company table which is created in F-XXX.
> That spec hasn't been written yet. Should I write F-XXX first,
> or note it as a dependency and continue?"

**If empty states are skipped**:
> "What does the user see if there are no [items] yet?
> This is not optional — every EPM crash in AT-003 was a
> missing null-safety check traced to an unspecced empty state."

---

## Documents to Produce

1. `.context/feature-specs/F-XXX.md` — full spec
2. `docs/testing/features/F-XXX-name.feature` — Gherkin scenarios
3. Update `.context/progress-tracker.md` — status = PLANNED with spec link

---

## Phase 4 Checklist (Per Feature)

```
Feature Spec:
[ ] Goal is one clear sentence (not vague)
[ ] All backend endpoints listed with exact paths and methods
[ ] API response shape is exact JSON (not approximate)
[ ] All frontend files listed
[ ] UI layout described precisely
[ ] Empty state described
[ ] Role behaviour described (admin vs readonly vs unauthenticated)
[ ] Dependencies on other features explicit

Gherkin:
[ ] Happy path scenario
[ ] Validation error scenario (at least one)
[ ] Auth/role scenario
[ ] Empty state scenario
[ ] Data persistence scenario
[ ] Scenario IDs sequential (SC-XXX)

Quality:
[ ] Two agents reading the spec would produce the same output
[ ] No "TBD" fields in the API shape
[ ] progress-tracker.md updated
```
