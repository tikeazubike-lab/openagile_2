# Repository Guidelines

## Project Structure & Module Organization
This repository is a focused WireGuard deployment module for the OpenAgile stack.

- `docker-compose.yml`: Primary service definition for `wg-easy`, Traefik labels, and external Docker network wiring.
- `deploy.sh`: Deployment entrypoint used for pull/restart flow and UFW allowance for `51820/udp`.
- `.env`: Runtime configuration (for example `WG_HOST`, `WG_PASSWORD_HASH`); treat as environment-specific and sensitive.
- `data/`: Persistent WireGuard state mounted to `/etc/wireguard` in the container.
- `GEMINI.md`: Operational runbook and architecture notes.

## Build, Test, and Development Commands
Use these commands from this directory:

- `docker compose config`: Validate Compose syntax and interpolated config.
- `docker compose pull`: Fetch the pinned `wg-easy` image.
- `docker compose up -d --remove-orphans`: Start or reconcile the running service.
- `docker compose logs -f wg-easy`: Follow runtime logs for troubleshooting.
- `bash deploy.sh`: Standard deployment path (creates `data/`, checks UFW rule, redeploys).

## Coding Style & Naming Conventions
- Shell scripts: Bash with `set -e`; prefer small, idempotent steps and clear `echo` status lines.
- YAML: 2-space indentation, lowercase keys, and quoted label values when they contain special characters.
- Naming: use descriptive, kebab-case file names and concise service/container names aligned with Docker Compose.
- Keep secrets out of committed files; reference environment variables through `.env`.

## Testing Guidelines
There is no dedicated unit-test framework in this module. Validate changes with:

1. `docker compose config` (syntax and env interpolation)
2. `docker compose up -d` (service boots cleanly)
3. `docker compose ps` and `docker compose logs --tail=100 wg-easy` (health and startup checks)
4. Optional smoke test: open the configured host (for example `https://vpn.zubbystudio.shop`) and confirm UI availability.

## Commit & Pull Request Guidelines
Follow the existing commit style seen in history: Conventional Commits such as `feat: ...`, `fix: ...`, `docs: ...`, optionally scoped (`fix(deploy): ...`).

For PRs:
- Explain what changed and why.
- Link related issue/ticket when available.
- Include validation evidence (commands run, relevant log snippets, or screenshots for UI/access changes).
- Call out infra-impacting edits explicitly (ports, network, firewall, secrets, image tags).
