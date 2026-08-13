# AGENTS.md — OpenAgile Workspace Rules

## First Contact

1. **Read `docs/PROJECT_CONTEXT_INDEX.md`** to resolve the target subproject.
2. Read that subproject's `docs/context/MASTER_CONTEXT.md` (or `.context/MASTER_CONTEXT.md` for EPM).
3. Read `docs/context/WORKFLOW.md`, `DELEGATION_REGISTRY.md`, and `AGENT_STATE.yaml`.
4. Read root `MASTER_CONTEXT.md` for full infrastructure contract.
5. Lock edits to the resolved project path unless scope explicitly expanded.

## Branch Discipline

- Always work on `test` branch. Never commit to `main`.
- `git checkout test` or `git switch -c test` before starting.
- Only approved maintainers merge `test → main`.

## Deployment Law

**No GitHub Actions workflows exist yet** — `.github/workflows/` is empty.
CI/CD is design-only. Actual deployments happen via direct VPS execution.

**On Fedora laptop (NON-NEGOTIABLE — when workstation is online):**
- NEVER run Docker commands locally
- Git ops, editing, local testing only
- No direct SSH, no scp, no manual file transfers

**On Netcup VPS (this environment):**
- `docker compose up -d`, logs, exec, build — all permitted
- Direct VPS execution is the current deployment method

## Infrastructure Constraints

| Rule | Value |
|---|---|
| Network | `openagile_network` (external bridge); secondary stacks declare `external: true` |
| | External stacks see it as `openagile_openagile_network` (Docker project-name prefix) |
| Reverse proxy | Traefik v2.10 — certresolver **`cloudflare`** (not `letsencrypt`) |
| Database | Shared PostgreSQL 15 (`openagile_postgres`) — **NEVER create a new Postgres container** |
| Host ports 80/443 | Traefik only — no other service binds these |
| Domain (EPM) | `*.zubbystudio.site` (migrated from `.shop` — other services still on `.shop`, deprioritized) |
| Domain (infra) | `*.zubbystudio.shop` (n8n, gitea, wiki.js, openproject, woodpecker, frappe) |
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
| Estate Portfolio (EPM) | Claude Web (architect), DeepSeek Pro (reviewer), OpenCode deepseek-flash (builder), Kimi (frontend escalation) | `egbuna_estate_account_streamlight/estate-portfolio/` |
| Frappe/ERPNext | (single agent) | `frappe_docker/` |
| Thrive Tech Hub | Frontend Agent / Backend Agent (split) | `thrive-tech-hub/` |
| WireGuard | (single agent) | `wireguard/` |

EPM sub-agent rules: `egbuna_estate_account_streamlight/estate-portfolio/.context/MASTER_CONTEXT.md`

## EPM-Specific (directory: `egbuna_estate_account_streamlight/estate-portfolio/`)

**Canonical context**: `.context/MASTER_CONTEXT.md` (v4.8+, maintained by Claude Web). This file wins over all other EPM docs.

**Spec-first rule (absolute)**: Never write implementation code without a Claude-authored `F-NNN` feature spec and corresponding `AT-NNN` acceptance test. If neither exists, stop and report back.

**HO numbering**: Never self-assign. Pull next number from `MASTER_CONTEXT.md` "Pre-assigned HO numbers" table.

**Merge gate (Gate 2 — live, enforced)**: `feature/* → PR → Zubbyik's explicit approval → merge`. No direct pushes to `main`. GitHub branch protection + CODEOWNERS (`@zubbyik`). Read-access approvals do NOT satisfy the rule — approving account must have Write access.

**Locked decisions (do not revisit without Zone 2 consensus)**:
- `bcrypt==4.0.1` pinned (passlib incompatibility)
- JWT in httpOnly cookies, 30-day max_age
- Admin routes at `/settings/*`, never `/admin/*`
- `ADMIN_ROLES = {"admin", "superadmin"}` in `app/deps.py`
- All CRUD editing is modal-based (no inline row editing — HO-023/040)
- Monetary API values always returned as JSON strings
- Migrations: additive only (`ADD COLUMN IF NOT EXISTS`), never destructive
- `lifecycle_status` is the single source of truth for claim UI state
- `epm_test` is a real, separate database on shared PostgreSQL (not a schema)
- Baseline migration: `000_baseline_production_schema.py` — chain reproducible from empty

**Build / Test commands**:
| Action | Working Directory | Command |
|--------|-------------------|---------|
| Frontend build | `estate-portfolio-manager/` | `npm run build` |
| Frontend tests | `estate-portfolio-manager/` | `npm run test` (vitest) |
| Backend tests | `backend/` | `python -m pytest` |
| Backend migrations | `backend/` | `alembic upgrade head` |
| Full test suite | project root | `python -m pytest` (166 passed, 4 xfailed, 8 xpassed) |
| Prod deploy | project root | `docker compose -f docker-compose.v3.yml up -d --build epm` |

**Test naming**: `DOMAIN-WORKFLOW-LAYER-TYPE-NNN` — see `MASTER_CONTEXT.md` → "Test Taxonomy".

**Tech stack**: FastAPI + SQLAlchemy async + Alembic (backend), React 18 + TypeScript + Tailwind v4 + TanStack Router/Table + Recharts (frontend).

**Temporary state (as of 2026-07-08)**: Fedora laptop crashed. Direct VPS execution temporarily permitted. Code still committed to GitHub.

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
- EPM: `epm_test` is a real database on shared PostgreSQL — integration tests run against it directly

## CI/CD & Infrastructure Gotchas

- **No GitHub Actions workflows exist** — `.github/workflows/` is empty. CI/CD is design-only. Deploy via direct VPS execution.
- **GH Actions SSH heredoc** (when implemented): Always use single-quoted `<< 'ENDSSH'` delimiter so variables resolve on the remote server, not the runner.
- **Frontend builds**: Build React/SPA in GitHub Actions (`npm ci && npm run build`), copy into backend static dir, then build Docker image. Do not run npm on the VPS.
- **Traefik certresolver**: Running config uses `cloudflare`. Some docs still say `letsencrypt` — trust the actual `docker-compose.yml`, not stale docs.
- **DB init**: New databases are created by `scripts/init-databases.sh` via `POSTGRES_MULTIPLE_DATABASES` env var. Add new DBs there, not manually.
- **Network naming**: Root stack's `openagile_network` becomes `openagile_openagile_network` when referenced from secondary stacks (Docker project-name prefix).
- **EPM domain**: Migrated to `*.zubbystudio.site`. Other services still on `*.zubbystudio.shop` (deprioritized, do not treat as urgent).
- **Gate 2 is real**: GitHub branch protection on `main` is live and enforced. Gate 1 (CI checks) is design-only.
