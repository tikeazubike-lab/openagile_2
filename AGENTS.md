# AGENTS.md — OpenAgile Workspace Rules

## First Contact

1. **Consult @hermes** — Read `.hermes/references/AGENTS.md` (EPM project) or `hermes/` (root) for agent roles and delegation context. The Hermes AI agent (`hermes/docker-compose.yml`) is the primary entry point — ask it clarifying questions about roles, ownership, and current tasks before editing.
2. **Check AGENT_LOG.md** — Read the last 5 entries in `.hermes/references/AGENT_LOG.md` for recent cross-agent handoffs. Append a dated entry after any non-trivial work (what changed, why, what's next, <150 words).
3. Read root `MASTER_CONTEXT.md` for the full infrastructure contract, decisions, and deployment law.
4. Read `docs/PROJECT_CONTEXT_INDEX.md` to resolve the target subproject.
5. Read the subproject's `docs/context/` engine (MASTER_CONTEXT, WORKFLOW, DELEGATION_REGISTRY, AGENT_STATE).
6. Lock edits to the resolved project path unless scope expanded.

## Branch Discipline

- Always work on `test` branch. Never commit to `main`.
- `git checkout test` or `git switch -c test` before starting.
- Only approved maintainers merge `test → main`.

## Deployment Law

**This session runs on the Netcup VPS** — Docker commands are safe to run directly.
When working from the Fedora laptop (local checkout), deploy via `git push → Actions`.

**On Fedora laptop (NON-NEGOTIABLE):**
- NEVER run Docker commands locally
- Git ops, editing, local testing only
- No direct SSH, no scp, no manual file transfers

**On Netcup VPS (this environment):**
- `docker compose up -d`, logs, exec, build — all permitted
- Still prefer GitHub Actions for repeatable deploys

## Infrastructure Constraints

| Rule | Value |
|---|---|
| Network | `openagile_network` (external bridge); secondary stacks declare `external: true` |
| | External stacks see it as `openagile_openagile_network` (Docker project-name prefix) |
| Reverse proxy | Traefik v2.10 — certresolver **`cloudflare`** (not `letsencrypt`) |
| Database | Shared PostgreSQL 15 (`openagile_postgres`) — **NEVER create a new Postgres container** |
| Host ports 80/443 | Traefik only — no other service binds these |
| Domain | `*.zubbystudio.shop` |
| Volumes | Named volumes for data; bind mounts only for configs (`./configs/`), backups, scripts |
| Server RAM | <4GB per service — avoid memory-heavy tools |

### Traefik Label Template
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.SERVICE.rule=Host(`SUBDOMAIN.zubbystudio.shop`)"
  - "traefik.http.routers.SERVICE.entrypoints=websecure"
  - "traefik.http.routers.SERVICE.tls=true"
  - "traefik.http.routers.SERVICE.tls.certresolver=cloudflare"
  - "traefik.http.services.SERVICE.loadbalancer.server.port=PORT"
  - "traefik.docker.network=openagile_network"
```

## Multi-Agent Workflow

The workspace uses a 3-agent pipeline (`agents/`):
1. **Investigator** (Zone 2) → forensic analysis → `INFRASTRUCTURE_CONTRACT.md`
2. **Orchestrator** (Zone 2) → cross-check, zone classification, plan → `RECOVERY_PLAN.md`
3. **Builder** (Zone 1) → implement approved plan inside `<TARGET_PROJECT>/`

Zone 2 tasks require human confirmation before Builder executes.
See `AGENT_STATE.yaml` for live workflow state.
See `agents/ORCHESTRATOR_AGENT.md`, `INVESTIGATOR_AGENT.md`, `BUILDER_AGENT.md`.

## Subproject Delegation

| Project | Agents | Write Scope |
|---|---|---|
| Estate Portfolio (EPM) | DeepSeek v4 (read-only reviewer), Owl Alpha (backend), Nex N2 (frontend) | `egbuna_estate_account_streamlight/estate-portfolio/` |
| Frappe/ERPNext | (single agent) | `frappe_docker/` |

EPM sub-agent rules: `egbuna_estate_account_streamlight/estate-portfolio/docs/context/DELEGATION_REGISTRY.md`

## Frappe-Specific (directory: `frappe_docker*`)
- Python: bench venv only — `/home/frappe/frappe-bench/env/bin/pip`
- After pip install: run `bench build`
- Assets: named volumes only (bind mounts break symlinks)
- All apps in `sites/apps.txt` must be pip-installed in bench venv

## Frontend Stack Priority
React (preferred for complex UIs) → Vanilla JS → Vue.js (Frappe edu_theme only)

## Documentation Conventions
- All `docs/` files: YAML front matter with `type`, `id`, `title`, `status`, `version`, `updated`
- Structure per `docs/DOCUMENTATION_STRUCTURE.md` — mirror same shape in subproject `docs/`
- Archive superseded docs (don't delete)
- Every solution must include a **Verification Steps** block (command, expected output, rollback)

## Testing
- BDD/TDD flow: Gherkin specs (`*.feature` / `.md`) → pytest from spec (Red) → production code (Green)
- Trace assertions: `# Spec: feature_name.feature | SC-00X | Then...`
- Single test: `pytest tests/test_file.py::test_function -s`

## CI/CD & Infrastructure Gotchas

- **GH Actions SSH heredoc**: Always use single-quoted `<< 'ENDSSH'` delimiter so variables resolve on the remote server, not the runner.
- **Frontend builds**: Build React/SPA in GitHub Actions (`npm ci && npm run build`), copy into backend static dir, then build Docker image. Do not run npm on the VPS.
- **Traefik certresolver**: Running config uses `cloudflare`. Some docs still say `letsencrypt` — trust the actual `docker-compose.yml`, not stale docs.
- **DB init**: New databases are created by `scripts/init-databases.sh` via `POSTGRES_MULTIPLE_DATABASES` env var. Add new DBs there, not manually.
