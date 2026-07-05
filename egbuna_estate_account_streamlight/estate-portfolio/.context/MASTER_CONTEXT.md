# MASTER_CONTEXT.md — Single Source of Truth

**DO NOT EDIT WITHOUT HANDOVER PROTOCOL**

**Version**: 4.0
**Last Updated**: April 25, 2026
**Maintained By**: Master Prompt Framework

---

## CHANGELOG v3.0 → v4.0

| Section | Change |
|---------|--------|
| Local Machine rules | Extended: no Python, Node, or any code execution locally — not just Docker |
| CI/CD Pipeline | Added fast-path / full-path split. Added vault-sync workflow. Added SSH heredoc rule. |
| Active Services | EPM Phase 2 (FastAPI+React) added. Streamlit marked as deprecated/legacy. |
| Historical Log | New entries: zero-load workflow, CI Option B resolution, Obsidian vault sync architecture |
| Failed Approaches | Added: epm-tests gitignore conflict, unquoted ENDSSH |
| Agent Chain | Added Codex (Tester) and Lovable (UI Generator) to tool strengths |
| Obsidian Vault | New section: vault-to-PostgreSQL sync architecture |

---

## Current Infrastructure Contract

### Stack Overview
```yaml
Base Platform: Docker Compose
Reverse Proxy: Traefik v2.10
Database: PostgreSQL 15 (shared, REUSE existing)
Network: openagile_network (external bridge)
Domain Pattern: *.zubbystudio.shop

Server Specs:
  OS: Ubuntu 24.04 LTS
  CPU: 8 vCPU
  RAM: 16GB
  Disk: 500GB SSD
  Location: Netcup VPS

Local Development:
  OS: Fedora Linux 42 (Workstation Edition)
  Hostname: fedora (laptop)
  Hardware: Dell Latitude E6540
  HARD CONSTRAINT: Resource-limited. Kernel OOM crashes on local code execution.
  RULE: Local machine does ONLY: git operations + code editing. Nothing else.
  Editors: Neovim, Cursor (Antigravity/GPT), Antigravity (Gemini Pro CLI)
```

### Active Services
```yaml
Core Services:
  - traefik (routing, SSL)
  - postgres (shared database)
  - prometheus (metrics collection)
  - grafana (visualization)

Production Apps:
  - frappe/erpnext (business ops)
    * Site: edu.erpnext.zubbystudio.shop
    * Bench venv: /home/frappe/frappe-bench/env
    * Volume strategy: Named volumes for apps
    * Custom apps: library_management, education, edu_theme
    * Frontend: edu_theme uses Vue.js 3 + Vite
    * API: Custom whitelisted endpoints (edu_theme.api.*)
  - openproject (project management)
  - n8n (automation)
  - wiki.js (documentation)
  - gitea (version control)
  - woodpecker (CI/CD)
  - registry (container images)
  - estate-portfolio-v1 (Streamlit — LEGACY/DEPRECATED)
    * URL: https://estate.zubbystudio.shop (will be cut over to v2)
    * Status: Running but being replaced by EPM Phase 2
  - estate-portfolio-v2 (EPM — FastAPI + React — ACTIVE DEVELOPMENT)
    * Staging URL: https://demo.estate.zubbystudio.shop
    * Production URL: https://estate.zubbystudio.shop (post-cutover)
    * Stack: FastAPI + SQLAlchemy + React 18 + TanStack Router + Tailwind v4
    * Auth: JWT httpOnly cookie, users table in shared Postgres
    * Container: Single container (FastAPI serves React static files)

Networking:
  - All services on openagile_network
  - Traefik labels for routing
  - HTTPS via Let's Encrypt
  - Internal DNS via container names
```

### Key Constraints
```yaml
DO NOT (Local Workstation — Fedora):
  - Run Docker commands (compose up/down/build/exec)
  - Run Python scripts or pip install
  - Run npm install or npm run anything
  - Run pytest, vitest, or any test runner
  - SSH directly to server for deployments
  - Execute ANY code that could load RAM/CPU

DO NOT (Server / Infrastructure):
  - Create new Postgres container (one exists, reuse it)
  - Create new Redis (check first if needed)
  - Bypass Traefik (all HTTP/HTTPS through it)
  - Use bind mounts for Frappe assets (symlink issues)
  - Install packages in system Python (use bench venv)
  - Use unquoted heredoc in GitHub Actions SSH scripts (see CI/CD section)

ALWAYS (Local Workstation):
  - Only: git add, git commit, git push, git pull
  - Only: Edit files in Neovim, Cursor, or Antigravity
  - Only: Read logs in browser (GitHub Actions UI, Grafana)

ALWAYS (Infrastructure):
  - Check existing services before adding new ones
  - Use openagile_network for inter-service communication
  - Follow Traefik label convention
  - Backup before infrastructure changes
  - Document decisions in this file
  - Deploy via GitHub Actions (NEVER local Docker)
  - Use bench venv for Frappe app installs
  - Use quoted heredoc in SSH scripts: << 'ENDSSH' (not << ENDSSH)
```

### Traefik Label Convention
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.SERVICE.rule=Host(`SUBDOMAIN.zubbystudio.shop`)"
  - "traefik.http.routers.SERVICE.entrypoints=websecure"
  - "traefik.http.routers.SERVICE.tls=true"
  - "traefik.http.routers.SERVICE.tls.certresolver=letsencrypt"
  - "traefik.http.services.SERVICE.loadbalancer.server.port=PORT"
  - "traefik.docker.network=openagile_network"
```

### Volume Strategy
```yaml
Named Volumes (preferred):
  - openproject_data
  - postgres_data
  - grafana_data
  - estate_data

Bind Mounts (only when necessary):
  - Config files: ./configs/service/
  - Backups: ./backups/
  - Scripts: ./scripts/

Frappe-Specific:
  - Assets: Named volumes (NOT bind mounts)
  - Custom apps: Mounted at /home/frappe/frappe-bench/apps/
  - Bench venv: /home/frappe/frappe-bench/env (use this Python)
  - Sites: ./sites (bind mount for persistence)

EPM-Specific:
  - Obsidian vault mirror: ~/ObsidianVaultMirror:/vault:ro
    (read-only bind mount into backend container for import_obsidian.py)
```

---

## CI/CD Pipeline: GitHub Actions (NON-NEGOTIABLE)

### The Fundamental Rule

```
Local machine: EDIT + COMMIT + PUSH only.
Everything else (test, build, deploy) runs on GitHub Actions or VPS.
This is not a preference — it is a hard constraint due to local RAM/CPU limits.
```

### What Happens on git push

```
git push origin <branch>
       │
       ▼
GitHub Actions fires ci.yml
       │
       ├── FAST PATH (feature/**, develop branches):
       │     Stage 0: Static analysis (ruff, eslint, actionlint)  < 2 min
       │     Stage 3: Build Docker image                          < 8 min
       │     Stage 4: Deploy to demo.estate.zubbystudio.shop      < 3 min
       │     → You get staging URL to check in browser. Done.
       │
       └── FULL PATH (main, test branches, nightly 02:00 WAT, workflow_dispatch):
             Stage 0: Static analysis
             Stage 1: Unit tests (pytest + vitest)                < 5 min
             Stage 2: Integration + contract + DB tests           < 10 min
             Stage 3: Build Docker image
             Stage 4: Deploy to staging
             Stage 5: E2E + Playwright + Locust + Accessibility   < 15 min
             → Blocks production deploy if any stage fails
```

### Branch Strategy

```
feature/xyz → develop → test → main
    ↑             ↑        ↑      ↑
  Edit here    Fast CI   Full   Manual
  locally      path      CI +   approval
                         Codex  + prod
                         tests  deploy
```

### SSH Heredoc Rule (CRITICAL — ALWAYS QUOTE)

```yaml
# ❌ WRONG — variables interpolate on the GitHub runner (wrong machine)
script: |
  ssh user@host << ENDSSH
    cd /path && docker compose up -d
  ENDSSH

# ✅ CORRECT — single-quoted, variables evaluate on REMOTE server
script: |
  ssh user@host << 'ENDSSH'
    cd /path && docker compose up -d
  ENDSSH

# When using appleboy/ssh-action, the `script:` field handles this automatically.
# Only applies when writing raw SSH heredocs in shell steps.
```

### GitHub Actions Secrets Required

```
VPS_HOST          — Netcup VPS IP (185.216.177.250)
VPS_USER          — zubbyik
VPS_SSH_KEY       — Private SSH key for VPS
JWT_SECRET        — EPM JWT signing secret
DB_HOST           — openagile_postgres (container name)
DB_NAME           — estate_portfolio
DB_USER           — openagile
DB_PASSWORD       — shared Postgres password
DB_PORT           — 5432
DB_TEST_SCHEMA    — estate_portfolio_test
ADMIN_USERNAME    — EPM admin username
ADMIN_PASSWORD    — EPM admin password (bcrypt hashed by seed_admin.py)
E2E_ADMIN_USER    — Playwright test admin username
E2E_ADMIN_PASS    — Playwright test admin password
E2E_VIEWER_USER   — Playwright readonly username
E2E_VIEWER_PASS   — Playwright readonly password
SNYK_TOKEN        — Snyk security scan token
VAULT_REPO_DEPLOY_KEY — SSH key for VPS to pull private vault repo
```

### Test Isolation Strategy

```
Integration + DB tests use a SEPARATE TEST SCHEMA on shared Postgres:
  Schema: estate_portfolio_test
  Created: by CI job before tests run
  Torn down: by CI job after tests finish (even on failure)
  Pattern: BEGIN SAVEPOINT → test → ROLLBACK (zero side effects)

This replaces the previous Option B (epm-tests gitignored) approach.
Tests now LIVE IN THE REPO and travel with code.
```

### Anti-Pattern: What AI Must NEVER Suggest

```
❌ "Run this on your machine: docker compose up -d"
❌ "Run this on your machine: pip install -r requirements.txt"
❌ "Run this on your machine: npm install"
❌ "Run this on your machine: pytest"
❌ "SSH into the server and run: docker compose restart"
❌ "Copy files to server with scp"
❌ "Use << ENDSSH (unquoted) in GitHub Actions"

✅ "Commit this change and push to develop — Actions will deploy to staging"
✅ "Push to test branch — Codex will run the full suite on the server"
✅ "Trigger workflow_dispatch from GitHub UI for immediate full pipeline run"
✅ "SSH to VPS to verify if needed: ssh zubbyik@185.216.177.250"
```

---

## Obsidian Vault → PostgreSQL Sync Architecture

### Overview

```
Obsidian Vault (local, ~/ObsidianVault/NigerianStocks)
    │
    │  git commit + git push (markdown only — no code execution)
    ▼
Private GitHub Repo (obsidian-nigerian-stocks-private)
    │
    │  GitHub Actions vault-sync.yml triggers
    ▼
Netcup VPS: git pull → ~/ObsidianVaultMirror
    │
    │  docker compose exec backend python scripts/import_obsidian.py
    ▼
estate_portfolio PostgreSQL (shared openagile_postgres)
```

### Sync Rules (Locked)

```
First run:   Full seed — all 85 companies + holdings + dividends
Re-runs:     INSERT new records only. Existing tickers are SKIPPED.
             Web app edits are NEVER overwritten by vault sync.
Conflict:    Web app wins after first import.
Trigger:     Manual — user pushes vault changes to private repo.
             GitHub Actions fires vault-sync.yml automatically on push.
```

### Holdings Classification from Vault

```
Obsidian status field → PostgreSQL holding_type

  "listed"    → holding_type = 'active'   (active investment)
  "merged"    → holding_type = 'active'   (may have successor claims)
  "delisted"  → holding_type = 'claim'    (cost_basis_override = 0)
  "defunct"   → holding_type = 'claim'    (cost_basis_override = 0)
  "uncertain" → holding_type = 'claim'    (cost_basis_override = 0)
```

### UI Layout (Holdings Page)

```
Table 1: Active Portfolio (holding_type = 'active')
  Shows: Ticker, Company, Sector, Shares, Avg Cost, Curr Price,
         Curr Value, Cost Basis, return[%], Div Yield, Status
  Subtotal: sum of current_value for live holdings

Table 2: Claims Portfolio (holding_type = 'claim')
  Shows: Ticker, Company, Sector, Shares, Status, Claim Authority,
         Claim Status, Expected Payout, Actual Payout
  Note: return[%] column ABSENT (null for claims)
  Subtotal: sum of actual_payout (paid) or expected_payout (pending)

Grand Total Row: Active value + Claims value = Total Assets (₦)
```

---

## Historical Decision Log

### Major Architectural Decisions

**2026-04-25: Zero-Load Local Workflow**
- **Why**: Fedora workstation causes kernel OOM crashes when running Python/Node locally
- **Solution**: Local machine does only git operations + editing. All execution on GitHub Actions or VPS.
- **Impact**: No local testing, no local builds, no local Docker. CI fast-path deploys to staging on every push.
- **Lesson**: Local resource constraints are a hard architectural constraint, not a preference.

**2026-04-25: Obsidian Vault Git-Based Sync**
- **Why**: Vault is local-only; VPS needs data; running import script locally crashes workstation
- **Solution**: Vault → private GitHub repo → VPS pulls → import_obsidian.py runs on VPS
- **Impact**: Vault sync requires one git push from local (markdown only — negligible resources)
- **Lesson**: Route all compute through the server, not the workstation.

**2026-04-24: CI Test Isolation via Separate Schema (Reinstatement)**
- **Why**: Option B (epm-tests gitignored) broke CI — tests must be in repo for Actions to run them
- **Solution**: Tests reinstated in repo. Integration tests use `estate_portfolio_test` schema.
  Schema created and torn down by CI job. No new container. No production data risk.
- **Impact**: Tests travel with code. Full CI pyramid restored.
- **Lesson**: Gitignoring tests to reduce PR noise is an anti-pattern — it breaks CI.

**2026-04-21: EPM Phase 2 — FastAPI + React (Single Container)**
- **Why**: Streamlit app had no auth, no edit UI, EODHD scraper broken (402)
- **Solution**: Full rebuild — FastAPI REST API + React 18 + TypeScript + TanStack Router + Tailwind v4
- **Impact**: Single container serves both API and React static files. Auth via JWT httpOnly cookie.
- **Lesson**: Streamlit is a prototype tool; FastAPI+React for production-grade apps.

**2026-04-20: EPM Auth — bcrypt==4.0.1 Pin**
- **Why**: passlib==1.7.4 crashes with bcrypt>=4.1.0 (dummy test > 72 bytes raises ValueError)
- **Solution**: Hard-pinned bcrypt==4.0.1 in requirements.txt
- **Impact**: seed_admin.py works correctly. Admin user seeded successfully.
- **Lesson**: Always pin bcrypt version when using passlib. Check pip-audit on every dependency update.

**2026-04-20: EPM Logout Bug Fix**
- **Why**: Sidebar clearUser() wiped Zustand state without calling POST /api/v1/auth/logout
- **Solution**: TanStack React Query useLogout() mutation hits backend first, then clearUser(), then navigate()
- **Impact**: httpOnly cookie correctly cleared on logout. Back button cannot restore dashboard.
- **Lesson**: Frontend state clear ≠ session termination. Always hit backend logout endpoint first.

**2026-04-18: Theme System — System Default + Dark Override**
- **Why**: User needs dark mode support; both desktop and mobile usage
- **Solution**: Three states: system (default) / dark (forced) / system (restored). Anti-FOUC script in <head>.
- **Impact**: Theme persists across refresh via localStorage('epm-theme'). Visible to all roles.

**2026-04-15: EPM Phase 2B — Obsidian Vault → PostgreSQL Migration**
- **Why**: 85 NGX stocks tracked in Obsidian; need structured DB for web app
- **Solution**: import_obsidian.py parses YAML frontmatter. INSERT new records only on re-run.
  All 85 stocks imported: listed/merged → holding_type='active'; delisted/defunct → holding_type='claim'
  ClaimRecord table for AMCON/CAC reference tracking. Dual Holdings table UI.
- **Impact**: Web app becomes permanent source of truth. Vault used for ongoing data entry.

**2026-04-12: EPM Phase 2 — Lovable.dev Frontend Generation**
- **Why**: Accelerate React UI build; Lovable generates production-quality React from prompts
- **Caveat**: Lovable defaults to Supabase; must be overridden in every prompt
- **Solution**: Frontend-only role for Lovable. Antigravity reviews all PRs for Supabase contamination.
- **Impact**: TanStack Start used instead of plain Vite React. TanStack Router (file-based routing).

**2026-03-28: Migrated Nginx → Traefik**
- **Why**: Automatic SSL, better Docker integration
- **Impact**: All services now use Traefik labels
- **Lesson**: Always check Traefik routing before debugging

**2026-03-15: Shared PostgreSQL Strategy**
- **Why**: Resource efficiency (<4GB RAM available per service)
- **Impact**: New services MUST check if Postgres exists
- **Lesson**: "Just spin up another X" anti-pattern caused issues

**2025-12-22: Frappe Asset Rebuilding Strategy**
- **Why**: Assets 404/MIME errors after deployment
- **Solution**: `bench build` after pip installing custom apps
- **Lesson**: Missing apps in Python env break bench build, even if unused

### Failed Approaches (Learn from These)

**Attempt: Unquoted ENDSSH heredoc in GitHub Actions**
- **Result**: Variables (docker compose paths, env vars) interpolated on GitHub runner instead of VPS
- **Fix**: Always quote the heredoc delimiter: `<< 'ENDSSH'`
- **Lesson**: Unquoted heredoc = variables resolve locally. Quoted heredoc = variables resolve remotely.

**Attempt: Gitignoring epm-tests/ to reduce PR noise (Option B)**
- **Result**: GitHub Actions cannot run tests that don't exist in the repo. CI becomes decoration.
- **Fix**: Tests back in repo. Isolation via separate test schema, not file exclusion.
- **Lesson**: CI requires tests to travel with code. Reduce PR noise differently (GitHub Actions path filters).

**Attempt: Running pip install / pytest on local Fedora workstation**
- **Result**: Kernel OOM crash — workstation cannot handle Python package installation + execution
- **Fix**: All code execution on GitHub Actions runners or VPS via SSH
- **Lesson**: Fedora laptop is an editing terminal only. Not a dev server.

**Attempt: Frappe bench build without pip install**
- **Result**: ModuleNotFoundError for custom apps
- **Fix**: docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app>
- **Lesson**: MUST use bench venv, not system Python

**Attempt: Using faster-whisper on CPU-only server**
- **Result**: Out of memory (OOM) crashes
- **Fix**: Use whisper.cpp with small model instead
- **Lesson**: Server is low-resource, PEP 668 enforced

---

## Frontend Technology Preferences

**EPM Project (current)**:
- React 18 + TypeScript + Vite + TanStack Router (file-based, src/routes/)
- Tailwind v4 with oklch colour tokens (not arbitrary CSS variable syntax)
- shadcn/ui component pattern (copy-paste, not installed as package dependency)
- TanStack Query v5 for server state, Zustand for UI state
- TanStack Table v8 for all data tables

**Other Projects (priority order)**:
1. Vanilla JavaScript (preferred for simple interactions)
2. React (for complex state management)
3. Vue.js (only when project requires it, e.g., Frappe custom apps)

---

## Master Prompt Framework (Embedded)

### Framework Version
**Version**: 3.0 (with Zone 1/Zone 2 + ToT integration)

### Quick Reference: 8 Core Principles

1. **Mandatory Infrastructure Context Block** — Always check what's running
2. **Constraint-First Framing** — State what must NOT break
3. **Output Schema Guards** — Specify exact format
4. **Self-Critique Trigger** — Check assumptions, flag [VERIFY THIS]
5. **Explicit Refinement Gate** — Stop after output, offer 3 next steps
6. **Handover Protocol** — Forensic analysis before cross-agent changes
7. **Zone-Aware Delegation** — Zone 1 automate, Zone 2 add friction
8. **Learn-It-All Mindset** — 4-level ladder for deep learning

### 20 Hard Rules (Summary)

**Infrastructure** (1-6):
1. Never guess paths — mark [VERIFY THIS]
2. Never create new service without checking if exists
3. Always show working directory before shell commands
4. Specify which Docker container for exec
5. No hallucinated version numbers
6. Frappe: Always use bench venv path

**Technical** (7-12):
7. Assume technical competence
8. Complete, not simplified
9. Include WHY, not just HOW
10. Systematic debugging over quick fixes
11. Don't ask permission for obvious tool use
12. Default: Ubuntu 24.04 + Bash (server), Fedora 42 (local — NO EXECUTION of any kind)

**Quality** (13-16):
13. Never invent attributions
14. Always provide file paths
15. Show BEFORE/AFTER for config changes
16. Diagnostic commands first for troubleshooting

**Handover** (17-18):
17. When receiving code: ask what was tried, why chosen, bugs fixed
18. When creating code: include decision log, limitations, dependencies

**Zone-Aware** (19-20):
19. Zone 1: DRAG framework. Zone 2: AI as spotter
20. Default to Zone 2 unless explicitly Zone 1

### Top 6 NEVER Rules (Always Enforce)

```
❌ 1. Context-blind generics
❌ 2. "Just spin up another X" reflex
❌ 3. Incomplete code ("# ... rest here")
❌ 4. Tutorial preamble
❌ 5. Placeholder hell (YOUR_API_KEY)
❌ 6. Orphaned code without handover brief
```

---

## Zone Classification Rules

### Default: Zone 2 (Add Friction)

**Auto-Switch to Zone 1 IF**:
- Keywords: format, generate, draft, boilerplate, "just give me"
- Task is mechanical (formatting, standard configs)
- Similar task exists in historical context
- User explicitly requests automation

**Force Zone 2 IF**:
- Keywords: architect, design, why, understand, critique, learn
- No similar precedent in historical context
- Architectural decision required
- Questions about tradeoffs or "best approach"

---

## Recommended Workflow by Task Type

**Zone 1 Tasks** (Implementation):
```
Antigravity (execute) → Claude (review + document) → Done
```

**Zone 2 Tasks** (Architecture):
```
Claude (design + ToT) → Grok (verify + current info) → Antigravity (implement)
```

**UI Generation**:
```
Claude (wireframe + Lovable prompt) → Lovable (React code → GitHub PR)
→ Antigravity (review PR, strip Supabase, wire build, deploy)
```

**Testing**:
```
Claude (STLC spec) → Codex (migrate + execute on test branch, SSH to VPS)
→ Codex handover → Claude (review drift) → Antigravity (fix backend gaps)
```

**Debugging**:
```
Antigravity (diagnose via SSH to VPS) → Claude (root cause analysis)
→ Grok (check if known issue) → Antigravity (fix + push)
```

**Handover**:
```
ANY TOOL → GENERATE HANDOVER BRIEF → Next tool → HANDOVER INTAKE
```

**Tool Strengths**:
- **Antigravity**: File system access, multi-file edits, FastAPI/Docker/GitHub Actions
- **Claude**: Deep reasoning, architecture, documentation, STLC, handover specs
- **Grok**: Up-to-date info, library version verification, tool capability audits
- **Lovable**: React 18 + TypeScript + Tailwind v4 UI code generation from prompts
- **Codex**: Test suite execution, codebase investigation, drift analysis (test branch only)

---

## Project-Specific Memories

### Frappe/ERPNext (OpenAgile Project)

**Custom App Installation Rule**:
```bash
# ALWAYS use bench venv for editable installs
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app_name>
# NEVER use system pip (installs to wrong Python)
```

**Current Apps**: education, library_management, edu_theme (Vue.js 3 + Vite)

### EPM — Estate Portfolio Manager Phase 2

**Current backend flat layout** (Codex-confirmed, 2026-04-21):
```
backend/app/
  config.py    — settings (from env vars)
  database.py  — async engine + get_session (NOT get_db)
  deps.py      — JWT logic: create_access_token(user_id, role), verify_password, hash_password
  main.py      — FastAPI factory + StaticFiles mount + SPA catch-all route
  models.py    — ALL SQLAlchemy models (flat, single file)
  routers/
    auth.py       — login, logout, me, change-password
    dashboard.py  — dashboard KPIs
    holdings.py   — holdings CRUD
backend/scripts/
  seed_admin.py — reads ADMIN_USERNAME + ADMIN_PASSWORD env vars
                  MUST be idempotent (skip if user exists)
```

**EPM function name contract**:
- `create_access_token(user_id: int, role: str)` — NOT `create_access_token(data={})`
- `get_session` — NOT `get_db`
- `verify_password`, `hash_password` — both in `app/deps.py`

**bcrypt pin**: `bcrypt==4.0.1` — DO NOT upgrade. passlib 1.7.4 incompatible with bcrypt >= 4.1.0.

**Missing backend modules** (Antigravity must build — Phase 2B):
- `app/services/portfolio.py` (business logic)
- `app/schemas/` package (Pydantic schemas)
- Routers: companies, prices, dividends, transactions, registrars,
  watchlist, nav_history, rebalancing, corporate_actions, obsidian, claims

### Server Resource Constraints

**Low-Resource Local (Fedora workstation)**:
- Kernel OOM on Python package install or code execution
- git push only — no execution of any kind

**VPS Resources** (Netcup — use freely for execution):
- 8 vCPU, 16GB RAM, 500GB SSD
- All tests, builds, and imports run here

---

## Emergency Protocols

### Production Outage
```
1. Check Historical Decision Log for last change
2. Review GitHub Actions logs (browser — no local execution needed)
3. SSH to VPS: ssh zubbyik@185.216.177.250
4. docker compose logs epm_v2 --tail=100
5. Rollback: git revert + push to main → Actions redeploys
```

### Lost Context (Fresh Agent Session)
```
1. Provide this file to agent
2. Agent reads Infrastructure Contract + Historical Log
3. Agent asks clarifying questions about current task
4. Proceed with full context
```

---

**END OF MASTER_CONTEXT.md**

**Version Control**: Commit with message format: "MASTER_CONTEXT: [change description]"
**Sync Locations**:
- Antigravity: ~/.gemini/GEMINI.md
- Claude: OpenAgile Master Project
- Grok: Memory Project
- Notion: Backup/reference
