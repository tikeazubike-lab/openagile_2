# Investigator Protocol

## Purpose

Use this reference when reconstructing the OpenAgile infrastructure contract for a target project.

## Operating Constraints

- Stay read-only.
- Do not modify files.
- Do not run state-changing commands.
- Label anything uncertain as `[INFERRED]` or `[UNKNOWN]`.

## Read Order

Read evidence in this order:

1. `MASTER_CONTEXT.md`
2. root `docker-compose.yml`
3. the target project directory
4. relevant `.github/workflows/deploy-*.yml`
5. `ORCHESTRATOR_MISSION.md` when history matters

## Evidence Checklist

### Networks

- Identify the expected shared network and any external network names.
- Check whether target stacks declare `external: true` where required.
- Confirm whether Traefik network labels match actual network names.

### Traefik

Look for these common labels:

```yaml
traefik.enable=true
traefik.http.routers.SERVICE.rule=Host(`SUBDOMAIN.zubbystudio.shop`)
traefik.http.routers.SERVICE.entrypoints=websecure
traefik.http.routers.SERVICE.tls=true
traefik.http.routers.SERVICE.tls.certresolver=cloudflare
traefik.http.services.SERVICE.loadbalancer.server.port=PORT
traefik.docker.network=openagile_network
```

Flag any confirmed deviation.

### Database and cache

- Check whether the shared PostgreSQL service is reused.
- Document naming conventions and credential flow.
- Check whether Redis is required and whether an existing instance already covers the need.

### CI/CD and deployment law

- Confirm deployment runs through GitHub Actions.
- Flag any instruction that suggests local Docker deployment, direct SSH deployment, or manual file transfer.
- Check for `appleboy/ssh-action@master` and expected VPS secrets where GitHub Actions deploys are present.

### Volumes

- Prefer named volumes for application data and Frappe assets.
- Treat bind-mounted Frappe assets as a breakage risk.

### Frappe-specific checks

For Frappe targets, inspect:

- `sites/apps.txt`
- bench environment usage
- `bench build` expectations
- custom app presence such as `education`, `library_management`, and `edu_theme`
- asset volume strategy

### Estate portfolio checks

For the Streamlit estate app, inspect any evidence related to:

- network attachment
- database schema constraints
- holdings edge cases
- Obsidian link parsing

## Required Output

Produce `INFRASTRUCTURE_CONTRACT.md` with these sections:

- source of truth
- networks
- Traefik
- database
- CI/CD
- volume strategy
- target-specific notes
- implicit rules
- uncertainties
- handover to Orchestrator

## Reporting Style

- Separate evidence from interpretation.
- Mark anything not directly confirmed.
- Highlight things that will break if violated.
- End with a concise handoff summary the Orchestrator can turn into a plan.
