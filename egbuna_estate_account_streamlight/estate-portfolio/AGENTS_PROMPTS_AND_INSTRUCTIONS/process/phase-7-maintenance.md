# Phase 7 — Maintenance and Evolution

## What This Phase Covers
- Bug triage and fix workflow
- New feature request workflow
- Monthly system health review
- Keeping .context/ files accurate
- Managing technical debt

---

## Entering This Phase

> "You're in Phase 7 — the project is in production.
> What brings you here today?
>
>   a) A bug appeared — something stopped working
>   b) A new feature is requested
>   c) Monthly review — checking system health
>   d) An agent needs re-onboarding
>   e) The .context/ files are out of date"

---

## Mode A — Bug Triage

> "Describe the bug:
>
> 1. What is the exact symptom?
>    (Not 'it's broken' — what specifically happens or doesn't happen)
>
> 2. When did it start?
>    (After a deploy? After a data change? Always been there?)
>
> 3. What layer is it in?
>    a) [DB] — data is wrong or missing in the database
>    b) [API] — endpoint returns wrong status, shape, or data
>    c) [UI] — page renders wrong, crashes, or shows stale data
>    d) Unknown — need to diagnose
>
> 4. Is there an error message?
>    If yes: paste it exactly."

After collecting this information:

> "Let me help you trace this systematically.
>
> Step 1 — Isolate the layer:
>
>   [DB] check:
>   docker compose exec postgres psql -U [user] -d [db]
>   SELECT [relevant query];
>
>   [API] check:
>   curl -s -b 'epm_token=TOKEN' [staging]/api/v1/[endpoint] | python3 -m json.tool
>
>   [UI] check:
>   Open DevTools → Console (errors?) → Network (request/response?)
>
> What did each layer show?"

Once root cause is identified:

> "Root cause confirmed. Before fixing:
>
> 1. Add to .context/current-issues.md:
>    - Exact symptom
>    - Layer (DB/API/UI)
>    - Root cause
>    - Fix plan (one change only)
>
> 2. Write HO-XXX.md directing the implementing agent to:
>    - Make exactly one change
>    - Run the relevant AT checklist items
>    - Create AT-XXX-N follow-up file with results
>
> 3. After fix: remove from current-issues.md
>    Update progress-tracker.md if feature status changes."

---

## Mode B — New Feature Request

> "New feature request. Before writing any spec:
>
> Phase 0 check — does it fit?
> 1. Does this fit the project vision?
>    (Re-read project-overview.md vision statement)
>    If yes → continue
>    If no → it belongs in a different project or Phase 4+
>
> 2. Is it explicitly in the out-of-scope list?
>    If yes → decline or move to a future phase explicitly
>
> 3. Does it require a new architectural decision?
>    (New data storage? New auth requirement? New infrastructure?)
>    If yes → write ADR first, then spec
>
> If all checks pass → go to Phase 4 spec writing."

---

## Mode C — Monthly Health Review

Ask these questions once a month:

> "Monthly review. Let's check each area:
>
> 1. progress-tracker.md accuracy
>    Does it match the actual codebase? Open it and scan:
>    - Any COMPLETE features that have open bugs?
>    - Any PLANNED features that were secretly started?
>    - Any new features that aren't listed yet?
>
> 2. current-issues.md staleness
>    Any bugs older than 2 sprints (roughly 4 weeks)?
>    If yes — are they P0 (must fix) or P2 (accept and document)?
>
> 3. Test suite health
>    Run all tests:
>    docker compose exec backend pytest backend/tests/ -v --tb=short
>    Any failing tests that weren't failing last month?
>
> 4. Dependencies
>    Check for security updates:
>    pip list --outdated  (inside container)
>    npm outdated  (in frontend directory)
>    Any critical security patches? Update with care.
>
> 5. .context/ file accuracy
>    Read architecture.md — do the invariants still match the code?
>    Read AGENTS.md — are the agent domains still correct?
>    If outdated — update now, before the next sprint.
>
> 6. Handover history patterns
>    ls docs/handovers/ | wc -l  (how many HOs this month?)
>    Are any types of bugs recurring? (Same root cause twice = process gap)
>
> After reviewing each area, what needs action?"

---

## Mode D — Agent Re-onboarding

> "Which agent needs re-onboarding?
>
> This happens when:
>   - Starting a new session after a long gap
>   - Switching to a different model for an existing role
>   - A new agent is taking over a role from another
>
> For re-onboarding, I'll generate a fresh session starter:
>
> 1. Read current progress-tracker.md
> 2. Read current-issues.md (active bugs)
> 3. Read the last 3 HO files in docs/handovers/
> 4. Produce FRESH_SESSION_MASTER_PROMPT.md
>
> The agent pastes this at the start of their session.
> They will know the full project state without needing any
> conversation history.
>
> Want me to generate it now?"

---

## Mode E — Context File Update

> "Which .context/ file needs updating?
>
>   a) architecture.md — new invariant discovered or changed
>   b) progress-tracker.md — feature statuses are stale
>   c) AGENTS.md — agent domains changed or new agent added
>   d) current-issues.md — bugs resolved or new ones found
>   e) project-overview.md — vision or scope changed
>   f) code-standards.md — new convention established
>
> For each selected file:
>   1. Show me the current content
>   2. Ask what needs to change
>   3. Produce the updated version
>   4. Confirm before writing"

---

## Technical Debt Triage

When asked "what should we clean up?":

> "Technical debt assessment. Rate each category 1-5:
> (1 = clean, 5 = urgent problem)
>
> Tests:
>   [ ] All features have tests?
>   [ ] Tests actually test the right things (not tautological)?
>   [ ] No skipped tests without documented reason?
>
> Documentation:
>   [ ] Every ADR decision is still in effect?
>   [ ] progress-tracker.md reflects reality?
>   [ ] No feature has been built without a spec?
>
> Code:
>   [ ] No hardcoded credentials or magic strings?
>   [ ] No datetime.utcnow() (naive timestamp) anywhere?
>   [ ] No float monetary values in API responses?
>   [ ] No get_db() calls (should be get_session())?
>
> Infrastructure:
>   [ ] .env not committed to git?
>   [ ] uploads/ not committed to git?
>   [ ] No production secrets in source code?
>
> For any category rated 3+, generate a cleanup task in progress-tracker.md."

---

## Phase 7 Ongoing Checklist

```
After Every Bug Fix:
[ ] Root cause documented in HO
[ ] AT follow-up run filed (AT-XXX-N)
[ ] current-issues.md entry removed
[ ] progress-tracker.md updated if status changed

After Every New Feature:
[ ] Phase 0 check passed (fits vision, not out-of-scope)
[ ] Phase 2 check passed (no new ADR needed, or ADR written)
[ ] F-XXX spec written before any implementation
[ ] progress-tracker.md updated with new feature entry

Monthly:
[ ] All .context/ files reviewed for accuracy
[ ] All tests running and green
[ ] Dependencies checked for security updates
[ ] Handover history reviewed for recurring patterns
[ ] current-issues.md — no bugs older than 2 sprints unaddressed
```
