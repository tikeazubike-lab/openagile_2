# MASTER_CONTEXT.md — Single Source of Truth

**DO NOT EDIT WITHOUT HANDOVER PROTOCOL**

**Version**: 3.0
**Last Updated**: March 30, 2026
**Maintained By**: Master Prompt Framework

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
  NOTE: NEVER run Docker commands here - use GitHub Actions
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
  - estate-portfolio (Streamlit app)
    * URL: https://estate.zubbystudio.shop
    * Purpose: Estate/investment portfolio tracking
    * Data: Obsidian vault integration

Networking:
  - All services on openagile_network
  - Traefik labels for routing
  - HTTPS via Let's Encrypt
  - Internal DNS via container names
```

### Key Constraints
```yaml
DO NOT:
  - Create new Postgres container (one exists, reuse it)
  - Create new Redis (check first if needed)
  - Bypass Traefik (all HTTP/HTTPS through it)
  - Use bind mounts for Frappe assets (symlink issues)
  - Install packages in system Python (use bench venv)
  - Run Docker commands on local Fedora laptop
  - SSH directly to server for deployments

ALWAYS:
  - Check existing services before adding new ones
  - Use openagile_network for inter-service communication
  - Follow Traefik label convention
  - Backup before infrastructure changes
  - Document decisions in this file
  - Deploy via GitHub Actions (NEVER local Docker)
  - Use bench venv for Frappe app installs
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
```

---

## Historical Decision Log

### Major Architectural Decisions

**2025-12-22: Frappe Asset Rebuilding Strategy**
- **Why**: Assets 404/MIME errors after deployment
- **Solution**: `bench build` after pip installing custom apps
- **Impact**: All apps in sites/apps.txt must be pip-installed in bench venv
- **Lesson**: Missing apps in Python env break bench build, even if unused

**2025-12: edu_theme Vue.js 3 + Vite Frontend**
- **Why**: Modern frontend for custom Frappe app
- **Solution**: Vue.js 3 with Vite build system
- **Impact**: Deployment script auto-installs via pip
- **Lesson**: Frontend assets served via direct volume mounts

**2025-12: Estate Portfolio Streamlit Integration**
- **Why**: Track Nigerian stock investments
- **Solution**: Streamlit app with Obsidian data import
- **Impact**: Database schema supports 20-char tickers
- **Lesson**: Handle zero-cost holdings and nested wiki links

**2026-03-28: Migrated Nginx → Traefik**
- **Why**: Automatic SSL, better Docker integration
- **Impact**: All services now use Traefik labels
- **Lesson**: Always check Traefik routing before debugging

**2026-03-15: Shared PostgreSQL Strategy**
- **Why**: Resource efficiency (<4GB RAM available per service)
- **Impact**: New services MUST check if Postgres exists
- **Lesson**: "Just spin up another X" anti-pattern caused issues

**2026-03-10: Frappe Bench Venv Discovery**
- **Why**: System pip installs didn't work for custom apps
- **Impact**: Always use /home/frappe/frappe-bench/env/bin/pip
- **Lesson**: Document environment-specific tooling paths

**2026-03-01: Named Volumes for Frappe Assets**
- **Why**: Bind mounts + symlinks = 404 errors
- **Impact**: Assets mounted as named volumes
- **Lesson**: Docker doesn't follow symlinks in bind mounts

### Failed Approaches (Learn from These)

**Attempt: Frappe bench build without pip install**
- **Result**: ModuleNotFoundError for custom apps
- **Fix**: docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app>
- **Lesson**: MUST use bench venv, not system Python

**Attempt: Using faster-whisper on CPU-only server**
- **Result**: Out of memory (OOM) crashes
- **Fix**: Use whisper.cpp with small model instead
- **Lesson**: Server is low-resource (<4GB RAM), PEP 668 enforced

**Attempt: Docker commands on local Fedora laptop**
- **Result**: Services deployed to wrong environment
- **Fix**: Mandatory GitHub Actions workflow
- **Lesson**: NEVER run Docker on local - always push to GitHub

---

## Frontend Technology Preferences

**Priority Order** (try in this sequence):
1. **Vanilla JavaScript** (preferred for simple interactions)
2. **React** (for complex state management)
3. **Vue.js** (only when project requires it, e.g., Frappe custom apps)

**Current Usage**:
- Vanilla JS: General web interactions, lightweight features
- React: Complex SPAs, data-heavy dashboards
- Vue.js: Frappe edu_theme, projects forcing Vue.js dependency

**Default Recommendation**: Start with Vanilla JS unless complexity requires React or project forces Vue.js

---

## CI/CD Pipeline: GitHub Actions (NON-NEGOTIABLE)

**CRITICAL RULE**: ALL deployment commands MUST go through GitHub Actions

**NEVER**: Run docker commands on local machine (Fedora laptop)

**ALWAYS**: Push to GitHub → Actions deploys to Netcup VPS

### Local Machine (Fedora 42)

**Allowed**:
- Git operations (commit, push, pull)
- Code editing
- Local testing (npm run dev, python manage.py runserver)
- Documentation

**FORBIDDEN**:
- docker compose up/down/build
- Direct SSH to server for deployments
- Manual file transfers to server
- Any production commands

### Deployment Flow (Mandatory)

```
Local Development (Fedora)
    ↓ git push
GitHub Repository
    ↓ triggers
GitHub Actions Workflow
    ↓ deploys to
Netcup VPS Server (Ubuntu 24.04)
```

### GitHub Actions Workflow Template

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Netcup VPS

on:
  push:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /root/openagile
            git pull origin main
            docker compose pull
            docker compose up -d
            docker compose ps
```

### Secrets Required

```
GitHub Repository → Settings → Secrets:
- VPS_HOST: Your Netcup VPS IP
- VPS_USER: root (or deployment user)
- VPS_SSH_KEY: Private SSH key for VPS
```

### Anti-Pattern: What AI Must NEVER Suggest

❌ "Run this on your machine: docker compose up -d"
❌ "SSH into the server and run: docker compose restart"
❌ "Copy files to server with scp"

✅ "Add this to docker-compose.yml, commit, push to GitHub"
✅ "GitHub Actions will deploy automatically on push to main"
✅ "To deploy now: git push or trigger workflow manually"

---

## SDLC & Documentation Governance

**CRITICAL RULE**: All projects MUST adhere to the EPM Governance & SDLC/STLC standards.

**Document Identity System**:
Every document (Requirement, Architecture, Test, Handover, Onboarding) MUST have a standardized YAML header block:
- `type`: BR | FR | ADR | TC | AT | HO | OB
- `id`: e.g., BR-005
- `title`, `status`, `version`, `owner`

**Folder Structure**:
All documentation must be stored in the `docs/` directory of the respective project:
- `docs/requirements/`
- `docs/architecture/`
- `docs/testing/` (with `test-plans/` and `acceptance-tests/`)
- `docs/handover/`
- `docs/onboarding/`

**Branch Strategy**:
- `main` is protected (production).
- All active development happens on `test`.
- Use conventional commits: `feat`, `fix`, `docs`, `test`, `chore`.

**BDD & TDD Testing Pipeline (Uncle Bob's Rule)**:
- Specifications are written in Gherkin (`.feature` or `.md`) by Claude.
- **Antigravity must write the tests** from the Gherkin spec using standard `pytest` with `httpx` (do NOT use `pytest-bdd`).
- **Tests must run and fail (Red)** to prove they test something.
- **Antigravity writes production code** to pass the tests (Green).
- Traceability is maintained via comments above assertions: `# Spec: feature_name.feature | SC-001 | Then...`
- Frontend tests (vitest) are written ONLY after API tests are green and endpoints are stable.

---

## Master Prompt Framework (Embedded)

### Framework Version
**Version**: 3.0 (with Zone 1/Zone 2 + ToT integration)
**Full Document**: See Notion "Master Prompt Framework - Complete Q&A"

### Quick Reference: 8 Core Principles

1. **Mandatory Infrastructure Context Block** - Always check what's running
2. **Constraint-First Framing** - State what must NOT break
3. **Output Schema Guards** - Specify exact format
4. **Self-Critique Trigger** - Check assumptions, flag [VERIFY THIS]
5. **Explicit Refinement Gate** - Stop after output, offer 3 next steps
6. **Handover Protocol** - Forensic analysis before cross-agent changes
7. **Zone-Aware Delegation** - Zone 1 automate, Zone 2 add friction
8. **Learn-It-All Mindset** - 4-level ladder for deep learning

### 20 Hard Rules (Summary)

**Infrastructure** (1-6):
1. Never guess paths—mark [VERIFY THIS]
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
12. Default: Ubuntu 24.04 + Bash (server), Fedora 42 (local - NO DOCKER)

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
- Learning mode requested
- Questions about tradeoffs or "best approach"

### Edge Case Resolution

**"Deploy X"**:
- Zone 1 IF: Similar deployment exists in historical context
- Zone 2 IF: New architecture or significant differences

**"Fix bug in Y"**:
- Zone 1 IF: Root cause clear, standard fix
- Zone 2 IF: Root cause unknown, requires investigation

---

## Infrastructure Context Responsibility

**For NEW projects** (e.g., "fairly used items webapp"):
1. AI asks clarifying questions about deployment target
2. User answers (Netcup VPS / local / cloud / etc.)
3. AI generates infrastructure context
4. User confirms/corrects
5. Context stored in MASTER_CONTEXT.md

**For EXISTING projects**:
1. User provides: docker-compose.yml, configs, or description
2. AI reconstructs infrastructure context
3. User confirms/corrects
4. Context stored in MASTER_CONTEXT.md

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

**Zone 2 Learning**:
```
Claude (4-level ladder) → Attempt yourself → Antigravity (implement) → Grok (verify)
```

**Debugging**:
```
Antigravity (diagnose with file access) → Claude (root cause analysis) → Grok (check if known issue) → Antigravity (fix)
```

**Handover**:
```
ANY TOOL → GENERATE HANDOVER BRIEF → Next tool → HANDOVER INTAKE
```

**Tool Strengths**:
- **Antigravity**: File system access, multi-file edits, execution
- **Claude**: Deep reasoning, architecture, documentation, learning
- **Grok**: Up-to-date info, current trends, quick verification

---

## Project-Specific Memories (Preserved from Original GEMINI.md)

### Frappe/ERPNext (OpenAgile Project)

**Custom App Installation Rule**:
```bash
# ALWAYS use bench venv for editable installs
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app_name>

# NEVER use system pip (installs to wrong Python)
```

**Asset Build Requirements**:
- ALL apps in `sites/apps.txt` must be pip-installed in bench venv
- Run `bench build` after installing apps to generate assets
- Missing apps break bench build even if not used by current site

**Current Apps**:
- education (ERPNext education module)
- library_management (custom app)
- edu_theme (Vue.js 3 + Vite frontend)

**edu_theme Deployment**:
- Frontend: Vue.js 3 with Vite build system
- API: Custom whitelisted endpoints (edu_theme.api.get_landing_page_data)
- Deployment: Script auto-installs via pip for persistence
- Assets: Served via volume mounts in `overrides/compose.frontend-custom-apps.yaml`

### Estate Portfolio Manager (Streamlit App)

**Database Schema**:
- Tickers: Support up to 20 characters
- Zero-cost holdings: Properly handled
- Nested wiki links: Parsed from Obsidian vault

**Access**:
- URL: https://estate.zubbystudio.shop
- Network: openagile_openagile_network
- DNS: Cloudflare

### Server Resource Constraints

**Low-Resource Environment**:
- CPU-only (no GPU)
- RAM: <4GB available per service
- PEP 668 enforced

**AI Model Limitations**:
- faster-whisper: Causes OOM crashes
- Solution: Use whisper.cpp with small model
- yt-dlp: Update via pip/pipx

---

## Verification Requirements

**ALL solutions must include**:

```markdown
## Verification Steps

1. **Test Command**: [exact command to test]
2. **Expected Output**: [what success looks like]
3. **If It Fails**: [diagnostic steps]
4. **Rollback**: [how to undo if broken]
```

---

## Maintenance Schedule

**Daily**: None (event-driven updates only)

**After Major Changes**:
- [ ] Update Infrastructure Contract
- [ ] Add to Historical Decision Log
- [ ] Increment version
- [ ] Sync to all tools (Claude, Grok)

**Monthly Review**:
- [ ] Archive deprecated decisions
- [ ] Update server specs if changed
- [ ] Verify all services still active
- [ ] Clean up Failed Approaches log

---

## Emergency Protocols

### Production Outage

```
1. Check last change in Historical Decision Log
2. Run diagnostic commands from verification sections
3. Check Grafana for metrics/alerts
4. Review container logs: docker compose logs SERVICE --tail=100
5. Rollback if needed (via GitHub Actions revert + push)
```

### Lost Context (Fresh Agent Session)

```
1. Provide this file to agent
2. Agent reads Infrastructure Contract + Historical Log
3. Agent asks clarifying questions about current task
4. Proceed with full context
```

---

**END OF MASTER_CONTEXT.md / GEMINI.md**

**File Maintainer**: Update this file after every major infrastructure change  
**Version Control**: Track in git with commit message format: "MASTER_CONTEXT: [change description]"  
**Sync Locations**: 
- Antigravity: ~/.gemini/GEMINI.md (this file)
- Claude: OpenAgile Master Project
- Grok: Memory Project
- Notion: Backup/reference
