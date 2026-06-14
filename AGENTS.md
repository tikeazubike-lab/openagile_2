# AGENTS.md — Essential Guidance for OpenCode Sessions

## Critical Rules (Never Miss These)

### 0. First-Contact Context Discovery
- Start at the workspace root `AGENTS.md` for global OpenAgile rules.
- Then identify the target subproject before editing files.
- Target project triggers, in priority order:
  1. Explicit project name in the user prompt.
  2. File paths mentioned in the user prompt.
  3. Active/open IDE file path supplied in context.
  4. A handover, acceptance test, or context file that names a project.
- If no target project can be identified, ask the user to name the project.
- Project-local context engines live under each subproject's `docs/context/`
  directory when available.
- For Estate Portfolio Manager, read:
  - `egbuna_estate_account_streamlight/estate-portfolio/docs/context/MASTER_CONTEXT.md`
  - `egbuna_estate_account_streamlight/estate-portfolio/docs/context/WORKFLOW.md`
  - `egbuna_estate_account_streamlight/estate-portfolio/docs/context/DELEGATION_REGISTRY.md`
  - `egbuna_estate_account_streamlight/estate-portfolio/docs/context/AGENT_STATE.yaml`
- Once a target project is resolved, edits are limited to that project path and
  explicitly authorized root coordination docs. Do not edit another subproject
  unless the user explicitly expands the scope.
- If project-local context conflicts with this file, this root `AGENTS.md`
  controls global infrastructure rules, while the subproject context controls
  local file ownership, current handovers, and implementation sequencing.
- Documentation structure must follow `docs/DOCUMENTATION_STRUCTURE.md` at the
  root and the matching structure inside each subproject `docs/` directory.

### 1. Branch Discipline
- **Always work on `test` branch** — never commit directly to `main`
- Create/switch to `test` before starting work: `git checkout test` or `git switch -c test`
- Only approved maintainers merge `test` → `main`

### 2. Docker Usage (GitHub Actions Only)
- **NEVER run Docker commands locally** (on Fedora laptop)
- All deployment must go through GitHub Actions:
  - Push changes to GitHub → Actions deploys to Netcup VPS
  - Local machine: Git ops, code editing, local testing only

### 3. Frappe Development Conventions (Applies only to frappe_docker* folders)
- Use bench venv Python: `/home/frappe/frappe-bench/env/bin/pip`
- Install custom apps: `docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app>`
- After pip install: Run `bench build` to generate assets
- Assets use named volumes (NOT bind mounts) to avoid symlink issues
- **Important**: These conventions ONLY apply to frappe_docker* directories. Do not use them in other project folders.

### 4. Testing Requirements
- **Single test**: `pytest tests/test_frappe_docker.py::test_endpoints -s`
- Follow BDD/TDD pipeline: Write pytest from Gherkin, see Red, then write production code to pass (Green)
- Trace assertions back to spec: `# Spec: feature_name.feature | SC-001 | Then...`
- **Verification format**: ALL solutions must include:
  ```markdown
  ## Verification Steps
  
  1. **Test Command**: [exact command to test]
  2. **Expected Output**: [what success looks like]
  3. **If It Fails**: [diagnostic steps]
  4. **Rollback**: [how to undo if broken]
  ```

### 5. Service-Specific Commands

#### Root Infrastructure
```bash
docker compose up -d          # Start stack (via GitHub Actions only)
docker compose ps             # Check status
docker compose logs -f [svc]  # View logs
```

#### frappe_docker (Main Frappe Setup)
```bash
./scripts/deploy.sh                              # Deploy multi-tenant
docker compose exec backend bench new-site [name] --admin-password=admin
```

#### edu_theme Frontend (Vue.js + Vite)
```bash
cd frappe_docker/apps/edu_theme/frontend
npm run dev       # Development server
npm run build     # Build for production (outputs to ../edu_theme/public/frontend/)
```

#### Estate Portfolio (Streamlit)
```bash
cd egbuna_estate_account_streamlight/estate-portfolio
pip install -r requirements.txt
streamlit run app.py    # Or: docker compose up -d via GitHub Actions
```

### 6. Key Constraints to Remember
- Shared PostgreSQL 15 — never create new container, reuse existing
- All services on `openagile_network` with Traefik labels for routing
- Low-resource server (<4GB RAM per service) — avoid memory-heavy tools
- Documentation must use standard YAML headers in `docs/` directory
- Pre-commit hooks: Install in `apps/edu_theme` for Python/JS formatting
- **Traefik labels**: When adding services, use the standard label convention
- **Volume strategy**: Use named volumes for Frappe assets (bind mounts cause symlink issues)
