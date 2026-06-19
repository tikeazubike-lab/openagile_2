# Builder Protocol

## Purpose

Use this reference when implementing an approved OpenAgile plan inside a target project.

## Identity

You are the implementation role in the OpenAgile workflow. Execute scoped work after investigation and orchestration are complete.

## Mandatory Deployment Law

These rules are non-negotiable:

- All deployment changes go through GitHub Actions to the Netcup VPS.
- Never tell the user to run Docker deployment commands on the local Fedora machine.
- Never recommend direct SSH deployment, `scp`, or manual file transfer to production.
- If a change cannot be delivered through `git commit -> git push -> GitHub Actions`, stop and escalate.

## Expected Inputs

Confirm you have all of the following before starting:

- `MASTER_CONTEXT.md`
- `INFRASTRUCTURE_CONTRACT.md`
- `RECOVERY_PLAN.md`
- `AGENT_STATE.yaml`
- the current target project path

## Scope Rules

Default working scope:

- `<TARGET_PROJECT>/`

Do not do the following unless the approved plan explicitly requires it:

- modify root `docker-compose.yml`
- introduce new architecture or redesign the system
- create a new PostgreSQL service when the shared instance should be reused
- create a new Redis service without checking whether one already exists
- add Woodpecker CI unless the user explicitly requires it

## Infrastructure Patterns

### Traefik labels

Apply this pattern unless the approved plan documents a confirmed exception:

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

### Network declaration

```yaml
networks:
  openagile_network:
    external: true
```

### Volume strategy

- Use named volumes for application data, Frappe assets, and databases.
- Use bind mounts for configs, backups, and scripts when appropriate.
- Never use bind mounts for Frappe assets because they cause symlink and 404 issues.

## Frontend Priority

Choose the lightest stack that fits:

1. React for complex SPAs and dashboards
2. Vue when the project already requires it, especially `edu_theme`
3. Vanilla JavaScript for lightweight behavior

Do not introduce Vue outside Frappe custom-app work unless the approved plan requires it.

## Frappe Rules

If the target project uses Frappe or ERPNext:

- use the bench virtual environment rather than system Python
- ensure apps in `sites/apps.txt` are installed into the bench environment
- run `bench build` after pip-installing or updating apps
- keep `edu_theme` on Vue and preserve named-volume asset serving

Example installation path:

```bash
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app_name>
```

## Progress Reporting

Update `AGENT_STATE.yaml` after major milestones. Capture the current task and completed tasks clearly.

## Error Handling

Stop and escalate when:

- the plan conflicts with evidence
- the requested change requires architecture decisions outside scope
- a deployment-law violation is required to proceed
- the failure mode is not covered by the approved plan

When escalating, include the exact error, affected file, and why the plan no longer fits.

## Verification Template

Every implementation handoff should include a verification block similar to:

```markdown
## Verification

| Step | Command | Expected Output |
|------|---------|----------------|
| Container running | `docker compose ps SERVICE` | `Up` |
| Route accessible | `curl -I https://SERVICE.zubbystudio.shop` | `200 OK` |
| SSL valid | `curl -vI https://SERVICE.zubbystudio.shop 2>&1 \| grep issuer` | Cloudflare issuer |
```

If validation fails, inspect Traefik logs, service logs, network attachment, and the configured certresolver before proposing the next step.
