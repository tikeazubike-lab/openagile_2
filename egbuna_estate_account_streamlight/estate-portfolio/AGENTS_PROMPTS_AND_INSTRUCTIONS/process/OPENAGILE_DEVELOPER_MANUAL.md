# The OpenAgile Developer Manual
## From Idea to Production — Solo Developer with AI Agents

**Version**: 1.0
**Author**: Claude (The Brain) — OpenAgile Architecture Series
**Audience**: Solo developers comfortable with coding and git,
              new to formal SDLC, BDD, and multi-agent AI workflows
**Worked example**: Estate Portfolio Manager (EPM) — FastAPI + React 18

---

## How to Use This Manual

This manual has two layers:

**Reference sections** — explain what each phase is, why it exists,
and what goes wrong when you skip it. Read these once to understand
the system. Come back when you need to understand a decision.

**Execution checklists** — at the end of every phase. When starting
a new project or a new feature, open the checklist for that phase
and work through it line by line. Do not proceed to the next phase
until every item is checked.

The manual is organised into **7 phases**:

```
Phase 0 — Idea Capture
Phase 1 — Project Foundation
Phase 2 — Architecture Decision
Phase 3 — Agent Setup
Phase 4 — Spec Writing
Phase 5 — Test-Driven Implementation
Phase 6 — Acceptance and Deployment
Phase 7 — Maintenance and Evolution
```

Every software project you build goes through all 7 phases.
Features within a project cycle through Phases 4–6 repeatedly.

---

# PHASE 0 — IDEA CAPTURE

## What This Phase Is

Before any code, any spec, any architecture decision — you need to
answer three questions clearly enough to explain the project to someone
who has never heard of it:

1. **What problem does this solve?**
2. **Who has this problem?**
3. **What does success look like on day one?**

If you cannot answer these three questions in plain language, the
project is not ready to be built. Writing code before answering
them is the fastest way to build the wrong thing.

## Why It Matters

EPM example: The original problem was "I have 85 NGX stocks scattered
across Obsidian, Excel, and my memory and I cannot answer what my
portfolio is worth today." That single sentence drove every architecture
decision that followed — the dual Holdings table, the NGX PDF parser,
the registrar document system. Without it, you would have built a generic
portfolio app that did not handle delisted stocks, AMCON claims, or
registrar requirements.

## The Four Documents This Phase Produces

### 1. Problem Statement (one paragraph)
What is broken today? Who is suffering? What do they use instead?
Why is the existing solution insufficient?

### 2. Vision Statement (one sentence)
What is the system when it is complete? Not what it does — what it IS.

EPM example:
> "A complete self-hosted personal Nigerian investment management system
> that tells me what I own, what it is worth, and what I need to do about it."

### 3. User List
Who uses the system? What are their roles? What can each role do?
What can they NOT do?

EPM example:
- Admin (owner): full read + write + administration
- Viewer (family/broker): read-only, limited pages
- Future: multi-portfolio per user (Phase 4)

### 4. Out of Scope List
Explicitly name what this system will NEVER do. This is as important
as what it will do. Every item on this list is a decision you have
made so you do not have to make it again when the idea surfaces later.

EPM example: No real-time market feeds. No automated broker integration.
No tax filing automation. No mobile native app.

## What to Use

A plain markdown file. No tools required. No templates required.
Write it yourself first. Then use Claude to challenge it:

> "Here is my problem statement, vision, users, and out-of-scope list.
> What am I missing? What assumptions am I making that I have not
> stated? What will become a problem in six months?"

---

## Phase 0 Checklist

```
[ ] Written: one-paragraph problem statement
[ ] Written: one-sentence vision statement
[ ] Written: user list with roles and capabilities
[ ] Written: explicit out-of-scope list (minimum 5 items)
[ ] Reviewed: Claude has challenged the assumptions
[ ] Decision: project is worth building (or not — and why)
```

---

# PHASE 1 — PROJECT FOUNDATION

## What This Phase Is

You have decided to build. Now you set up the environment that
everything else depends on. Get this right and every future phase
runs smoothly. Get this wrong and you spend weeks fighting your
own tools instead of building features.

This phase has four components: repository structure, context files,
agent configuration, and infrastructure baseline.

## Repository Structure

Every project gets the same skeleton:

```
project-root/
├── .context/                    ← Agent memory (read every session)
│   ├── AGENTS.md                ← Entry point — first file agents read
│   ├── project-overview.md      ← What the project is
│   ├── architecture.md          ← Stack, invariants, API contracts
│   ├── code-standards.md        ← Language conventions
│   ├── ai-workflow-rules.md     ← How agents behave (universal)
│   ├── ui-context.md            ← Design tokens, layout rules (if UI)
│   ├── progress-tracker.md      ← Live feature status
│   ├── current-issues.md        ← Active bugs (GITIGNORED)
│   └── feature-specs/           ← F-XXX.md files (one per feature)
│
├── docs/
│   ├── decisions/               ← ADR-XXX.md (why choices were made)
│   ├── requirements/            ← BR-XXX.md (business requirements)
│   ├── testing/
│   │   ├── features/            ← Gherkin .feature files
│   │   └── acceptance/          ← AT-XXX.md (UAT results)
│   └── handovers/               ← HO-XXX.md (agent handover briefs)
│
├── [source code directories]
│
└── .gitignore                   ← Must include: .context/current-issues.md
```

## The .context/ Files

These seven files are the agent's memory. Every agent reads them at
the start of every session. They replace the need to re-explain the
project each time.

**AGENTS.md** — The entry point. Tells agents what to read, in what
order, and what the hard rules are. The first sentence every agent
reads. Keep it short and non-negotiable.

**project-overview.md** — What the project is, who it is for, what
success looks like, and what is explicitly out of scope. Derived from
your Phase 0 documents.

**architecture.md** — Stack choices, infrastructure constraints, API
contracts, and invariants. An invariant is a rule the system must
never violate. List them explicitly. Examples from EPM:
- `bcrypt==4.0.1` — never upgrade (passlib incompatibility)
- `get_session()` not `get_db()` — function name in codebase
- Monetary values as strings in API responses — never floats

**code-standards.md** — Python conventions, TypeScript conventions,
file naming, commit message format. Prevents agents from inventing
their own style.

**ai-workflow-rules.md** — How agents behave. The debug protocol.
The handover format. The zone system. This file is UNIVERSAL — copy
it unchanged between projects. It does not contain project-specific
information.

**ui-context.md** — Design tokens, colour variables, typography rules,
component patterns, empty state patterns. Only relevant for projects
with a UI. Prevents agents from hardcoding hex values and inventing
their own component patterns.

**progress-tracker.md** — The live status of every feature. Updated
at the end of every agent session. This file is what prevents the
"going back and forth without knowing what has been done" problem.

## Agent Configuration

Configure your AI tools before starting implementation:

**Hermes** — Set the personality to match the project. Write one
personality per role (builder, debugger, architect, tester). Set the
`cwd` to the project root. Set `show_cost: true` to track model costs.

**Cursor** — Write `.cursor/rules/*.mdc` files matching the four
domains: general (always active), backend, frontend, infrastructure.
These rules load automatically when editing files in those directories.

**Model routing** — Decide which model handles which type of work:
- Heavy reasoning (architecture, debugging): most capable model
- Fast coding (small edits, boilerplate): fast cheap model
- Context compression: fast cheap model

## Infrastructure Baseline

Set up the minimum running environment before writing any feature code.
For a web project this means:
- Docker Compose with your services defined
- Database running and reachable
- A "hello world" endpoint returning 200
- The frontend rendering one page
- A deploy script or CI/CD pipeline

EPM example: Phase 2A established auth, the database, the single
Docker container, and Traefik routing. Everything else was built
on top of that baseline.

Why infrastructure first: if your deploy pipeline is broken, every
feature you build has untested deployment assumptions. Fix the
pipeline once, at the start, and every subsequent feature ships cleanly.

---

## Phase 1 Checklist

```
Repository:
[ ] .context/ folder created with all 7 files populated
[ ] docs/ folder structure created
[ ] .gitignore includes .context/current-issues.md, .env, uploads/
[ ] README.md has quickstart instructions

Agent Setup:
[ ] Hermes personality written for this project (builder, debugger)
[ ] Cursor .cursor/rules/*.mdc files written (general, backend, frontend, infra)
[ ] Default working directory set to project root
[ ] Model routing decided (which model for which task type)

Infrastructure:
[ ] Version control initialised (git init + remote)
[ ] Docker Compose (or equivalent) defined
[ ] Database schema baseline (empty, but reachable)
[ ] "Hello world" endpoint returns 200
[ ] Deploy mechanism works (CI/CD or manual script)
[ ] Staging environment accessible at a URL

Context Files:
[ ] AGENTS.md written with hard rules
[ ] project-overview.md contains: problem, vision, users, out-of-scope
[ ] architecture.md contains: stack, invariants, API contract rules
[ ] code-standards.md contains: language conventions, commit format
[ ] ui-context.md written (if UI project)
[ ] progress-tracker.md contains feature list with all statuses = PLANNED
[ ] ai-workflow-rules.md copied from previous project or written fresh
```

---

# PHASE 2 — ARCHITECTURE DECISION

## What This Phase Is

Every project has a small set of decisions that are very hard to
reverse once you have written significant code. These are architectural
decisions. This phase is about identifying and making those decisions
explicitly — before implementation — and recording them so they are
never re-litigated.

## What an Architectural Decision Is

An architectural decision is a choice between two or more options where:
- The choice affects multiple parts of the system
- Reversing it later requires significant rework
- There are meaningful trade-offs between the options

Examples from EPM:
- JWT in httpOnly cookie vs localStorage (security vs simplicity)
- Single Docker container vs separate frontend/backend containers (simplicity vs independent scaling)
- Shared Postgres vs separate database per service (resource efficiency vs isolation)
- Soft delete vs hard delete (audit trail vs storage)
- Monetary values as strings vs floats (precision vs convenience)

## The ADR Format

Every architectural decision gets an ADR (Architecture Decision Record)
filed in `docs/decisions/`. The format is:

```markdown
# ADR-001 — [Decision Title]

## Status: ACCEPTED

## Context
What situation forced this decision?

## Decision
What was decided? (one sentence)

## Rationale
Why this option over the alternatives?

## Alternatives Considered
| Option | Rejected Because |
|--------|-----------------|
| Option A | reason |

## Consequences
Positive: what gets better
Negative: what gets harder
Risk: what could go wrong
```

## The Tree of Thoughts Technique

For any decision where you are genuinely uncertain, use this technique
before deciding:

1. List all plausible options (usually 2–4)
2. For each option, trace forward 3–6 months: what does the system
   look like? What becomes harder? What becomes easier?
3. Identify which option produces the least regret at month 6
4. Decide

This is what prevents the most common architectural mistake: choosing
the option that is easiest to implement today, at the expense of
something you will need in three months.

EPM example: The decision to store monetary values as strings in API
responses was made using this technique. Float is easier to implement
today. But at month 3, when Recharts needs to render ₦12,345,678.50
and JavaScript floating-point arithmetic has introduced a rounding
error, the string approach saves a debugging session.

## Decisions to Make Before Writing Code

For any web project, these decisions must be made before writing
production code:

**Authentication**: Who can access what? How are sessions managed?
How long do they last? What is the password storage strategy?

**Data model**: How is data deleted (soft vs hard)? How are monetary
values stored and serialised? How is multi-tenancy handled (if at all)?
What is the ID strategy (sequential, UUID)?

**API contract**: What is the response envelope shape? What HTTP
status codes mean what? How are errors structured?

**Infrastructure**: Single container or multiple? Shared database or
per-service? What is the deployment mechanism? Where do uploaded files
live?

**Role model**: What roles exist? What can each role do? How is
authorisation enforced (at route level, query level, both)?

---

## Phase 2 Checklist

```
[ ] Auth strategy decided and recorded in ADR
[ ] Data deletion strategy decided (soft delete recommended)
[ ] Monetary value serialisation decided (strings recommended)
[ ] API response envelope shape defined
[ ] HTTP status code conventions defined
[ ] Infrastructure topology decided (containers, services, database)
[ ] Role model defined (roles, permissions, enforcement point)
[ ] File storage strategy decided (local volume, cloud, CDN)
[ ] Deployment mechanism defined
[ ] At least 5 ADRs written for major decisions
[ ] architecture.md updated with all invariants from ADR decisions
[ ] All decisions recorded — none left as "we'll figure it out later"
```

---

# PHASE 3 — AGENT SETUP

## What This Phase Is

You have a foundation and architectural decisions. Now you configure
the agents that will do the implementation work. This phase prevents
the most common multi-agent failure: agents that contradict each other,
overwrite each other's work, or drift from the architectural decisions
you just made.

## The Agent Registry

Write an explicit registry of who does what. Every agent must have:
- A clear domain (files they own)
- A clear anti-domain (files they never touch)
- A clear communication protocol (how they report back)

EPM agent registry:
```
Claude (Architect):
  Owns: .context/ files, docs/, feature specs, handover briefs
  Never touches: source code files
  Reports: through handover briefs (HO-XXX.md)

Antigravity (Backend Builder):
  Owns: backend/**, docker-compose.yml, deploy scripts
  Never touches: frontend src/ files
  Reports: through HO-XXX.md to Claude

Deepseek v4 (Frontend Builder):
  Owns: src/routes/**, src/components/**, src/api/**
  Never touches: backend/ files
  Reports: through HO-XXX.md to Claude

Push sequence: Antigravity pushes backend first.
Deepseek v4 pulls then does frontend. Never simultaneously.
```

## The Conflict Prevention Rules

The most common multi-agent failure is two agents editing the same
file in overlapping sessions. Prevent it with two rules:

**Rule 1 — File domain separation**: Each agent owns specific
directories. No agent touches another agent's files without explicit
instruction.

**Rule 2 — Push sequence**: When a feature requires both backend
and frontend changes, backend goes first and is deployed, then
frontend starts. Never both sides simultaneously.

## Writing the AGENTS.md Entry Point

The AGENTS.md file is the most important file in the project. It is
the first thing every agent reads in every session. It must contain:

1. What the project is (one sentence)
2. Which context files to read and in what order
3. File domain assignments
4. The one rule that cannot be broken (tests RED before code)
5. Hard rules (language-specific, project-specific invariants)
6. What to do after completing work (update tracker, write handover)

Keep it under 100 lines. If it is longer, agents will not read all of it.

## The Handover Protocol

Every agent session ends with a handover brief. This is the
communication mechanism between agents. Without it, context is lost
between sessions and agents repeat work or break each other's changes.

The handover brief format (5 sections — always exactly these):

```markdown
---
type: HO
id: HO-XXX
title: [From Agent] → [To Agent]: [Topic]
date: YYYY-MM-DD
from: [Agent]
to: [Agent]
---

## 1. What Was Done
[Specific files changed, commands run, tests executed]

## 2. What Is Verified Working
[Exact output or test result — not "it works", but what was run and what was seen]

## 3. What Is Broken / Uncertain
[Root cause if known]

## 4. Next Agent Action List
1. [numbered step]
2. [numbered step]

## 5. Blockers
[What cannot proceed until resolved]
```

The sequential numbering (HO-001, HO-002...) creates a chronological
audit trail. EPM reached HO-018 in its first major implementation cycle.
That is 18 handovers — 18 explicit state transitions between agents.
Every one is in `docs/handovers/`. Nothing was lost between sessions.

---

## Phase 3 Checklist

```
Agent Registry:
[ ] Every agent has a defined file domain
[ ] Every agent has a defined anti-domain
[ ] Push sequence defined for features requiring multiple agents
[ ] Conflict rule documented in AGENTS.md

Communication:
[ ] HO-XXX handover format documented in ai-workflow-rules.md
[ ] Every agent knows to write a handover after every session
[ ] Handover numbering convention established (HO-001, HO-002...)

Configuration:
[ ] Hermes config.yaml has project personalities written
[ ] Cursor .mdc rules files reference project-specific conventions
[ ] ai-workflow-rules.md finalised (universal across projects)

Test Environment:
[ ] Agents can run tests (via SSH to server, or CI/CD)
[ ] Test output is accessible (logs, terminal, CI UI)
[ ] Test database or schema isolated from production
```

---

# PHASE 4 — SPEC WRITING

## What This Phase Is

This is where the rubber meets the road. For every feature you are
about to build, you write a specification before writing a single
line of production code. The spec is the contract between the
Architect (you + Claude) and the builders (your implementing agents).

This phase has two outputs per feature:
1. A feature spec file (F-XXX.md)
2. A Gherkin .feature file

## The Feature Spec

The feature spec answers: what does this feature do, what files does it
touch, what does the API look like, what does the UI look like, and
how do we know it is done?

```markdown
---
id: F-XXX
title: Feature Name
status: PLANNED
owner-backend: [Agent]
owner-frontend: [Agent]
---

# F-XXX — Feature Name

## Goal
One sentence: what does this produce when complete?

## What Is Built
Backend:
  Router: backend/app/routers/feature.py
  Endpoints: GET /api/v1/feature | POST /api/v1/feature
  Model: FeatureName in models.py
  Migration: yes/no

Frontend:
  Route: src/routes/_app.feature.tsx
  Components: [list]
  Hooks: useFeature() in src/api/queries.ts

## API Response Shape
[Exact JSON structure — not approximate]

## Layout
[Exact description of what the user sees]

## Acceptance Checklist
[DB] — PostgreSQL verification
[API] — curl or DevTools verification
[UI] — browser verification

## Sign-Off
[ ] All checklist items passing
[ ] progress-tracker.md updated
[ ] HO filed in docs/handovers/
```

## The Gherkin .feature File

The Gherkin file translates the feature spec into executable test
scenarios. It is the bridge between the spec and the test code.

Why Gherkin? Because it forces you to think through the feature in
terms of observable behaviour — not implementation. "Given a holding
with 100 shares and a price of ₦450, when I request the holdings API,
then current_value should be ₦45,000" is a test. "The holdings
endpoint should compute values" is not.

The Gherkin format:
```gherkin
Feature: [Feature name]
  As a [user type]
  I want [action]
  So that [outcome]

  Background:
    Given [common setup for all scenarios]

  Scenario: SC-XXX [scenario name]
    Given [initial state]
    When  [action taken]
    Then  [observable outcome]
    And   [additional outcome]
```

## How Many Scenarios to Write

For every feature, write scenarios covering:

1. **Happy path** — the normal successful case
2. **Validation errors** — what happens with bad input
3. **Auth/role checks** — what happens when unauthorised
4. **Empty states** — what happens when there is no data
5. **Data persistence** — verify the DB actually changed

EPM example for price entry:
- SC-007: Valid price update stores in DB and audit log (happy path)
- SC-008: Future date rejected with 422 (validation)
- SC-009: Negative price rejected (validation)
- SC-010: Price above sanity cap rejected (validation)
- SC-014: Readonly user gets 403 (auth)

## Common Mistakes in Spec Writing

**Too vague**: "The dashboard should show portfolio data." This is not
a spec. A spec says: "The GET /api/v1/dashboard endpoint returns a JSON
object where `sector_allocation` is an array of objects each containing
`name` (string), `value` (string, monetary), and `pct` (string, percentage)."

**Missing the API contract**: Specs that describe UI but not the API
shape leave agents to invent the API. They will invent different shapes
in different sessions. Specify the exact JSON.

**No empty states**: Almost every bug in EPM's AT-003 was a crash when
data was null or undefined. Spec the empty state explicitly.

**No role checks**: If you do not spec what readonly users see, agents
will implement for admin only and the feature will be wrong.

---

## Phase 4 Checklist (Per Feature)

```
Feature Spec (F-XXX.md):
[ ] Goal is one clear sentence
[ ] All backend files and endpoints listed with exact paths
[ ] All frontend files listed with exact paths
[ ] API response shape is exact JSON (not approximate)
[ ] UI layout is precise enough that two agents would produce the same UI
[ ] Acceptance checklist has [DB] [API] [UI] labelled items
[ ] Dependencies on other features are explicit
[ ] Acceptance checklist includes: happy path, validation, auth, empty state

Gherkin (.feature file):
[ ] Feature description states: As a / I want / So that
[ ] Background covers common setup
[ ] At least one happy path scenario
[ ] At least one validation error scenario
[ ] At least one auth/role scenario
[ ] At least one empty state scenario
[ ] Scenario IDs are sequential (SC-001, SC-002...)
[ ] Scenarios reference the feature spec ID (F-XXX)

Before Moving to Phase 5:
[ ] Feature spec reviewed — would two agents produce the same output?
[ ] API shape is complete — no "TBD" fields
[ ] Gherkin reviewed — are the "Then" clauses observable and testable?
[ ] progress-tracker.md updated: feature status = PLANNED with spec link
```

---

# PHASE 5 — TEST-DRIVEN IMPLEMENTATION

## What This Phase Is

This is Uncle Bob's Red-Green-Refactor cycle, adapted for multi-agent
AI development. The rule is absolute: no agent writes production code
for a feature until tests for that feature exist and are confirmed
failing (RED).

## Why the RED Phase Matters

Writing tests after code is natural selection for tests that pass.
You write the code, then you write tests that confirm the code you just
wrote. Those tests will always pass — because you wrote them to match
what you already built. They do not prove the feature works; they prove
the code exists.

Writing tests before code proves two things:
1. The test actually tests something (it fails when the feature is absent)
2. The implementation actually satisfies the requirement (not just happens to pass)

In EPM: every time an agent implemented without tests first, bugs emerged
in acceptance testing that required a separate fix sprint. Every time the
RED phase was respected, features shipped correctly on the first AT run.

## Translating Gherkin to pytest

EPM uses standard pytest with httpx — not pytest-bdd. The Gherkin
file is a design artifact (spec document). The pytest file is the
executable test. The link between them is a traceability comment.

```python
# backend/tests/integration/test_price_entry.py

class TestPriceEntry:

    @pytest.mark.asyncio
    async def test_sc007_quick_price_entry_updates_price_and_audit(
        self, admin_http_client, test_company, db_session
    ):
        """
        Spec: price_entry.feature | SC-007
        Given ZENITHBANK has current_price 31.00
        When POST /api/v1/prices/quick with price 32.50
        Then current_price updated AND price_audit record created
        """
        # --- GIVEN ---
        test_company.current_price = Decimal("31.00")
        await db_session.flush()

        # --- WHEN ---
        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id,
                  "price": "32.50",
                  "entry_date": str(date.today())}
        )

        # --- THEN ---
        # Spec: SC-007 | Then response status 200
        assert response.status_code == 200

        # Spec: SC-007 | And price updated in DB
        await db_session.refresh(test_company)
        assert test_company.current_price == Decimal("32.50")

        # Spec: SC-007 | And audit record created with source 'manual'
        result = await db_session.execute(
            select(PriceAudit).where(PriceAudit.company_id == test_company.id)
        )
        audit = result.scalar_one_or_none()
        assert audit is not None
        assert audit.old_price == Decimal("31.00")
        assert audit.source == "manual"
```

## The Implementation Session Protocol

Every agent implementation session follows this exact sequence:

```
1. Read .context/AGENTS.md and relevant context files
2. Read .context/feature-specs/F-XXX.md
3. Write pytest tests from the Gherkin scenarios
4. Run tests → confirm FAILING (RED)
   If tests pass without any implementation: the tests are wrong
5. Write minimum production code to satisfy the tests
6. Run tests → confirm PASSING (GREEN)
7. Refactor if needed → tests stay green
8. Run acceptance checklist from F-XXX.md (3-layer: DB/API/UI)
9. Update .context/progress-tracker.md
10. Write HO-XXX.md handover brief
```

## The Three-Layer Acceptance Test

Every feature's acceptance checklist has three layers, each tested
independently:

**[DB] Database layer** — verify data was actually stored correctly
```sql
-- After adding a holding:
SELECT id, company_id, num_shares, avg_purchase_price, status, deleted_at
FROM holdings WHERE id = [new_id];
-- Confirm: num_shares correct, deleted_at is NULL, status = 'draft'
```

**[API] API layer** — verify the contract is correct
```bash
curl -s -b "epm_token=TOKEN" \
  https://testdrive.epm.zubbystudio.shop/api/v1/holdings \
  | python3 -c "import sys,json; d=json.load(sys.stdin);
    print(type(d['data'][0]['current_value']))"
# Expected: <class 'str'>  (confirms monetary string contract)
```

**[UI] UI layer** — verify rendering is correct
- Open browser DevTools Console — zero errors
- Open Network tab — confirm request payload and response shape
- Visual confirmation — data renders, empty states present,
  role-based controls shown/hidden correctly

Why three layers? Because a bug can exist at any layer independently:
- DB correct, API wrong: serialisation bug (float instead of string)
- API correct, UI wrong: Recharts expects numbers, API sends strings
- UI correct, DB wrong: soft delete not setting deleted_at

Testing all three layers catches all three categories.

## Common Implementation Mistakes

**Skipping RED**: Agent writes tests after implementation. Tests always
pass. Bugs emerge in UAT. Fix sprint required.
Prevention: Run tests before writing any production code. If they pass
immediately, the tests are testing the wrong thing.

**Trial-and-error debugging**: Agent changes multiple things at once
to fix a bug. One of them works. Agent does not know which. Bug returns
in a different form later.
Prevention: The debug protocol — capture exact error, trace to exact
line, propose one fix, implement one change, verify.

**Monetary float leak**: Agent returns `current_value: 45000.0` instead
of `current_value: "45000.00"`. Works in Python. Breaks in JavaScript
at ₦12,345,678.90 due to float precision.
Prevention: explicit check in acceptance test — `assert isinstance(response_data['current_value'], str)`

---

## Phase 5 Checklist (Per Feature)

```
Before Writing Code:
[ ] Tests written for all Gherkin scenarios
[ ] Tests run → confirmed FAILING (RED)
[ ] If tests pass without implementation: stop, fix the tests first

During Implementation:
[ ] One feature unit at a time — not mixed concerns in one session
[ ] Backend pushed first if both backend and frontend are needed
[ ] Frontend agent pulls latest before starting

After Implementation:
[ ] Tests run → all PASSING (GREEN)
[ ] No skipped tests (unless explicitly justified in code comment)
[ ] Refactoring done with tests still green

Acceptance (3-Layer):
[ ] [DB] Database state verified with SQL query
[ ] [API] API contract verified with curl or DevTools Network
[ ] [UI] Page renders correctly, empty states work, role controls correct
[ ] Zero console errors in browser DevTools

Handover:
[ ] progress-tracker.md updated: feature status = COMPLETE
[ ] HO-XXX.md written with exact verification evidence
[ ] Commit made with conventional format: feat(scope): implement F-XXX
```

---

# PHASE 6 — ACCEPTANCE AND DEPLOYMENT

## What This Phase Is

The feature passes its own tests. Now the product owner (you) verifies
that what was built is actually what was wanted. This is the UAT
(User Acceptance Testing) phase. Then the feature is deployed.

## Writing the Acceptance Test Document

Every feature gets an AT-XXX.md file filed in
`docs/testing/acceptance/`. This file is an immutable historical record.

**NEVER modify an existing AT file.** When you find bugs and fix them,
create a follow-up: AT-001 → AT-001-1 → AT-001-2.

The format uses the three-layer labels:

```markdown
---
type: AT
id: AT-XXX
title: [Feature Name] — Acceptance Test
date: YYYY-MM-DD
tester: [your name]
environment: [URL]
branch: [branch name]
feature: F-XXX
---

## [DB] Database Checks
- [ ] [DB] After creating a holding, row exists in holdings table
      with correct company_id, num_shares, status = 'draft'
- [x] [DB] Soft delete sets deleted_at timestamp, not hard delete

## [API] API Contract Checks
- [ ] [API] GET /api/v1/holdings returns current_value as string
- [fail] [API] POST /holdings returns 500 — see Issue #1

## [UI] UI Checks
- [ ] [UI] Holdings table renders without crash
- [skip] [UI] Readonly user check — no readonly user created yet

## Issues Found
| # | Description | Severity | Fix Required |
|---|-------------|----------|-------------|
| 1 | POST 500 error | P0 | Yes — BUG-003 |

## Result: PARTIAL
```

## The AT Naming Convention

```
AT-001           — first run of feature 1
AT-001-1         — follow-up after fixing bugs from AT-001
AT-001-2         — second follow-up if more bugs found
AT-002           — first run of feature 2
```

Never use AT-001-v2 or AT-001-fixed. The dash-number suffix is the
only convention. It preserves chronological order in the filesystem.

## Deployment

For self-hosted projects without CI/CD (like EPM on openagile_2):

```bash
# Backend change
cd /home/zubbyik/openagile_2/.../estate-portfolio
docker compose -f docker-compose.v2.yml up -d --build epm_v2

# Frontend change
cd estate-portfolio-manager
npm run build
cp -r dist/* ../backend/app/static/
docker compose -f docker-compose.v2.yml restart epm_v2

# Verify
docker compose -f docker-compose.v2.yml logs epm_v2 --tail=20
curl -s https://testdrive.epm.zubbystudio.shop/api/v1/health
```

For projects with CI/CD:
```
git push origin feature/xxx → CI runs → staging deploy automatic
Manual approval → production deploy
```

## The Production Cutover Checklist

When all features are complete and AT-verified on staging, you cut over
to production. This checklist prevents the "it works on staging" problem:

```
[ ] All features pass AT on staging URL
[ ] No open P0 bugs
[ ] No mock data anywhere in the codebase
[ ] Auth verified: cookie lifetime, session restore, logout
[ ] All env vars set in production environment
[ ] Database migrations run on production database
[ ] File upload volume mounted correctly in production
[ ] Traefik labels updated for production domain
[ ] Old version still running until new version confirmed healthy
[ ] DNS cutover done
[ ] Old container stopped after new version confirmed
[ ] MASTER_CONTEXT/architecture.md updated with production URLs
```

---

## Phase 6 Checklist (Per Feature)

```
Acceptance Testing:
[ ] AT-XXX.md file created for this feature
[ ] All [DB] items checked
[ ] All [API] items checked
[ ] All [UI] items checked
[ ] Result recorded: PASS / FAIL / PARTIAL
[ ] All P0 bugs documented in current-issues.md

If PASS:
[ ] progress-tracker.md: feature status confirmed COMPLETE
[ ] AT file filed in docs/testing/acceptance/
[ ] HO-XXX.md written with AT results and next recommended actions

If FAIL/PARTIAL:
[ ] Bugs documented in current-issues.md
[ ] HO-XXX.md written directing agent to fix bugs
[ ] AT-XXX-1.md created for follow-up run after fixes
[ ] Do NOT proceed to next feature until P0 bugs resolved

Deployment:
[ ] Container rebuilt/restarted after backend change
[ ] Frontend rebuilt and copied to static dir after frontend change
[ ] Logs checked after deploy — no startup errors
[ ] Production URL accessible and returning correct responses
```

---

# PHASE 7 — MAINTENANCE AND EVOLUTION

## What This Phase Is

The project is in production. Users are using it. Now the work is
different: bugs appear, features are requested, the context evolves.
This phase describes how to maintain the system without accumulating
technical debt or losing architectural integrity.

## The Two Types of Work in Maintenance

**Bug fixes** — something that was working has stopped working, or
something that was specified was implemented incorrectly.

Protocol:
1. Document in current-issues.md with exact symptoms
2. Diagnose before fixing (capture exact error, identify layer)
3. Write a fix spec for the implementing agent
4. Verify fix with AT follow-up run

**Feature evolution** — new features are requested or existing
features are extended.

Protocol:
1. Phase 0 check: does this fit the vision and out-of-scope list?
2. Phase 2 check: does this require a new architectural decision?
3. Update progress-tracker.md with new feature entry
4. Write F-XXX spec (Phase 4)
5. Implement with tests (Phase 5)
6. Accept (Phase 6)

## Keeping .context/ Files Accurate

The .context/ files are only useful if they are accurate. An inaccurate
context file is worse than no context file — it actively misleads agents.

Rules:
- progress-tracker.md is updated at the END of every agent session
- current-issues.md is updated whenever a bug is confirmed or resolved
- architecture.md is updated whenever an invariant changes or is added
- Never let progress-tracker.md be more than one session out of date

## Managing Technical Debt

Technical debt is implementation shortcuts that will need to be fixed
later. Left unchecked, it makes every future feature harder to build.
The most common sources in AI-agent development:

**Skipped tests**: "We'll add tests later." Later never comes.
Prevention: Phase 5 protocol — no production code without RED tests.

**Undocumented decisions**: A decision was made in a session but not
recorded in an ADR or architecture.md. The next agent makes the
opposite decision.
Prevention: Every significant decision gets an ADR within the session
it is made.

**Duplicate code between agents**: Antigravity writes a utility function.
Deepseek v4 writes a different version of the same function in the
frontend. Both drift independently.
Prevention: Shared utilities explicitly defined in code-standards.md.
Agents instructed to check for existing utilities before writing new ones.

**Context drift**: .context/ files describe the system as it was six
months ago. Agents make decisions based on stale information.
Prevention: Monthly review of all .context/ files. Flag anything that
no longer matches the actual codebase.

## The Monthly Review

Once a month, spend 30 minutes on system health:

```
[ ] Read progress-tracker.md — does it match reality?
[ ] Read architecture.md — are all invariants still in place?
[ ] Read current-issues.md — are any bugs older than 2 sprints?
[ ] Run all tests — are they still green?
[ ] Check for unused dependencies in requirements.txt / package.json
[ ] Check for deprecated packages with known vulnerabilities
[ ] Review docs/handovers/ — what patterns keep recurring?
[ ] Update AGENTS.md if any workflow rules have changed
```

---

## Phase 7 Checklist (Ongoing)

```
After Every Agent Session:
[ ] progress-tracker.md updated
[ ] current-issues.md updated (bugs added or removed)
[ ] HO-XXX.md filed in docs/handovers/

After Every Bug Fix:
[ ] Root cause documented in the issue entry
[ ] AT follow-up run (AT-XXX-N)
[ ] current-issues.md entry removed

After Every New Feature Request:
[ ] Phase 0 check: fits vision and out-of-scope list?
[ ] Phase 2 check: new ADR needed?
[ ] F-XXX spec written
[ ] progress-tracker.md updated

Monthly:
[ ] All .context/ files reviewed for accuracy
[ ] All tests running and green
[ ] Dependencies checked for security updates
[ ] Handover history reviewed for recurring patterns
```

---

# QUICK REFERENCE — THE COMPLETE CYCLE

## Starting a New Project

```
Phase 0:  Problem statement → Vision → Users → Out of scope
Phase 1:  Repository → .context/ files → Agent config → Infrastructure baseline
Phase 2:  ADRs for all major decisions → architecture.md invariants
Phase 3:  Agent registry → File domains → Handover protocol
Phase 4:  F-001 spec → Gherkin → [repeat for all features]
Phase 5:  Tests (RED) → Code (GREEN) → Refactor → 3-layer AT
Phase 6:  AT-001 → fix bugs → AT-001-1 → deploy
Phase 7:  Maintain → evolve → monthly review
```

## Starting a New Feature (Mid-Project)

```
1. Check progress-tracker.md — what is the current state?
2. Check current-issues.md — any open bugs that must go first?
3. Write F-XXX spec
4. Write Gherkin .feature file
5. Agent writes tests → confirms RED
6. Agent writes code → confirms GREEN
7. Run 3-layer AT → file AT-XXX.md
8. Update progress-tracker.md
9. Agent writes HO-XXX.md
```

## Debugging a Bug

```
1. Add bug to current-issues.md with exact symptoms
2. Identify the layer: [DB] [API] or [UI]
3. Capture exact error:
   [DB]:  SQL query showing row state
   [API]: curl output or DevTools Network payload
   [UI]:  DevTools Console error + Network request body
4. Trace to exact file and line
5. Write ONE fix plan
6. Implement ONE change
7. Verify all three layers
8. File AT-XXX-N follow-up
9. Remove from current-issues.md when resolved
```

---

# APPENDIX A — THE .context/ FILE TEMPLATES

## AGENTS.md Template

```markdown
# AGENTS.md — [Project Name] Agent Entry Point

**Project**: [name]
**Server**: [host]
**Project root**: [full path]
**Staging URL**: [URL]
**Deployment**: [method]

## Read These Files First (in order)
1. .context/project-overview.md
2. .context/architecture.md
3. .context/code-standards.md
4. .context/ai-workflow-rules.md
5. .context/ui-context.md    (frontend only)
6. .context/progress-tracker.md
7. .context/current-issues.md  (if exists)
8. .context/feature-specs/F-XXX.md  (assigned feature)

## File Domain Split
| Agent | Owns | Never Touches |
|-------|------|---------------|
| [Backend agent] | backend/** | src/** |
| [Frontend agent]| src/**    | backend/** |

## The One Rule
No production code until tests are FAILING (RED).

## After Completing Work
1. Run acceptance checklist from F-XXX.md
2. Update .context/progress-tracker.md
3. Write docs/handovers/HO-XXX.md

## Hard Rules
[Project-specific invariants here]
```

## ai-workflow-rules.md (Universal — Copy Unchanged)

Already provided in the EPM .context/ files.
This file does not change between projects.

---

# APPENDIX B — DOCUMENT TYPE REFERENCE

| Code | Type | Purpose | Location |
|------|------|---------|----------|
| F-XXX | Feature Spec | What to build | .context/feature-specs/ |
| HO-XXX | Handover Brief | Agent-to-agent context | docs/handovers/ |
| AT-XXX | Acceptance Test | UAT results | docs/testing/acceptance/ |
| ADR-XXX | Architecture Decision | Why choices were made | docs/decisions/ |
| BR-XXX | Business Requirement | What the system must do | docs/requirements/ |
| SC-XXX | Gherkin Scenario | Executable test spec | docs/testing/features/ |

Document naming is always chronological and sequential.
Never reuse a number. Never modify a historical document.
Create follow-ups (AT-001-1) instead of editing originals.

---

# APPENDIX C — COMMON FAILURE MODES

| Failure | Symptom | Prevention |
|---------|---------|-----------|
| Vibe coding | Features work then mysteriously break | Write tests before code |
| Context drift | Agent makes decisions that contradict earlier ones | Keep .context/ files accurate |
| Agent collision | Two agents edit the same file | File domain separation |
| Missing RED phase | Tests always pass, bugs in production | Run tests before implementation |
| Float monetary values | Rounding errors at large numbers | String contract in architecture.md |
| Session cookie | Users logged out every browser close | Specify max_age in auth ADR |
| Symptom fixing | Same bug reappears in different form | Debug protocol: trace to root cause |
| Scope creep | Features keep expanding, nothing ships | Phase 0 out-of-scope list |
| Stale tracker | No one knows what is actually done | Update progress-tracker.md every session |
| Lost decisions | Same architectural debate happens twice | Write ADR at time of decision |

---

# APPENDIX D — TEST TAXONOMY STANDARD

## Why a Taxonomy

A test file named `test_br001_gherkin.py` tells you nothing about what
it tests, which system boundary it covers, or where to look when it
fails. A test named `AUTH-LOGIN-BE-INT-001` tells you the domain
(Authentication), the workflow (Login), the layer (Backend), the type
(Integration), and the sequence number — without opening the file.

An engineer or AI agent must be able to identify the failing subsystem,
workflow, layer, and file location solely from the test identifier.

## The Identifier Standard

```
<DOMAIN>-<WORKFLOW>-<LAYER>-<TYPE>-<NNN>

Examples:
  AUTH-LOGIN-BE-INT-001    login endpoint integration test
  AUTH-LOGIN-FE-E2E-001    login flow end-to-end browser test
  SEC-JWT-BE-SEC-001       JWT cookie security test
  INF-DOCKER-SMK-001       Docker health check smoke test
  HOLD-CREATE-BE-API-001   create holding contract/schema test
```

## Domain Codes

Each project defines its own domain codes based on its bounded contexts.
Add new domain codes only when a new bounded context is introduced.

EPM domain codes:
```
AUTH  HOLD  PRIC  PRIH  DASH  REGR  CLAM  DIVD
TRAN  NAVH  WTCH  COMP  ADMN  USER  OBSD  CHAT
SEC   INF
```

Generic starting codes for new projects:
```
AUTH = Authentication
USER = User Management
ROLE = Roles and Permissions
FILE = File Management
NOTF = Notifications
AUDT = Audit Logs
SETT = Settings
SEC  = Security
INF  = Infrastructure
```

## Layer Codes

```
BE   = Backend (Python, Go, Node — server-side)
FE   = Frontend (React, Vue — browser-side)
SEC  = Security (auth boundaries, injection, escalation)
INF  = Infrastructure (Docker, Traefik, CI/CD, health)
```

## Type Codes

```
UT   = Unit Test (isolated function/class, no DB, no HTTP)
INT  = Integration Test (real FastAPI flow, real DB operations)
API  = Contract/Schema Test (request/response shape validation)
E2E  = End-to-End Test (Playwright, full browser workflow)
SMK  = Smoke Test (is the service alive and reachable?)
REG  = Regression Test (confirms a fixed bug stays fixed)
PERF = Performance Test (response time, throughput)
SEC  = Security Test (auth bypass, injection, privilege escalation)
```

## Folder Structure

Tests are organised by business domain first, not by test type.

```
tests/
├── backend/
│   ├── auth/
│   │   ├── login/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── contract/
│   │   └── logout/
│   └── [domain]/
│       └── [workflow]/
│           ├── unit/
│           ├── integration/
│           └── contract/
├── frontend/
│   └── [domain]/
│       └── [workflow]/
├── security/
│   └── [topic]/
├── infrastructure/
│   └── [service]/
└── fixtures/
    ├── conftest.py
    ├── factories.py
    └── seed_data.py
```

## Deterministic Mapping Rule

A test identifier maps directly to its folder location.
This mapping must never break.

```
AUTH-LOGIN-BE-INT-001  →  tests/backend/auth/login/integration/
AUTH-LOGIN-FE-E2E-001  →  tests/frontend/auth/login/
SEC-JWT-BE-SEC-001     →  tests/security/authentication/jwt/
INF-DOCKER-SMK-001     →  tests/infrastructure/docker/
```

## Requirement Traceability

Requirements are identified as REQ-DOMAIN-NNN.
A requirement maps to multiple tests (bidirectional).

```
REQ-AUTH-001 (30-day persistent login)
  ├── AUTH-LOGIN-BE-INT-001   cookie max_age=2592000
  ├── AUTH-LOGIN-BE-API-001   Set-Cookie header contract
  └── SEC-JWT-BE-SEC-001      httpOnly, SameSite attributes

REQ-HOLD-001 (holdings CRUD)
  ├── HOLD-CREATE-BE-INT-001  POST creates record
  ├── HOLD-UPDATE-BE-INT-001  PATCH updates correctly
  └── HOLD-DELETE-BE-INT-001  soft delete only
```

## Test File Template

Every test file opens with this docstring:

```python
"""
Test ID:     HOLD-CREATE-BE-INT-001
Domain:      Holdings
Workflow:    Create
Layer:       Backend
Type:        Integration
Requirement: REQ-HOLD-001
Feature:     F-003 Holdings
"""
```

Every assertion has a traceability comment:

```python
# REQ-HOLD-001 | F-003 | SC-028 | Then status is draft
assert data["status"] == "draft"

# REQ-HOLD-001 | monetary contract | avg_purchase_price must be string
assert isinstance(data["avg_purchase_price"], str)
```

## Frontend Test Rule

Organise Playwright/E2E tests around USER WORKFLOWS, not page names.

```
Correct:   tests/frontend/auth/login/login-success.e2e.spec.ts
Incorrect: tests/frontend/login-page.spec.ts
```

A workflow may span multiple pages. The test file name describes
the workflow outcome, not the page visited.

## Security Tests Are First-Class

Security tests are not optional and not deferred.
Every feature that has auth or role enforcement must have a SEC test.

Minimum security coverage per feature:
```
[ ] Unauthenticated request → 401
[ ] Wrong role (readonly on write endpoint) → 403
[ ] Input with SQL injection patterns → 422 or rejected
[ ] JWT with tampered signature → 401
```

---

# APPENDIX E — BUG CAPTURE AND REPORTING

## The Problem This Solves

When you spot a bug in the browser, you need a way to log it that:
1. Captures enough information for any agent to diagnose it
2. Works whether you are using Hermes, OpenCode, or ChatGPT web
3. Does not require you to remember the file paths or codebase structure
4. Produces actionable output without back-and-forth clarification

## The Bug Report Format

Copy the template from `assets/bug-report-template.md`, fill in the
four key sections, and paste it to any agent.

The four key sections:
```
1. What I Did        — exact steps (numbered)
2. What I Expected   — what should have happened
3. What Happened     — exact error, paste verbatim
4. Layer             — [DB] [API] [UI] or Unknown
```

The template includes an "Agent Instructions" section that tells
any agent exactly what to do when it receives the report — read
context files, follow debug protocol, write analysis, await approval.

## Bug Severity Levels

```
P0 — Blocking
     Core feature does not work. Data corruption risk. Auth broken.
     Fix before any other work. Do not start next feature.

P1 — Usability impaired
     Feature works partially. Users can work around it.
     Fix within current sprint.

P2 — Polish
     Visual issue, missing tooltip, minor layout problem.
     Fix when convenient. Does not block sprints.
```

## Bug Lifecycle

```
1. You spot anomaly in browser
2. Fill in bug report template
3. Paste to agent (Hermes / OpenCode / ChatGPT)
4. Agent produces root cause analysis + proposed fix
5. You review and approve (or ask questions)
6. Agent implements fix
7. Add to .context/current-issues.md (if not yet fixed)
8. Run relevant AT checklist items
9. File AT-XXX-N follow-up
10. Remove from current-issues.md when resolved
```

## What NOT to Do

```
❌ "The dashboard is broken" — too vague, agent will guess
❌ Paste a screenshot only — agent cannot read the Network tab from an image
❌ "Fix this" without steps to reproduce — agent will fix the wrong thing
❌ Multiple bugs in one report — keep each report to one specific symptom
```

## When You Do Not Have DevTools Evidence

Sometimes you spot a visual bug without checking DevTools.
That is fine — fill in what you know and mark the layer as Unknown:

```
Layer: Unknown — needs diagnosis
Evidence: [describe what you saw — "the chart was blank"]
```

The agent will run the diagnosis steps from the debug protocol
and report back with the layer identified before proposing a fix.

---

# APPENDIX F — AGENT QUICK REFERENCE

## Starting Any Session (Paste to Agent)

```
Read these files before doing anything:
1. .context/AGENTS.md
2. .context/architecture.md
3. .context/code-standards.md
4. .context/ai-workflow-rules.md
5. .context/progress-tracker.md
6. .context/current-issues.md (if it exists)
7. .context/feature-specs/[F-XXX].md (your assigned feature)

Your task: [describe task]
Do not implement until you have confirmed tests are RED.
```

## Debug Session (Paste to Agent)

```
Read .context/AGENTS.md and .context/current-issues.md.

Bug report:
[paste filled bug report template]

Follow the debug protocol from .context/ai-workflow-rules.md:
1. Identify exact layer [DB/API/UI]
2. Capture exact error from logs or network tab
3. Trace to exact file and line
4. Write root cause analysis
5. Propose ONE fix — do not implement

Write "AWAITING APPROVAL" at the end.
```

## Onboarding New Agent (Paste to Agent)

```
You are joining the [project name] development team.

Read these files to understand the project:
1. .context/AGENTS.md (your entry point — start here)
2. .context/project-overview.md
3. .context/architecture.md
4. .context/code-standards.md
5. .context/ai-workflow-rules.md
6. .context/progress-tracker.md

Your role: [Backend Builder / Frontend Builder / Tester]
Your file domain: [backend/** / src/** / tests/**]
You must never touch: [other agent's files]

Your first task: read .context/feature-specs/F-XXX.md
Then write the tests for that feature before writing any production code.
```

## Generating a Fresh Session Prompt (Ask Claude)

When starting a new Claude chat after a long gap:

```
I need a fresh session master prompt for the [project] project.
Read .context/progress-tracker.md and .context/current-issues.md
and generate a FRESH_SESSION_MASTER_PROMPT.md that captures:
- Current feature status
- Open bugs
- Next priority order
- All locked architectural decisions
- Agent team and file domains
```
