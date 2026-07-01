# Phase 6 — Acceptance and Deployment

## What This Phase Produces
- AT-XXX.md in docs/testing/acceptance/ (immutable UAT record)
- Confirmed deployment to staging URL
- Updated progress-tracker.md (COMPLETE or BUGS-OPEN)
- HO-XXX.md with AT results directed to next agent

---

## Step 1 — UAT Readiness Check

> "Before running acceptance tests, confirm:
>
> 1. Is the feature deployed to staging?
>    URL: [staging URL]
>    How to verify: curl [staging URL]/api/v1/[endpoint] → 200
>
> 2. Is there test data in the staging database?
>    Some features need seed data to test (e.g. companies for price entry)
>    If not: run the relevant seed script first
>
> 3. Do you have admin credentials for staging?
>    If not: run seed_admin.py or equivalent"

---

## Step 2 — AT Document Setup

> "Create the acceptance test file:
> Path: docs/testing/acceptance/AT-XXX-[feature]-[YYYY-MM-DD].md
>
> AT numbering rules:
>   First run of feature 1:  AT-001
>   Follow-up after fixes:   AT-001-1, AT-001-2
>   First run of feature 2:  AT-002
>   NEVER modify an existing AT file — always create a follow-up
>
> Header block for the AT file:"

```markdown
---
type: AT
id: AT-XXX
title: [Feature Name] — Acceptance Test
status: IN-PROGRESS
date: YYYY-MM-DD
tester: [your name]
environment: [staging URL]
feature: F-XXX
fixes-from: HO-XXX (if this is a follow-up)
---
```

---

## Step 3 — Running the 3-Layer Tests

Guide the user through each layer interactively.

### [DB] Layer

> "Database checks first — these are fastest and most direct.
>
> Connect to your database:
>   docker compose -f docker-compose.v2.yml exec postgres \
>     psql -U [user] -d [database]
>
> For each [DB] item in the F-XXX checklist:
>   Run the SQL, paste the result, mark [x] or [fail].
>
> Common queries to always run:
>   -- Confirm soft delete works (deleted_at set, not hard deleted)
>   SELECT id, deleted_at FROM [table] WHERE id = [test_id];
>
>   -- Confirm monetary values stored as Decimal (not float)
>   SELECT pg_typeof([monetary_column]) FROM [table] LIMIT 1;
>
>   -- Confirm timestamps are timezone-aware
>   SELECT [timestamp_column], pg_typeof([timestamp_column])
>   FROM [table] LIMIT 1;"

### [API] Layer

> "API contract checks second.
>
> Get your auth token first:
>   TOKEN=$(curl -s -X POST [staging]/api/v1/auth/login \
>     -H 'Content-Type: application/json' \
>     -d '{\"username\":\"admin\",\"password\":\"[pass]\"}' \
>     -c /tmp/cookies.txt && cat /tmp/cookies.txt | grep epm_token | awk '{print $7}')
>
> Or use DevTools Application tab → Cookies → copy epm_token value.
>
> For each [API] item in the F-XXX checklist, run the curl command
> and paste the output. Key checks:
>
>   -- Monetary type check (must return 'str' not 'float')
>   curl -s -b 'epm_token=TOKEN' [staging]/api/v1/[endpoint] | \
>     python3 -c \"import sys,json; d=json.load(sys.stdin);
>     v=d['data'][0]['[monetary_field]'];
>     print(f'type: {type(v).__name__}, value: {v}')\"
>
>   -- Auth check (must return 401)
>   curl -s -o /dev/null -w '%{http_code}' [staging]/api/v1/[endpoint]
>
>   -- Role check (must return 403 for write operations)
>   curl -s -o /dev/null -w '%{http_code}' -X POST \
>     -b 'epm_token=READONLY_TOKEN' [staging]/api/v1/[endpoint]"

### [UI] Layer

> "Browser checks last — open [staging URL] in Chrome/Firefox.
>
> DevTools setup (do this before testing):
>   F12 → Console tab → confirm zero errors on page load
>   F12 → Network tab → filter by XHR/Fetch to see API calls
>
> For each [UI] item in the F-XXX checklist:
>   1. Perform the action described
>   2. Check Console for errors
>   3. Check Network for correct request/response shape
>   4. Confirm visual rendering matches the spec
>   5. Mark [x], [fail], or [skip] with reason
>
> Always test these regardless of spec:
>   - Empty state: does it show a message or a blank/broken page?
>   - Loading state: is there a spinner while data loads?
>   - Error state: what does the user see if the API fails?"

---

## Step 4 — Recording Results

After all three layers:

> "Fill in the AT summary table:
>
> | Section | Total | Pass | Fail | Skip | Pending |
> |---------|-------|------|------|------|---------|
> | [DB]    |   N   |  N   |  N   |  N   |    N    |
> | [API]   |   N   |  N   |  N   |  N   |    N    |
> | [UI]    |   N   |  N   |  N   |  N   |    N    |
>
> Overall result:
>   PASS    — all items [x], feature complete
>   PARTIAL — some [fail] or [skip], feature needs fixes
>   FAIL    — critical P0 failures, feature not shippable"

---

## Step 5 — If PASS

> "All items passing — feature complete.
>
> Actions:
> 1. Update progress-tracker.md: F-XXX status → COMPLETE
> 2. Update AT file: status: COMPLETE
> 3. Write HO-XXX.md with AT results
>    'All AT-XXX items passing. F-XXX complete. Ready for next feature.'
>
> Ready to move to Phase 4 for the next feature?
> Next in queue: [next feature from progress-tracker.md]"

---

## Step 6 — If FAIL or PARTIAL

> "Some items failed. Let's triage them:
>
> P0 (blocking — must fix before proceeding):
>   - Core functionality broken
>   - Data corruption risk
>   - Auth/role enforcement missing
>
> P1 (fix soon — affects usability but not data integrity):
>   - UI rendering issues
>   - Empty state missing
>   - Error messages unhelpful
>
> P2 (fix eventually — polish):
>   - Tooltip missing
>   - Animation not smooth
>   - Minor layout issue
>
> For each failed item, categorise it. Then:
> 1. Add P0 + P1 bugs to .context/current-issues.md
> 2. Update progress-tracker.md: F-XXX status → BUGS-OPEN
> 3. Write HO-XXX.md directing agent to fix bugs
> 4. Create AT-XXX-1.md for the follow-up run
>
> Do NOT start the next feature until all P0 bugs are resolved."

---

## Step 7 — Deployment Confirmation

After PASS:

> "Confirm the feature is live on staging:
>
> 1. Container running:
>    docker compose -f docker-compose.v2.yml ps
>    → epm_v2 should show 'Up'
>
> 2. Health check:
>    curl -s [staging URL]/api/v1/health || \
>    curl -s -o /dev/null -w '%{http_code}' [staging URL]
>    → expect 200
>
> 3. Log check (no startup errors):
>    docker compose -f docker-compose.v2.yml logs epm_v2 --tail=20
>    → no ERROR lines
>
> Feature F-XXX is live at [staging URL]."

---

## Production Cutover Checklist (Run Once at End of Project)

Only when ALL features are AT-verified on staging:

```
Pre-cutover:
[ ] All features COMPLETE in progress-tracker.md
[ ] Zero P0 bugs in current-issues.md
[ ] All AT files filed in docs/testing/acceptance/
[ ] No mock/seed data in production code paths

Infrastructure:
[ ] All env vars set in production environment (.env.prod)
[ ] Database migrations run on production DB
[ ] File upload volume mounted correctly in production
[ ] Traefik labels updated for production domain
[ ] SSL certificate provisioned and valid

Cutover:
[ ] Old version still running until new version confirmed healthy
[ ] New version deployed to production URL
[ ] Production URL accessible and returning correct responses
[ ] Smoke test: login, dashboard loads, data visible
[ ] Old container stopped AFTER new version confirmed

Post-cutover:
[ ] DNS propagation confirmed
[ ] .context/architecture.md updated with production URLs
[ ] progress-tracker.md updated: F-021 Production Cutover → COMPLETE
[ ] AGENTS.md updated with production URL
```
