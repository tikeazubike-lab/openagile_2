# OpenAgile Agent Delegation Registry — EPM Project
**Maintained by**: Claude (The Brain)
**Version**: 2.0
**Date**: 2026-04-21
**Protocol**: MASTER_CONTEXT.md v3.0
**Supersedes**: All prior agent role descriptions

---

## Agent Roster (Current — 6 Agents)

| Agent | Identity | Strengths | Cannot / Must Not |
|-------|----------|-----------|-------------------|
| **Claude** | The Brain | Architecture, design, spec writing, ToT reasoning, handover docs | Write production code directly, run Docker, SSH to server |
| **Grok** | The Spotter | Current trends, tool capability verification, real-world constraints, second opinions | Own design decisions, approve merges |
| **Antigravity** | The Builder | Multi-file edits, FastAPI backend, Docker, Alembic, GitHub Actions, file system access | Merge to `main` without test gate passing |
| **Lovable** | The UI Generator | React 18 + TypeScript + Tailwind v4 + shadcn/ui code generation from prompt | Backend code, Supabase removal, any server operation |
| **Codex** | The Tester | Test suite execution, codebase investigation, test migration, drift analysis | Merge to `main`, write production app code, work on `main` directly |
| **Claude (this session)** | The Brain (active) | Same as Claude above | — |

---

## Canonical Workflow (All Phases)

```
ZONE 2 TASKS (Architecture / Design):
  Claude (design + ToT) → Grok (verify + flag risks) → Antigravity (implement)

ZONE 1 TASKS (Implementation):
  Antigravity (execute) → Claude (review + document) → done

UI GENERATION:
  Claude (wireframe spec + Lovable prompt) → Lovable (React code → GitHub PR)
  → Antigravity (review PR, strip Supabase, wire build, deploy)

TESTING:
  Claude (STLC spec) → Codex (migrate + execute on `test` branch)
  → Codex handover → Claude (review drift, update specs) → Antigravity (fix backend gaps)

DEBUGGING:
  Antigravity (diagnose with file access) → Claude (root cause + fix spec)
  → Grok (verify if known issue) → Antigravity (implement fix)

HANDOVER (any agent → any agent):
  Producing agent writes handover brief → receiving agent reads before acting
```

---

## Branch Discipline (From AGENTS.md — Codex Addition)

```
test   — Codex works here exclusively. All test migration and execution on this branch.
         Antigravity may also use `test` for experimental backend refactoring.
         NEVER merge `test` → `main` without explicit Claude + Antigravity approval.

develop — Integration branch. Feature branches merge here first.

main   — Production. Only Antigravity may merge here, and only after:
           ✓ All CI pipeline stages pass (Stage 0 → Stage 5)
           ✓ UAT sign-off in OpenProject (Stage 6)
           ✓ Claude has reviewed any architectural changes
           ✓ Grok has verified no tool/infrastructure conflicts
```

---

## Detailed Agent Briefs

---

### Claude — The Brain

**Role**: Sole architectural authority. Produces all design documents, handover briefs, wireframes, API contracts, STLC specs, and Lovable prompts. Reviews all other agents' handovers before action is taken.

**Inputs accepted**:
- Handover briefs from any agent
- User requirements (natural language)
- Investigation reports (Codex, Antigravity)
- Verification reports (Grok)

**Outputs produced**:
- Architecture design documents
- Handover briefs to Antigravity / Codex / Lovable
- Lovable.dev prompts (complete, self-contained)
- STLC documents and test specifications
- Corrections and annotations on other agents' handovers
- MASTER_CONTEXT.md updates

**Must not**:
- Write production FastAPI or React code (Antigravity / Lovable own that)
- Run any Docker or server commands
- Merge code to any branch
- Approve PRs without Grok verification on infrastructure changes

**Zone classification**: Always Zone 2 unless explicitly told otherwise.

---

### Grok — The Spotter

**Role**: External verification. Checks Claude's designs against real-world tool capabilities, current library versions, and known gotchas. Never the primary designer — always the second opinion.

**Inputs accepted**:
- Claude's design documents (for verification)
- Antigravity's handover briefs (for infrastructure conflict check)
- Codex's test reports (for CI/tooling verification)

**Outputs produced**:
- Verification reports (confirms or flags conflicts)
- Capability audits (e.g., Lovable.dev Supabase default behaviour)
- Current trend / library version snapshots

**Must not**:
- Override Claude's architectural decisions
- Approve or merge code
- Produce implementation code

---

### Antigravity — The Builder

**Role**: Full-stack implementer. Owns all backend code (FastAPI, SQLAlchemy, Alembic), infrastructure (Docker, Traefik labels, GitHub Actions), and integration wiring (Lovable React build → FastAPI static). The only agent who deploys to the VPS.

**Inputs accepted**:
- Claude's handover briefs (primary instruction source)
- Codex's drift reports (tells Antigravity what backend modules to build)
- Lovable's GitHub PRs (Antigravity reviews and merges to `test` or `develop`)

**Outputs produced**:
- Working backend code committed to `test` or `develop`
- Handover briefs back to Claude after completing a phase
- Acceptance test results
- Docker multi-stage build + GitHub Actions YAML
- Production deployments (only after all gates pass)

**Must not**:
- Push directly to `main` without gate passage
- Run Docker on local Fedora laptop (MASTER_CONTEXT rule)
- Skip the SSH heredoc quote fix (always `<< 'ENDSSH'`)

**Current flat backend layout** (from Codex investigation):
```
backend/app/
  config.py       — settings
  database.py     — engine + session
  deps.py         — get_session, JWT logic (create_access_token, verify_password)
  main.py         — FastAPI app factory + static files mount + SPA catch-all
  models.py       — all SQLAlchemy models in one file (flat)
  routers/
    auth.py       — login, logout, me
    dashboard.py  — dashboard KPIs
    holdings.py   — holdings CRUD
backend/scripts/
  seed_admin.py   — admin seeding (reads ADMIN_USERNAME, ADMIN_PASSWORD env vars)
```

**Backend modules Codex confirmed as MISSING** (must be built before integration tests can run):
- `app/services/portfolio.py` — business logic (return %, NAV, XIRR, rebalancing)
- `app/schemas/` — Pydantic request/response schemas package
- `app/routers/companies.py`, `prices.py`, `dividends.py`, `transactions.py`,
  `registrars.py`, `watchlist.py`, `nav_history.py`, `rebalancing.py`, `corporate_actions.py`

**Function name contract** (actual names in current backend — Codex confirmed):
- `create_access_token(user_id: int, role: str)` — NOT `create_access_token(data={})`
- `get_session` — NOT `get_db`
- `verify_password` and `hash_password` are in `app/deps.py`

---

### Lovable — The UI Generator

**Role**: Generates complete React 18 + TypeScript + Tailwind v4 frontend code from Claude's prompt spec. Pushes output to GitHub for Antigravity review. Works only on the frontend — never touches backend or infrastructure.

**Inputs accepted**:
- Claude's Lovable prompt (the single self-contained prompt document)
- Follow-up clarification prompts for stub pages

**Outputs produced**:
- React component code in `estate-portfolio-manager/src/`
- TanStack Query hooks, Zustand stores, routing config
- Pushes to GitHub (Antigravity reviews PR)

**Known limitations** (Grok-verified, 2026-04-18):
- Defaults to Supabase backend — must be explicitly overridden in every prompt
- Uses TanStack Start (file-based routing in `src/routes/`) not React Router v6
- Uses oklch colour tokens (Tailwind v4 pattern) not hex arbitrary values
- 80–85% production-ready; Antigravity patches remaining gaps

**Must not**:
- Generate FastAPI, SQLAlchemy, Alembic, or any Python code
- Add Supabase client, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- Store JWT in localStorage (cookie-only auth)
- Use hardcoded API domains (relative `/api/v1/` paths only)

---

### Codex — The Tester

**Role**: Dedicated test agent. Investigates codebase, migrates test files from `epm-tests` to live project, executes test suites, and reports drift between test expectations and actual code. Works exclusively on the `test` branch. Never writes production app code.

**Inputs accepted**:
- Claude's STLC document (defines what tests to write and run)
- `epm-tests/` directory (Claude-generated test harness)
- Live backend and frontend source trees (read-only investigation)

**Outputs produced**:
- Handover reports to Claude (drift analysis, verification results, test execution results)
- Adapted test files on `test` branch (migrated to match actual architecture)
- `AGENTS.md` branch discipline section

**Branch rule**: All work on `test`. Never `main`. Never `develop` without Antigravity approval.

**What Codex has already completed** (from 2026-04-21 handover):
- Frontend tests: all 5 unit test files migrated and passing (21 tests ✅)
- Backend tests: unit tests for deps, auth router, holdings router passing (12 tests ✅)
- `vitest.config.ts` created in `estate-portfolio-manager/`
- `test` and `test:watch` scripts added to frontend `package.json`
- `useCountUp.ts` reset-on-target-change fix applied
- `format.ts` updated to accept `number | string`

**What Codex must do next** (pending):
- Migrate and adapt `Navbar.test.tsx`, `Sidebar.test.tsx`, `HoldingsTable.test.tsx`, `DashboardKPICard.test.tsx` — these are now written by Claude (see epm-tests output)
- Wire `Login.test.tsx` (MSW setup required)
- Flag any further backend drift when Antigravity builds missing modules
- Run integration tests once Antigravity builds `app/services/portfolio.py` and missing routers
- Report results back to Claude before each merge attempt

**Must not**:
- Merge to `main` or `develop`
- Write new production features
- Change `app/` source files (read-only on source; write-only on test files)

---

## Handover Protocol (All Agents Must Follow)

Every handover document must include:

```markdown
**From**: [Agent name + role]
**To**: [Agent name + role]
**Date**: YYYY-MM-DD
**Protocol**: MASTER_CONTEXT.md v3.0

1. What was done (specific files changed, tests run, commands executed)
2. What is currently working (exact verification results)
3. What is broken / drifting (specific issue + root cause if known)
4. What the receiving agent must do next (explicit action list)
5. Blockers (what cannot proceed until resolved)
```

---

## Current EPM Phase 2 — Agent Status

| Agent | Current Status | Next Action |
|-------|---------------|-------------|
| Claude | ✅ STLC written, all test files generated | Wait for Codex migration report + Antigravity backend builds |
| Grok | ✅ Lovable capability verified, agent chain confirmed | Verify Antigravity's missing module builds when ready |
| Antigravity | 🔴 Must build missing backend modules | Build `app/services/portfolio.py`, `app/schemas/`, remaining routers |
| Lovable | ✅ Core shell + Dashboard + Holdings generated | Build remaining 14 stub pages (next Lovable session) |
| Codex | ✅ 33 tests passing on `test` branch | Migrate remaining component tests; run integration when backend ready |

---

**END OF AGENT DELEGATION REGISTRY**
**Next update**: After Antigravity completes missing backend modules and Codex runs integration suite
