# EPM Hybrid Framework
## Spec-First + Test-Driven Development for Multi-Agent Systems

**Version**: 1.0
**Date**: 2026-06-15
**Author**: Claude (The Brain)
**Status**: APPROVED — implement this framework for EPM Phase 3 onwards

---

## Part 1: The Framework Philosophy

### Why This Exists

Three prior approaches each solved part of the problem:

| Approach | What It Solved | What It Missed |
|----------|---------------|---------------|
| Uncle Bob TDD | Code correctness — tests prove features work | No spec discipline — "what to test" was still vague |
| Ghost AI Spec-Driven | Clarity — agents have precise specs before starting | No test discipline — agents vibe-implement against checklist |
| EPM HO-* system | Multi-agent coordination, audit trail, handovers | No single feature document — specs spread across HO, SPEC, BR, AT files |

The hybrid fuses all three:

```
SPEC (what to build) → GHERKIN (how to prove it) → RED (tests fail)
→ CODE (make tests pass) → GREEN → CHECKLIST (3-layer AT) → DONE
```

### The One Rule That Cannot Be Broken

> **No agent writes production code for a feature until:
> (a) a spec file exists, AND
> (b) tests for that feature are confirmed failing (RED)**

This is Uncle Bob's rule. It has no exceptions. An agent that skips
straight to implementation is vibe-coding regardless of what spec
exists. The spec tells you WHAT to build. The failing test proves
you haven't built it yet. Only then does implementation have purpose.

---

## Part 2: Folder Structure

### Repository Layout (EPM)

```
estate-portfolio/
│
├── .context/                          ← Agent context (read every session)
│   ├── AGENTS.md                      ← Entry point — agent reads this first
│   ├── project-overview.md            ← What EPM is, goals, scope, success criteria
│   ├── architecture.md                ← Stack, invariants, API contract rules
│   ├── code-standards.md              ← Python + TypeScript conventions
│   ├── ai-workflow-rules.md           ← How agents behave, zone system
│   ├── ui-context.md                  ← Design tokens, oklch vars, DM Mono, fonts
│   ├── progress-tracker.md            ← ONLY file that updates constantly
│   └── current-issues.md             ← Active bugs only (GITIGNORED)
│
├── .context/feature-specs/            ← One file per feature (the build queue)
│   ├── F-001-auth.md
│   ├── F-002-dashboard.md
│   ├── F-003-holdings.md
│   ├── F-004-price-entry.md
│   ├── F-005-price-history.md
│   ├── F-006-registrars.md
│   ├── F-007-nav-history.md
│   ├── F-008-dividends.md
│   ├── F-009-transactions.md
│   ├── F-010-claims.md
│   ├── F-011-rebalancing.md
│   ├── F-012-watchlist.md
│   ├── F-013-companies.md
│   ├── F-014-corporate-actions.md
│   ├── F-015-obsidian-import.md
│   └── F-016-settings.md
│
├── docs/                              ← Permanent record (never deleted)
│   ├── decisions/                     ← ADR-*.md (architectural decisions)
│   ├── requirements/                  ← BR-*.md (business requirements)
│   ├── testing/
│   │   ├── features/                  ← Gherkin .feature files (specs, not runtime)
│   │   └── acceptance/                ← AT-*.md (historical UAT results)
│   ├── handovers/                     ← HO-*.md (agent handovers, archive)
│   └── archive/                       ← Everything superseded goes here
│
├── backend/
│   ├── app/
│   └── tests/                         ← SINGLE authoritative test tree
│       ├── unit/
│       ├── integration/
│       ├── contract/
│       └── db/
│
├── estate-portfolio-manager/src/
│
├── .github/workflows/                 ← CI/CD (to be built in F-000)
│
└── .gitignore                         ← includes current-issues.md, uploads/, .env
```

### Key Structural Decisions

**`.context/` not `context/`**: The dot-prefix hides it from casual
browsing but keeps it accessible. Agents know to look for it.

**Feature specs in `.context/feature-specs/`**: Numbered with F-prefix.
Agents get one file per session. Simple, findable, unambiguous.

**`docs/` is a permanent archive**: Nothing is ever deleted from docs/.
ADRs, BRs, HOs, ATs all live here permanently. They are reference
material, not agent working memory.

**`current-issues.md` is gitignored**: Active bugs are volatile — they
change every session. Committing them creates noise. The agent reads
the file from disk; it does not need to be in version control.

---

## Part 3: The Seven Context Files

These files live in `.context/` and are loaded by every agent at the
start of every session. They are the agent's memory.

### File 1 — AGENTS.md (Entry Point)

The first file every agent reads. Tells the agent what to load and
in what order.

```markdown
# AGENTS.md — EPM Agent Entry Point

You are an implementation agent for the Estate Portfolio Manager (EPM).

## Before every session, read these files in order:
1. .context/project-overview.md
2. .context/architecture.md
3. .context/code-standards.md
4. .context/ai-workflow-rules.md
5. .context/ui-context.md        (frontend work only)
6. .context/progress-tracker.md  (current state)
7. .context/current-issues.md    (if it exists — active bugs)

## Then read the feature spec for your assigned task:
.context/feature-specs/F-XXX-feature-name.md

## After completing work:
- Update .context/progress-tracker.md
- Write a handover brief (HO-* format) and place in docs/handovers/
- Run acceptance checklist from feature spec
- Commit with conventional commit format

## Hard rules — no exceptions:
- No production code before tests are RED
- No implementation without a feature spec
- No merging to main without full checklist passing
- backend/ files: Antigravity only
- src/ files: Deepseek v4 only
```

### File 2 — project-overview.md

```markdown
# EPM — Project Overview

## What It Is
A self-hosted Nigerian stock portfolio tracker for personal investment
management. Tracks NGX equities (active + claims), dividends, registrar
relationships, and administrative documents. Self-hosted on Netcup VPS.

## Three Morning Goals (North Star)
Every Dashboard feature must serve one of these:
1. Net worth: "What do I own and what is it worth today?"
2. Administration: "What paperwork is outstanding?"
3. Performance: "Is my portfolio growing over time?"

## Users
- Admin (owner): full read + write + administration
- Viewer (future): read-only across all pages
- Multi-portfolio (Phase 4): separate portfolios per user

## Asset Scope
Current: NGX listed equities, delisted/defunct equities, merged equities
Future: Eurobonds, real estate, treasury bills, fixed deposits, mutual funds

## In Scope (Now)
[16 features — see .context/feature-specs/]

## Out of Scope (Forever)
- Real-time market data feeds (NGX has no free API)
- Automated broker integration
- Tax filing automation
- Social / sharing features
- Mobile native app

## Success Criteria
The system is complete when:
- [ ] User sees total net worth in one number on Dashboard
- [ ] User sees all pending administrative actions
- [ ] User tracks portfolio performance over any time period
- [ ] All NGX holdings (active + claims) are represented
- [ ] All registrar document requirements are tracked
- [ ] Price updates take < 5 minutes via NGX PDF upload
- [ ] Works reliably on desktop and mobile browsers
```

### File 3 — architecture.md

```markdown
# EPM — Architecture

## Stack
- Backend: FastAPI 0.115.6 + SQLAlchemy 2.0 async + Alembic + asyncpg
- Frontend: React 18 + TypeScript + Vite + TanStack Router
- Database: PostgreSQL 15 (shared openagile_postgres — NEVER create a new one)
- Container: Single Docker container (FastAPI serves React static files)
- Proxy: Traefik v2.10 + Let's Encrypt

## Invariants (Rules the System Must Never Violate)
1. Monetary values are strings in API responses — never floats
2. bcrypt==4.0.1 pinned — do not upgrade (passlib incompatibility)
3. get_session() not get_db() — session function name in database.py
4. create_access_token(user_id: int, role: str) — token function signature
5. JWT in httpOnly cookie — never localStorage
6. cookie max_age=60*60*24*30 — always 30-day persistent, never session-only
7. Soft delete only — deleted_at = datetime.now(timezone.utc)
8. All deploys via GitHub Actions — never manual SSH deploy
9. SSH to VPS = read/diagnose only — never deploy via SSH
10. No new Postgres containers — reuse shared openagile_postgres

## API Contract
- Response envelope: { data: ..., meta: { total: N }, error: null }
- Monetary values: always strings ("12345.50" not 12345.50)
- Recharts exception: parse strings to floats at component boundary only
- Soft-deleted records: excluded by default

## File Domain (Agent Conflict Prevention)
- Antigravity: backend/**, docker-compose.v2.yml, .github/workflows/**
- Deepseek v4: estate-portfolio-manager/src/**
- Push sequence: Antigravity pushes backend first → Deepseek v4 pulls → fixes frontend
```

### File 4 — code-standards.md

```markdown
# EPM — Code Standards

## Python (Backend)
- Type hints on all function signatures
- Pydantic models for all request bodies (never raw dict)
- field_validator for domain validation (positive numbers, future dates)
- Decimal for all monetary arithmetic
- datetime.now(timezone.utc) for all timestamps (never datetime.utcnow())
- Async/await throughout — no sync DB calls
- HTTPException(status_code=N, detail="message") for all error responses

## TypeScript (Frontend)
- Strict mode — no `any`
- Null-safe rendering: value?.toFixed(2) ?? "—" — never assume non-null API data
- Monetary display: fmtNaira(value ?? null) from lib/format.ts
- API calls: always credentials: 'include' (httpOnly cookie auth)
- Colour tokens: var(--color-name) — never hardcoded hex
- DM Mono class for all numbers, tickers, monetary values
- No Supabase imports — ever

## Commit Format
feat(scope): description
fix(scope): description
chore(scope): description
test(scope): description
docs(scope): description

## File Naming
Feature specs: F-XXX-feature-name.md
Handovers: HO-XXX-from-to-topic.md (in docs/handovers/)
Acceptance tests: AT-XXX-feature-YYYY-MM-DD.md (in docs/testing/acceptance/)
Architecture decisions: ADR-XXX-decision-title.md (in docs/decisions/)
```

### File 5 — ai-workflow-rules.md

```markdown
# EPM — AI Workflow Rules

## The Execution Sequence (No Exceptions)
1. Read all context files
2. Read the assigned feature spec
3. Write tests for the feature → confirm they are RED
4. Write production code → confirm tests are GREEN
5. Run the feature checklist (3-layer: DB / API / UI)
6. Update progress-tracker.md
7. Commit with conventional format
8. Write handover brief to docs/handovers/

## Zone System
Zone 1 (automate): mechanical tasks, clear precedent, "format/generate/draft"
Zone 2 (add friction): architecture, design, unknown territory — default
When in doubt: stop and write a handover to Claude before proceeding.

## One Feature Unit at a Time
Never combine unrelated system boundaries in one implementation step.
Example of wrong: "build the dividends API and also fix the dashboard chart"
Example of right: "build the dividends API" — full stop.

## When a Decision Is Needed
Stop. Do not guess. Write a handover brief to Claude describing:
- What decision is needed
- What the options are
- What you recommend and why
Do not implement until Claude responds.

## Debug Protocol (Prevent the Fix Spiral)
1. Capture exact error (network tab, server logs, psql)
2. Write analysis: what is wrong, where, why
3. Propose fix plan
4. Send handover to Claude for approval
5. Implement only after approval
Never fix by trial and error.
```

### File 6 — ui-context.md

```markdown
# EPM — UI Context

## Design Aesthetic
Dark, technical, precise — feels like a professional finance tool.
Not corporate. Not startup-bright. Measured and trustworthy.

## Colour Tokens (oklch — Tailwind v4)
All colours via CSS variables. Never hardcode hex values.

Primary actions: var(--accent-lavender)  → #BCBDFA
Danger:          var(--accent-red)        → #F87171
Success:         var(--accent-green)      → #4ADE80
Warning:         var(--accent-amber)      → #FCD34D
Gold/wealth:     var(--accent-gold)       → #DABF82
Surface:         var(--bg-surface)
Subtle bg:       var(--bg-subtle)
Border:          var(--border)
Text primary:    var(--text-primary)
Text secondary:  var(--text-secondary)
Text muted:      var(--text-muted)

## Typography
Numbers, tickers, monetary values: font-mono (DM Mono)
UI text, labels, headings: Plus Jakarta Sans
Code: JetBrains Mono

## Component Patterns
Buttons:
  Primary: bg-[var(--accent-lavender)] text-[#1A1A1A] hover:opacity-90
  Secondary: border border-[var(--border)] text-[var(--text-secondary)]
  Danger: text-[var(--accent-red)] border-[var(--accent-red)]

Inputs:
  h-9 px-3 rounded-lg border border-[var(--border)]
  bg-[var(--bg-surface)] focus:ring-2 focus:ring-[var(--accent-lavender)]

Badges (status):
  pending:   bg-amber-100 text-amber-700
  live:      bg-green-100 text-green-700
  draft:     bg-gray-100  text-gray-600
  claim:     bg-orange-100 text-orange-700

Charts:
  Primary line: #BCBDFA (accent-lavender)
  Area fill: rgba(188,189,250,0.15)
  Always wrap in: <div style={{ width:'100%', height: N }}><ResponsiveContainer>

## Layout Rules
- Edit mode toggle: hidden on /dashboard (read-only page), visible elsewhere
- Edit mode toggle: visible only for admin role
- Actions columns: visible only in edit mode
- Inline editing: InlineEditRow child component (not parent table state)
- Add forms: slide-out drawer from right (not modal, not inline row)
- Tooltips: on all interactive icons and buttons
```

### File 7 — progress-tracker.md

```markdown
# EPM — Progress Tracker
**Last updated**: [agent updates this after every session]

## Current Phase: Phase 3 — Completing Core Pages

## Active Work
[Agent fills this in at session start]

## Feature Status
| ID | Feature | Status | Last Updated |
|----|---------|--------|-------------|
| F-001 | Auth | ✅ Complete | HO-008 |
| F-002 | Dashboard | ⚠️ Bugs open | AT-003-1 |
| F-003 | Holdings | ⚠️ Bugs open | AT-003-1 |
| F-004 | Price Entry | ✅ Complete | AT-001 |
| F-005 | Price History | ✅ Complete | AT-003-1 |
| F-006 | Registrars | ✅ Complete | AT-002 |
| F-007 | NAV History | 📋 Planned | HO-018 |
| F-008 | Dividends | 📋 Planned | — |
| F-009 | Transactions | 📋 Planned | — |
| F-010 | Claims | 📋 Planned | — |
| F-011 | Rebalancing | 📋 Planned | — |
| F-012 | Watchlist | 📋 Planned | — |
| F-013 | Companies | 📋 Planned | — |
| F-014 | Corporate Actions | 📋 Planned | — |
| F-015 | Obsidian Import | 📋 Planned | — |
| F-016 | Settings | 📋 Planned | — |

## Open Bugs
See .context/current-issues.md

## Last 3 Sessions
[Agent appends after each session — most recent first]
```

---

## Part 4: The Feature Spec Format

Every feature gets exactly two files:

### File A — `F-XXX-feature-name.md` (the spec)

```markdown
---
id: F-XXX
title: Feature Name
status: PLANNED | IN-PROGRESS | COMPLETE
owner-backend: Antigravity
owner-frontend: Deepseek v4
sprint: Phase 3C
---

# F-XXX — Feature Name

## Goal
One sentence: what does this feature produce when it is complete?

## Gherkin Reference
Scenarios: SC-XXX through SC-XXX
File: docs/testing/features/F-XXX-feature-name.feature

## Backend
Router: backend/app/routers/feature.py
Endpoints:
  GET  /api/v1/feature        — description
  POST /api/v1/feature        — description
Model: FeatureName in backend/app/models.py
Migration: alembic revision needed? [yes/no]

## Frontend
Route: src/routes/_app.feature.tsx
Components:
  - src/components/feature/FeatureTable.tsx
  - src/components/feature/FeatureDrawer.tsx
Query hooks: useFeature(), useCreateFeature() in src/api/queries.ts

## Dependencies
- F-XXX must be complete first (reason)
- scipy must be in requirements.txt (if XIRR)
- APScheduler must be in requirements.txt (if scheduled)

## Implementation Checklist
### [DB] Database
- [ ] Migration creates table with correct columns
- [ ] Soft delete column (deleted_at) present
- [ ] Monetary columns use Decimal type

### [API] Backend
- [ ] GET endpoint returns correct envelope shape
- [ ] Monetary values are strings in response
- [ ] Admin-only endpoints return 403 for readonly role
- [ ] Soft delete endpoint sets deleted_at correctly
- [ ] No hard deletes anywhere

### [API] Contract
- [ ] curl test: GET /api/v1/feature returns 200
- [ ] curl test: POST with invalid payload returns 422
- [ ] curl test: GET without auth returns 401

### [UI] Frontend
- [ ] Page renders without crash
- [ ] Data loads from API (not mock)
- [ ] Empty state renders correctly (no blank/broken UI)
- [ ] Monetary values display in DM Mono font
- [ ] Edit mode shows/hides action buttons correctly
- [ ] Readonly user cannot see admin controls
- [ ] No console errors on load

## Acceptance Sign-Off
- [ ] All checklist items passing
- [ ] progress-tracker.md updated
- [ ] Handover written to docs/handovers/HO-XXX.md
- [ ] Committed: feat(feature): implement F-XXX feature name
```

### File B — The Gherkin `.feature` file

Goes in `docs/testing/features/F-XXX-feature-name.feature`.
Written by Claude. Executed by Antigravity/Codex as standard pytest.
See existing feature files for format (SC-025 through SC-046).

---

## Part 5: The Session Protocol

### Starting a New Feature Session

Agent prompt (paste into Cursor/Antigravity/Deepseek):

```
Read the following files in order before doing anything:
1. .context/AGENTS.md
2. .context/project-overview.md
3. .context/architecture.md
4. .context/code-standards.md
5. .context/ai-workflow-rules.md
6. .context/ui-context.md          [if frontend work]
7. .context/progress-tracker.md
8. .context/current-issues.md      [if exists]
9. .context/feature-specs/F-XXX-feature-name.md

Then:
1. Update progress-tracker.md: mark F-XXX as IN-PROGRESS
2. Write the tests for this feature → run them → confirm RED
3. Implement the feature → confirm tests are GREEN
4. Run the acceptance checklist from the spec
5. Update progress-tracker.md: mark F-XXX as COMPLETE
6. Write handover to docs/handovers/HO-XXX.md
7. Commit: feat(scope): implement F-XXX feature-name
```

### Debugging a Bug Session

```
Read .context/AGENTS.md and .context/current-issues.md.

Bug: [paste exact error]
Triggered by: [exact action]
Layer: [DB / API / UI]

Do NOT implement a fix yet.
1. Analyse the root cause
2. Propose a fix plan with exact files and lines to change
3. Stop and wait for approval before changing any code
```

### Closing a Feature Session

After all checklist items pass:
1. Delete `current-issues.md` if it exists and all bugs resolved
2. Update `progress-tracker.md` → mark feature COMPLETE
3. Write `docs/handovers/HO-XXX.md`
4. `git add -A && git commit -m "feat(scope): implement F-XXX" && git push origin test`

---

## Part 6: What Changes from the Old System

| Old System | New System | Why |
|-----------|-----------|-----|
| HO-* files are the spec | Feature specs in `.context/feature-specs/` | HO files are handovers — they record what happened, not what to build |
| Specs spread across HO, SPEC, BR, AT files | One F-XXX spec per feature | Single document per feature per agent session |
| MASTER_CONTEXT.md (monolithic) | 7 focused `.context/` files | Agents load only what they need — less token waste |
| Handovers accumulate in root | Handovers archive in `docs/handovers/` | Root stays clean; history is preserved |
| AT files mutated between runs | AT-003, AT-003-1, AT-003-2 naming | Immutable historical record per run |
| current-issues.md committed | current-issues.md gitignored | Bug state is volatile — don't pollute git history |
| No CI/CD | GitHub Actions pipeline (F-000) | Every push deploys to staging automatically |

## What Does NOT Change

- HO-* handover format (same 5-section structure)
- 3-layer testing (DB / API / UI labels)
- Uncle Bob RED → GREEN rule
- Gherkin .feature files in docs/testing/features/
- Agent domain split (Antigravity backend, Deepseek v4 frontend)
- bcrypt==4.0.1 pin
- All monetary values as strings in API
- get_session() not get_db()
- Soft delete with datetime.now(timezone.utc)

---

## Part 7: Reusability (Phase 2 — Codebase-Agnostic)

When applying this framework to other openagile projects (Frappe, ERPNext, etc.):

The `.context/` folder structure is universal. Only these files change
per project:

| File | EPM Version | New Project Version |
|------|------------|-------------------|
| project-overview.md | NGX portfolio tracker | New project description |
| architecture.md | FastAPI + React | Project-specific stack |
| code-standards.md | Python + TypeScript rules | Project language rules |
| ui-context.md | oklch tokens + DM Mono | Project design tokens |
| AGENTS.md | EPM agent roles | Project agent roles |
| progress-tracker.md | EPM feature list | New project feature list |
| ai-workflow-rules.md | ✅ UNIVERSAL — no changes needed | Same file, same rules |
| feature-specs/ template | ✅ UNIVERSAL — no changes needed | Same template, new content |

The framework is already abstracted. To apply it to a new project:
1. Copy `.context/` folder
2. Replace project-specific files (architecture, overview, ui-context)
3. Keep universal files unchanged (ai-workflow-rules, feature template)
4. Write new F-XXX specs for the new project's features

---

## Part 8: Implementation Order for EPM

### Before writing any feature specs — do this first:

**F-000 — GitHub Actions CI/CD** (not a product feature — infrastructure)
This is the most critical gap found in the audit. No specs mean nothing
without a pipeline to validate them.

```
F-000 includes:
  - .github/workflows/ci.yml (fast path + full path)
  - Test schema creation/teardown in CI
  - Deploy to demo.estate.zubbystudio.shop on push
  - scipy and APScheduler added to requirements.txt
```

### Then feature specs in this order:

```
F-001 Auth          (document existing implementation)
F-002 Dashboard     (document + fix open bugs)
F-003 Holdings      (document + fix open bugs)
F-004 Price Entry   (document existing)
F-005 Price History (document existing)
F-006 Registrars    (document existing)
F-007 NAV History   (build — Gherkin spec exists)
F-008 Dividends     (build)
F-009 Transactions  (build)
F-010 Claims        (build)
F-011 Rebalancing   (build)
F-012 Watchlist     (build)
F-013 Companies     (build CRUD page)
F-014 Corporate Actions (build)
F-015 Obsidian Import (build)
F-016 Settings      (build)
```

Features F-001 through F-006 document what already exists. Writing
specs for them serves two purposes: it closes the gap where the
implementation exists but no single authoritative spec document does,
and it surfaces anything in the implementation that deviates from
the original design intent.
