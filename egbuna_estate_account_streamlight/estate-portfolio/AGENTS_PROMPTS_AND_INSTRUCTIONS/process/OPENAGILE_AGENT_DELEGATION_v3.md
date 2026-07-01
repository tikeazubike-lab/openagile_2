# OpenAgile Agent Delegation Registry
**Maintained by**: Claude (The Brain)
**Version**: 3.0
**Date**: 2026-04-25
**Protocol**: MASTER_CONTEXT.md v4.0
**Supersedes**: OPENAGILE_AGENT_DELEGATION.md v2.0 (2026-04-21)

---

## CHANGELOG v2.0 → v3.0

| Change | Detail |
|--------|--------|
| Antigravity "Must not" expanded | No local code execution of any kind (not just Docker) |
| Antigravity new section added | Vault Sync Responsibilities (one-time VPS setup tasks) |
| All agents updated | Reference to zero-load local workflow |
| CI pipeline updated | Fast-path / full-path split documented per agent |

---

## Agent Roster (Current — 6 Agents)

| Agent | Identity | Strengths | Cannot / Must Not |
|-------|----------|-----------|-------------------|
| **Claude** | The Brain | Architecture, design, STLC specs, handover docs, ToT reasoning | Write production code, run any local execution, merge branches |
| **Grok** | The Spotter | Current trends, library versions, tool capability audits, second opinions | Own design decisions, approve merges, write implementation code |
| **Antigravity** | The Builder | FastAPI, Docker, GitHub Actions, Alembic, SSH to VPS, multi-file edits | Any local code execution (no pip, no npm, no pytest, no Docker locally) |
| **Lovable** | The UI Generator | React 18 + TypeScript + Tailwind v4 + shadcn/ui from prompt | Backend code, Supabase, local execution, server operations |
| **Codex** | The Tester | Test execution via SSH to VPS, drift analysis, test migration | Merge to main, write production app code, work on main directly, local execution |
| **You (Owner)** | Product Owner | Direction, decisions, UAT sign-off | — |

---

## Canonical Workflow (All Phases)

```
ZONE 2 TASKS (Architecture / Design):
  Claude (design + ToT) → Grok (verify + flag risks) → Antigravity (implement)

ZONE 1 TASKS (Implementation):
  Antigravity (execute, push to develop) → Fast-path CI deploys to staging
  → Claude (review handover + document)

UI GENERATION:
  Claude (wireframe spec + Lovable prompt) → Lovable (React code → GitHub PR)
  → Antigravity (review PR: strip Supabase, wire build, push to develop)

TESTING:
  Claude (STLC spec) → Codex (SSH to VPS, migrate tests, execute on test branch)
  → Codex handover → Claude (review drift) → Antigravity (fix backend gaps, push)

DEBUGGING:
  Antigravity (diagnose via SSH to VPS, never locally)
  → Claude (root cause + fix spec) → Grok (verify if known issue)
  → Antigravity (implement fix, push to develop)

OBSIDIAN VAULT SYNC:
  You (edit vault, git commit, git push to private repo)
  → vault-sync.yml fires → VPS pulls vault mirror
  → import_obsidian.py runs ON VPS → PostgreSQL updated

HANDOVER (any agent → any agent):
  Producing agent writes handover brief → receiving agent reads before acting
```

---

## Branch Discipline

```
feature/xyz → develop → test → main
    ↑             ↑        ↑       ↑
  All agents    Fast CI  Codex  Manual
  edit here     path     tests  approval
  (code only,   fires    on VPS + prod
  no execution) on push         deploy

RULES:
  - All code work on feature/* or develop branches
  - Codex works exclusively on test branch
  - Only Antigravity merges to main
  - main merges require: all CI stages pass + UAT sign-off
  - NEVER commit test execution results or build artifacts to any branch
  - NEVER run Docker, pip, npm, or pytest on local Fedora workstation
```

---

## Detailed Agent Briefs

---

### Claude — The Brain

**Role**: Sole architectural authority. Produces all design documents, handover briefs, wireframes, API contracts, STLC specs, Lovable prompts, and this registry. Reviews all agent handovers before action is taken.

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
- MASTER_CONTEXT.md updates (v4.0+)
- This Agent Delegation Registry

**Must not**:
- Write production FastAPI or React code
- Run any commands locally or on server
- Merge code to any branch
- Approve PRs without Grok verification on infrastructure changes

**Zone classification**: Always Zone 2 unless explicitly told otherwise.

---

### Grok — The Spotter

**Role**: External verification. Checks Claude's designs against real-world tool capabilities, current library versions, and known gotchas. Never the primary designer — always the second opinion.

**Inputs accepted**:
- Claude's design documents
- Antigravity's handover briefs (for infrastructure conflict check)
- Codex's test reports (for CI/tooling verification)

**Outputs produced**:
- Verification reports (confirms or flags conflicts)
- Capability audits (e.g. Lovable.dev Supabase default, bcrypt/passlib conflicts)
- Current library version snapshots

**Must not**:
- Override Claude's architectural decisions
- Approve or merge code
- Produce implementation code

---

### Antigravity — The Builder

**Role**: Full-stack implementer and sole deployment agent. Owns all backend code (FastAPI, SQLAlchemy, Alembic), infrastructure (Docker, Traefik labels, GitHub Actions), integration wiring (Lovable React build → FastAPI static), and all VPS-side operations. The only agent who deploys to the VPS.

**Inputs accepted**:
- Claude's handover briefs (primary instruction source)
- Codex's drift reports (tells Antigravity what backend modules to build)
- Lovable's GitHub PRs (Antigravity reviews and integrates)

**Outputs produced**:
- Working backend code committed to feature/* or develop
- Handover briefs back to Claude after completing a phase
- Docker multi-stage build + GitHub Actions YAML
- Production deployments (after all gates pass)

**Must not — local workstation (ABSOLUTE)**:
```
❌ docker compose up/down/build/exec  — any Docker operation
❌ pip install / pip run              — any Python package operation
❌ npm install / npm run / npx        — any Node operation
❌ pytest / vitest / playwright       — any test execution
❌ python <anything>                  — any Python execution
❌ Direct SSH to server for deployments (use GitHub Actions)
```

**Verification without local execution**:
- Read GitHub Actions logs in browser
- SSH to VPS for manual checks: `ssh zubbyik@185.216.177.250`
- On VPS: `docker compose exec backend pytest tests/unit/ -v` (VPS has 16GB RAM)

**Always**:
```
✅ git add + git commit + git push only on local workstation
✅ Use quoted heredoc in ALL SSH scripts: << 'ENDSSH'
✅ Push to develop for fast-path CI (staging in ~5 min)
✅ Push to test for full CI suite (Codex + Playwright)
✅ Pin bcrypt==4.0.1 — do not upgrade
```

**Current flat backend layout** (Codex-confirmed 2026-04-21):
```
backend/app/
  config.py    — settings
  database.py  — async engine + get_session (NOT get_db)
  deps.py      — create_access_token(user_id, role), verify_password, hash_password
  main.py      — FastAPI factory + StaticFiles + SPA catch-all
  models.py    — all models (flat single file)
  routers/auth.py, dashboard.py, holdings.py
backend/scripts/seed_admin.py
```

**Missing backend modules Antigravity must build (Phase 2B)**:
```
app/services/portfolio.py
app/schemas/ package
routers: companies, prices, dividends, transactions, registrars,
         watchlist, nav_history, rebalancing, corporate_actions,
         obsidian, claims
```

### Antigravity — Vault Sync Responsibilities (NEW — One-Time Setup)

These are one-time VPS setup tasks that enable the Obsidian vault sync pipeline.

**SSH KEY RULE**: Do NOT generate a new SSH key pair. The VPS already has an
established SSH key used for GitHub Actions deployments (VPS_SSH_KEY secret).
Reuse that existing key as the deploy key for the private vault repo. No new
key generation required.

```
[ ] 1. Confirm existing VPS public key:
        ssh zubbyik@185.216.177.250
        cat ~/.ssh/id_ed25519.pub
        # (or whichever key is already established — check ~/.ssh/ for existing keys)
        # This is the key already trusted by GitHub for CI/CD deployments.

[ ] 2. Add existing VPS public key to private vault GitHub repo:
        → GitHub: obsidian-nigerian-stocks-private → Settings → Deploy Keys → Add Key
        → Paste the public key from step 1
        → Title: "Netcup VPS (existing key)", Allow read-only
        # If this key is already a deploy key on the EPM repo, GitHub may warn
        # about reuse — this is expected and acceptable for a read-only vault repo.

[ ] 3. Verify SSH access from VPS to vault repo (no new config needed
        if existing ~/.ssh/config already points to github.com):
        ssh -T git@github.com
        # Should respond: "Hi zubbyik! You've successfully authenticated..."
        # If a separate Host alias is needed for the vault key:
        # Add to ~/.ssh/config:
        Host github-vault
          HostName github.com
          User git
          IdentityFile ~/.ssh/id_ed25519   # existing key — no new key

[ ] 4. Create vault mirror directory on VPS and clone:
        mkdir -p ~/ObsidianVaultMirror
        git clone git@github.com:zubbyik/obsidian-nigerian-stocks-private.git \
          ~/ObsidianVaultMirror
        # Uses existing SSH identity — no new credentials

[ ] 5. Add vault volume mount to docker-compose.yml:
        services:
          backend:
            volumes:
              - ~/ObsidianVaultMirror:/vault:ro

[ ] 6. Add VPS_SSH_KEY to vault-sync.yml (already exists as GitHub secret):
        # vault-sync.yml reuses the existing VPS_SSH_KEY secret —
        # the same one used by the EPM deploy workflow.
        # No new secret creation required.

[ ] 7. Create vault-sync.yml in the PRIVATE VAULT REPO:
        (see EPM_CICD_ZERO_LOAD_WORKFLOW.md Part B.4)
        # The SSH action in vault-sync.yml uses:
        #   key: ${{ secrets.VPS_SSH_KEY }}  ← existing secret, no change

[ ] 8. Test full pipeline:
        - Edit one .md file in Obsidian locally
        - git commit + git push to private vault repo
        - Confirm vault-sync.yml fires in GitHub Actions
        - Confirm ~/ObsidianVaultMirror updates on VPS
        - Confirm import_obsidian.py runs with --dry-run output
```

---

### Lovable — The UI Generator

**Role**: Generates complete React 18 + TypeScript + Tailwind v4 frontend code from Claude's prompt spec. Pushes output to GitHub for Antigravity review. Frontend only — never touches backend or infrastructure.

**Inputs accepted**:
- Claude's Lovable prompt (self-contained, single document)
- Follow-up prompts for stub pages (sequential, one group at a time)

**Outputs produced**:
- React code in `estate-portfolio-manager/src/routes/` (TanStack Start file-based routing)
- TanStack Query hooks, Zustand stores, routing config
- Pushes to GitHub PR → Antigravity reviews

**Known limitations** (Grok-verified 2026-04-18):
- Defaults to Supabase — must be overridden in every prompt with explicit "DO NOT use Supabase"
- Uses TanStack Start file-based routing (`src/routes/`) not React Router v6
- Uses oklch colour tokens (Tailwind v4) not hex arbitrary values `bg-[var(--x)]`
- 80–85% production-ready; Antigravity patches remaining gaps

**Antigravity's review checklist for every Lovable PR**:
```
[ ] No supabase imports anywhere in src/
[ ] No SUPABASE_URL or SUPABASE_ANON_KEY references
[ ] All API calls use relative /api/v1/ paths (no hardcoded domains)
[ ] No localStorage for JWT (cookie-only auth)
[ ] Vite outputs to dist/ (Antigravity copies to backend/app/static/)
[ ] No "Skip to demo" link in login page
```

**Must not**:
- Generate FastAPI, SQLAlchemy, Alembic, or Python code
- Add Supabase client
- Store JWT in localStorage
- Use hardcoded API domains

---

### Codex — The Tester

**Role**: Dedicated test agent. Investigates codebase, migrates test files, executes test suites on the VPS (never locally), and reports drift. Works exclusively on the `test` branch. Never writes production app code.

**Inputs accepted**:
- Claude's STLC document
- `epm-tests/` directory (Claude-generated test harness)
- Live backend and frontend source trees (read-only investigation)

**Outputs produced**:
- Handover reports to Claude (drift analysis + test execution results)
- Adapted test files committed to `test` branch
- `AGENTS.md` updates

**How Codex executes tests (zero local resources)**:
```bash
# Codex SSHes to VPS — never runs locally
ssh zubbyik@185.216.177.250

# Backend unit tests on VPS
cd /root/openagile/egbuna_estate_account_streamlight/estate-portfolio
docker compose exec backend pytest tests/unit/ -v

# Frontend unit tests on VPS
docker compose exec frontend npm test

# Full suite
docker compose exec backend pytest tests/ -v
```

**Branch rule**: All work on `test`. Never commits to `main` or `develop`.

**Current status** (2026-04-21 handover):
```
✅ Frontend: 5 test files, 21 tests passing (authStore, uiStore, useTheme, useCountUp, format)
✅ Backend: 3 test files, 12 tests passing (deps, auth_router, holdings_router)
⏳ Pending: Navbar, Sidebar, HoldingsTable, DashboardKPICard component tests
⏳ Pending: Integration tests (blocked on Antigravity building missing backend modules)
⏳ Pending: E2E Playwright tests (blocked on staging being stable)
```

**Must not**:
- Merge to `main` or `develop`
- Write new production features
- Modify `app/` source files (test files only)
- Execute any code on local Fedora workstation

---

## Handover Protocol (All Agents Must Follow)

Every handover document must include:

```markdown
**From**: [Agent name + role]
**To**: [Agent name + role]
**Date**: YYYY-MM-DD
**Protocol**: MASTER_CONTEXT.md v4.0

1. What was done (specific files changed, commands run, tests executed)
2. What is currently working (exact verification results with numbers)
3. What is broken / drifting (specific issue + root cause if known)
4. What the receiving agent must do next (explicit numbered action list)
5. Blockers (what cannot proceed until resolved)
```

---

## Current EPM Phase 2 — Agent Status

| Agent | Status | Immediate Next Action |
|-------|--------|----------------------|
| Claude | ✅ STLC written, architecture docs complete | Await Antigravity Phase 2B migration + Codex integration test results |
| Grok | ✅ Capabilities verified, chain confirmed | Verify python-frontmatter library + Obsidian YAML quirks for Phase 2B |
| Antigravity | 🔴 Must complete vault sync setup + missing backend modules | 1. Vault sync one-time setup (8 tasks above). 2. Build app/services/portfolio.py + missing routers |
| Lovable | ✅ Core shell + Dashboard + Holdings done | Build remaining 14 stub pages in next Lovable session |
| Codex | ✅ 33 tests passing on test branch | Migrate component tests (Navbar, Sidebar, HoldingsTable, KPICard) when Antigravity builds missing modules |

---

**END OF AGENT DELEGATION REGISTRY v3.0**
**Next update**: After Antigravity completes Phase 2B backend modules and vault sync setup
