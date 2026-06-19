---
type: CTX
id: DEEPSEEK_CONTEXT
title: Minimal Context for DeepSeek Implementer
version: 1.0
date: 2026-05-22
purpose: Single source of truth for DeepSeek to implement changes without hallucinating
---

# DeepSeek Context — OpenAgile Project

## 1. Hard Rules (NEVER Violate)

These rules are non-negotiable. Any violation will break the production system.

### 1.1 Deployment Law (NON-NEGOTIABLE)
- ALL deployments go through GitHub Actions → Netcup VPS.
- NEVER suggest running Docker commands on local Fedora laptop.
- NEVER suggest direct SSH to server for deployments.
- NEVER suggest scp or manual file transfers.

**Correct pattern:**
```
git commit → git push → GitHub Actions auto-deploys
```

### 1.2 Infrastructure Constraints
- **Network**: `openagile_network` (external bridge). For external stacks, declare `external: true` and use `openagile_openagile_network`.
- **Traefik**: 
  - Entrypoints: `websecure` (port 443)
  - Certresolver: `cloudflare` (NOT `letsencrypt`)
  - Labels must include exact pattern:
    ```yaml
    traefik.enable=true
    traefik.http.routers.SERVICE.rule=Host(`SUBDOMAIN.zubbystudio.shop`)
    traefik.http.routers.SERVICE.entrypoints=websecure
    traefik.http.routers.SERVICE.tls=true
    traefik.http.routers.SERVICE.tls.certresolver=cloudflare
    traefik.http.services.SERVICE.loadbalancer.server.port=PORT
    traefik.docker.network=openagile_network
    ```
- **Database**: Shared PostgreSQL 15 container `postgres` on `openagile_network`. NEVER create a new Postgres container. Reuse existing.
- **Redis**: Check if existing instance available before adding new one.
- **Volume Strategy**: 
  - Named volumes preferred for app data, Frappe assets.
  - Bind mounts only for configs, backups, scripts.
  - Frappe assets: MUST use named volumes (bind mounts cause symlink issues).

### 1.3 Frappe-Specific Rules
- **Python environment**: Always use bench venv: `/home/frappe/frappe-bench/env/bin/pip`
- **Custom app install**: 
  ```bash
  docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app_name>
  docker compose exec backend bench build   # After pip install
  ```
- **Apps in sites/apps.txt**: ALL must be pip-installed in bench venv.
- **Frontend**: `edu_theme` uses Vue.js 3 + Vite; builds into `edu_theme/public/frontend/`.

### 1.4 Frontend Stack Priority
1. **React** — preferred for SPAs, data-heavy dashboards.
2. **Vue.js** — only when project requires it (Frappe `edu_theme`) or explicitly specified.
3. **Vanilla JavaScript** — for lightweight interactions.

### 1.5 General Code Style
- **Python**: Line length 110, tabs indentation, double quotes, ruff linting.
- **JavaScript/Vue**: ESLint with specific globals, `no-console: warn`.
- **Shell scripts**: `shfmt -w`, `shellcheck -x`.

---

## 2. Infrastructure Contract (Compact)

### Networks
- Main: `openagile_network` (bridge, external: true for secondary stacks)
- Traefik listens on this network.

### Services Overview
| Service | Subdomain | Port | Notes |
|---------|-----------|------|-------|
| Traefik | traefik.zubbystudio.shop | 443 | Reverse proxy, SSL termination |
| PostgreSQL | (internal) | 5432 | Shared, no direct exposure |
| Frappe/ERPNext | erpnext.zubbystudio.shop | 8080 | Custom apps: education, library_management, edu_theme |
| Estate Portfolio | estate.zubbystudio.shop | 8501 | Streamlit app |
| OpenProject | project.zubbystudio.shop | 8080 | Project management |
| n8n | n8n.zubbystudio.shop | 5678 | Automation |
| Wiki.js | docs.zubbystudio.shop | 3000 | Documentation |
| Gitea | git.zubbystudio.shop | 3000 | Git hosting |
| Grafana | metrics.zubbystudio.shop | 3000 | Monitoring |

### GitHub Actions Deploy Template
```yaml
name: Deploy to VPS
on:
  push:
    branches: [main]
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

---

## 3. Active Sub-Projects

| Directory | Purpose | Tech Stack | Status |
|-----------|---------|------------|--------|
| `/` (root) | Infrastructure orchestration | Docker Compose, Traefik, PostgreSQL | Active |
| `frappe_docker/` | Main Frappe/ERPNext setup | Frappe, ERPNext, Vue.js, Python | Active |
| `frappe_docker_edu/` | Education-focused Frappe | Similar to main, education focus | Active |
| `frappe_docker_local/` | Local development Frappe | Local testing | Development |
| `egbuna_estate_account_streamlight/` | Estate portfolio Streamlit app | Streamlit, Python, Obsidian integration | Active |
| `wireguard/` | WireGuard VPN | Docker, wg-easy | Active |
| `ghost_website/` | Ghost CMS blog | Headless Ghost, React frontend | Planned |
| `thrive-tech-hub/` | Recover project | Various | Recovery |

---

## 4. Agent Roles

| Agent | Role | Code Authority | Output Format |
|-------|------|---------------|---------------|
| **Claude** | Architect, documentation, reasoning | ❌ None in repo — advises only | Plans, briefs, analysis |
| **Antigravity** | Primary implementer — sole code author in repo | ✅ Full — reads, writes, executes | Files, configs, scripts |
| **DeepSeek** | Secondary implementer (NEW) | ✅ Via Antigravity review — code suggestions | Code snippets, SEARCH/REPLACE blocks |
| **Codex** | Peer reviewer only — never an implementer | ❌ None — read-only | Git diff style suggestions |

**DeepSeek Integration Model:**
- DeepSeek receives minimal context (this file + specific task + file paths).
- DeepSeek outputs code changes in SEARCH/REPLACE format.
- Antigravity reviews and applies changes.
- All changes go through GitHub Actions deployment.

---

## 5. Task Template for DeepSeek

When assigning a task to DeepSeek, use this template:

```markdown
# Task for DeepSeek

## Context
- Relevant files (list paths):
  - `path/to/file1.py`
  - `path/to/file2.yaml`
- Constraint reminders:
  - certresolver: cloudflare
  - network: openagile_network
  - deployment: GitHub Actions only

## Task Description
[Exact description of what needs to be changed or implemented]

## Input Files
[If DeepSeek needs to read files, list them here. Antigravity must provide the file contents.]

## Expected Output
Return ONLY the code changes in this format:

FILE: path/to/file
------- SEARCH
[exact lines to find]
=======
[new lines to replace with]
+++++++ REPLACE

If multiple changes, use multiple blocks.

## Verification
After applying, verify with:
1. [command to test]
2. [expected output]
```

---

## 6. Anti-Hallucination Checklist (Mandatory for DeepSeek)

Before outputting any code, DeepSeek must confirm:

- [ ] I have searched the codebase for existing patterns (or Antigravity provided search results).
- [ ] I referenced only existing APIs, functions, and file paths.
- [ ] I used `cloudflare` as certresolver (not `letsencrypt`).
- [ ] I used `openagile_network` (or `openagile_openagile_network` for external stacks).
- [ ] I did NOT create a new Postgres container.
- [ ] I did NOT suggest local Docker commands.
- [ ] I did NOT invent file paths or API endpoints.
- [ ] I stated [UNKNOWN] for anything not in provided files.
- [ ] My output is in SEARCH/REPLACE format (if code change) or exact code (if new file).

---

## 7. Files to Archive (Redundant After This File)

The following files contain overlapping information and should be moved to `docs/archive/` after `DEEPSEEK_CONTEXT.md` is adopted:

1. `MASTER_CONTEXT.md` — replaced by sections 1-2 above.
2. `GEMINI.md` — replaced by this file (note: MASTER_CONTEXT says GEMINI.md is absorbed).
3. `INFRASTRUCTURE_CONTRACT.md` — replaced by section 2.
4. `AGENTS.md` — agent roles summarized in section 4.
5. `agents/BUILDER_AGENT.md` — builder rules condensed in section 1.
6. `agents/INVESTIGATOR_AGENT.md` — investigator rules not needed for DeepSeek.
7. `agents/ORCHESTRATOR_AGENT.md` — orchestrator rules not needed for DeepSeek.
8. `skills/INDEX.md` — skills summarized in section 4.
9. `ORCHESTRATOR_MISSION.md` — historical context, keep for reference but not in active context.
10. `RECOVERY_PLAN.md` — specific to a past recovery, archive.

**Action for Antigravity:** After `DEEPSEEK_CONTEXT.md` is committed and pushed, create `docs/archive/` and move the above files there. Update `.gitignore` if needed.

---

## 8. Verification for This File

| Step | Command | Expected Output |
|------|---------|----------------|
| File exists | `ls -la DEEPSEEK_CONTEXT.md` | file present |
| Valid YAML frontmatter | `head -n 10 DEEPSEEK_CONTEXT.md` | type: CTX, etc. |
| No broken links | (manual check) | all referenced paths exist |

---

**End of DEEPSEEK_CONTEXT.md**

**Instructions for Antigravity:**
1. Commit this file to `test` branch.
2. Communicate to the user the list of files to archive (section 7).
3. When assigning tasks to DeepSeek, use the template in section 5.
4. Always provide DeepSeek with only this file + the specific files needed for the task (to respect its smaller context window).