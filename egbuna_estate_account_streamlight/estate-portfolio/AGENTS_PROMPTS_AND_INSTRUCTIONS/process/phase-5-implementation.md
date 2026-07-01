# Phase 5 — Test-Driven Implementation

## What This Phase Produces (Per Feature)
- pytest test file in backend/tests/integration/test_F-XXX.py
- Confirmed RED test run (evidence of failure)
- Production code making tests GREEN
- Passing 3-layer acceptance checklist

---

## Step 1 — Confirm Prerequisites

Before any implementation starts, confirm:

> "Before we implement F-XXX, three prerequisites:
>
> 1. Is .context/feature-specs/F-XXX.md complete and approved?
> 2. Is docs/testing/features/F-XXX.feature written with scenarios?
> 3. Are all dependencies (other F-XXX features) complete?
>
> If any are no — stop. Complete those first."

---

## Step 2 — Test Writing Questions

Ask the implementing agent (or the user if directing an agent):

> "Which agent is implementing F-XXX?
>   a) Antigravity (backend first)
>   b) Deepseek v4 (frontend — only after backend is complete)
>   c) Both (sequence: Antigravity → Deepseek v4)
>
> For the backend tests:
> - Test file location: backend/tests/integration/test_f[XXX]_[name].py
> - Test framework: pytest + httpx (async)
> - Traceability format: # Spec: F-XXX.feature | SC-XXX above each assert
>
> For the frontend tests:
> - Test file location: estate-portfolio-manager/src/tests/
> - Framework: vitest + React Testing Library
>
> Confirm the test structure looks correct before writing production code."

---

## Step 3 — RED Phase Confirmation

This is the most important step. Never skip it.

> "The agent must confirm tests are FAILING before writing production code.
>
> Expected RED evidence:
>   Backend:  FAILED test_sc007_... - AssertionError: assert 404 == 200
>   Frontend: FAIL src/tests/... - Cannot find element...
>
> If tests PASS before any production code exists:
>   → The tests are testing the wrong thing
>   → Stop and fix the tests first
>   → Common cause: testing a route that already existed from another feature
>
> Ask the agent: 'Paste the pytest/vitest output showing the failing tests.'"

---

## Step 4 — Implementation Guidance Questions

> "What is the implementation sequence for F-XXX?
>
> For backend:
>   1. Alembic migration first (if new table needed)
>   2. SQLAlchemy model update in models.py
>   3. Pydantic schemas (request + response models)
>   4. Router function implementation
>   5. Wire router in main.py
>   6. Run tests → GREEN
>
> For frontend:
>   7. TanStack Query hook in queries.ts
>   8. Route component in src/routes/_app.XXX.tsx
>   9. Child components as needed
>   10. Run tests → GREEN
>
> Is there anything in F-XXX that doesn't fit this sequence?"

---

## Step 5 — Common Implementation Issues (Ask Proactively)

Before the agent starts, surface known pitfalls:

> "A few things that commonly cause issues — confirm these are handled:
>
> 1. Monetary fields: are they Decimal in the model and string in the
>    API response? (Not float anywhere in the chain)
>
> 2. Soft delete: does the endpoint filter deleted_at IS NULL?
>    Does the delete operation set datetime.now(timezone.utc)?
>    (Not datetime.utcnow() — it creates naive datetimes)
>
> 3. Auth guard: does the endpoint use require_admin() for write
>    operations? get_current_user() for read operations?
>
> 4. Empty state: does the frontend handle null/undefined API fields
>    with optional chaining and ?? fallbacks?
>
> 5. Query invalidation: after any mutation, does the frontend
>    invalidate all related query keys?"

---

## Step 6 — 3-Layer Acceptance Checklist

After tests are GREEN, run the acceptance checklist:

### [DB] Layer — PostgreSQL Verification

> "Verify the database state directly. For each DB checklist item:
>
> Connect: docker compose exec postgres psql -U [user] -d [database]
>
> For each item in the F-XXX spec [DB] checklist:
>   1. Write the SQL query
>   2. Run it
>   3. Confirm the result matches the spec
>   4. Mark the item [x] or [fail]"

### [API] Layer — Contract Verification

> "Verify the API contract. For each [API] checklist item:
>
> Method: curl with the epm_token cookie, or DevTools Network tab
>
> Key checks that must never be skipped:
>   - Monetary fields are JSON strings, not floats:
>     python3 -c 'import json,sys; d=json.load(sys.stdin);
>     print(type(d[\"data\"][0][\"current_value\"]))'
>     Expected: <class 'str'>
>
>   - Auth enforcement (test with no cookie):
>     curl without -b flag → expect 401
>
>   - Role enforcement (test with readonly token):
>     POST/PATCH/DELETE → expect 403"

### [UI] Layer — Browser Verification

> "Verify the browser rendering. For each [UI] checklist item:
>
> Open: [staging URL]
> Open DevTools (F12)
>
> Console tab: zero errors before interacting with the feature
> Network tab: confirm request payload and response shape
> Visual: confirm data renders, empty states work, role controls correct
>
> Role tests:
>   - If no readonly user exists yet → mark as [skip] with reason
>   - Create a readonly user (when F-016 is complete) to unblock"

---

## Step 7 — Handover Brief

After all checklist items pass:

> "Phase 5 complete for F-XXX. Now produce the handover brief:
>
> File: docs/handovers/HO-XXX.md
>
> It must include:
>   1. What Was Done (specific files changed, commands run)
>   2. What Is Verified Working (paste exact test output + AT results)
>   3. What Is Broken / Uncertain (any items marked [fail] or [skip])
>   4. Next Action List
>   5. Blockers
>
> And update .context/progress-tracker.md:
>   Feature F-XXX status → COMPLETE (if all items pass)
>   Feature F-XXX status → BUGS-OPEN (if any [fail] items)"

---

## Phase 5 Checklist (Per Feature)

```
Before Writing Code:
[ ] F-XXX spec confirmed complete
[ ] Gherkin .feature file confirmed written
[ ] Dependencies confirmed complete
[ ] Test file written (backend/tests/integration/test_fXXX_*.py)
[ ] Tests confirmed FAILING (RED) — paste output as evidence

During Implementation:
[ ] Alembic migration created (if new table)
[ ] SQLAlchemy model updated
[ ] Pydantic request/response models written
[ ] Router implemented and wired in main.py
[ ] Frontend hook added to queries.ts
[ ] Frontend route component built

After Implementation:
[ ] All tests PASSING (GREEN)
[ ] No skipped tests without justification

3-Layer Acceptance:
[ ] [DB] All database checks verified with SQL
[ ] [API] All contract checks verified with curl/DevTools
[ ] [UI] Page renders, empty states work, role controls correct
[ ] Zero console errors in browser

Handover:
[ ] progress-tracker.md updated (COMPLETE or BUGS-OPEN)
[ ] HO-XXX.md written with exact verification evidence
[ ] Commit: feat(scope): implement F-XXX feature-name
```
