# Infrastructure Contract

## Networks
- **Main Internal Network**: `openagile_network` (bridge network defined in the root `docker-compose.yml`).
- **External Network Name**: `openagile_openagile_network` (this is the actual Docker network on the host that external services MUST connect to via `external: true`).
- **Public/Traefik Exposure**: Services must be attached to the `openagile_network` (or `openagile_openagile_network` for external stacks) to be routed by Traefik.
- Explicit Traefik network label is sometimes required for external stacks: `traefik.docker.network=openagile_openagile_network`.

## Traefik
- **Entrypoints**: The standard secure entrypoint is `websecure` (port 443).
- **Certificate Resolver**: Let's Encrypt with Cloudflare DNS challenge -> `cloudflare`.
- **Labels Required for Exposure**:
  - `traefik.enable=true`
  - `traefik.http.routers.<service>.rule=Host('<subdomain>.zubbystudio.shop')`
  - `traefik.http.routers.<service>.entrypoints=websecure`
  - `traefik.http.routers.<service>.tls=true`
  - `traefik.http.routers.<service>.tls.certresolver=cloudflare`
  - `traefik.http.services.<service>.loadbalancer.server.port=<port>` (often required)
- **Security Middlewares**: Most main-stack services use `security-headers@file`. Frappe uses local middleware configs.

## Database
- **Shared PostgreSQL Container**: `openagile_postgres` running `postgres:15-alpine`.
- **Internal Hostname**: `postgres` (on `openagile_network`).
- **Default Database User**: `openagile` (override via `POSTGRES_USER`).
- **Connection Details**: Password passed via `.env` (`POSTGRES_PASSWORD`). Databases are created dynamically on start using `init-databases.sh` and comma-separated env var `POSTGRES_MULTIPLE_DATABASES`.

## Implicit Rules
- **Network Name Match**: The network name declared in Traefik labels (`traefik.docker.network`) MUST exactly match the network name of the Docker Compose stack if the host has multiple networks.
- **External Network Declaration**: Secondary stacks (like `frappe_docker`) MUST declare the Traefik network as `external: true` with the name `openagile_openagile_network`.
- **Host Matching Services**: Docker container names and service names shouldn't conflict with main stack components (`postgres`, `traefik`, `n8n`, etc.).
- **VPS Port Constraints**: No service should bind directly to host ports `80` or `443` except Traefik.
- **Opt-in Exposing**: Traefik runs with `exposedByDefault=false` (inferred from label usage). You MUST use `traefik.enable=true` to expose anything.
