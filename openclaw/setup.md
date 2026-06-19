# OpenClaw Setup Guide

Safe sandbox deployment of OpenClaw on the production VPS using the official Docker image.

> **Architecture**: OpenClaw runs as an integrated component within the `openagile` repository CI/CD flow. The `docker-compose.yml` natively implements Traefik routing and network isolation. 

---

## Deployment Strategy

OpenClaw is deployed exactly like the other stack components (e.g., WireGuard, Estate Portfolio) via GitHub Actions.

The deployment relies on:
1. The **`ghcr.io/openclaw/openclaw:latest`** pre-built image (skips the 2GB local build requirement).
2. The **`.github/workflows/deploy-openclaw.yml`** CI/CD pipeline.

---

## How to Deploy / Update

1. Push any changes inside the `openclaw/` directory to the `main` branch.
2. The GitHub Action `Deploy OpenClaw` will trigger automatically.
3. The pipeline will:
   - SSH into the VPS
   - Pull the latest code (`git pull`)
   - Write the `.env` file securely
   - Run `docker compose pull` and `docker compose up -d`
   - Run a health check against the gateway.

> **Manual Trigger**: You can also trigger the deployment manually by going to **GitHub → Actions → "Deploy OpenClaw Gateway" → Run workflow**.

---

## Required GitHub Secret

The GitHub Actions workflow requires the `SSH_PRIVATE_KEY` secret.
Since this project already deploys other services via SSH, **this secret is already configured and no action is needed.**

---

## Post-Deployment Initialization (Crucial)

Because this pipeline intentionally bypasses the local `docker-setup.sh` wizard to run natively inside GitHub Actions, the OpenClaw database starts completely unconfigured.

**To initialize the agent, pair your CLI, select a model, and link Telegram:**
SSH into the server and run the interactive onboarding wizard:
```bash
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/openclaw
docker compose run --rm -it openclaw-cli onboard
```
*Note: This command is interactive. Follow the prompts to configure your API keys (e.g., ZAI_API_KEY), select your default model, and pair chat channels (Telegram, Discord, etc).*

---

## Accessing OpenClaw

Once deployed and onboarded, Traefik automatically exposes the UI:

- **URL:** [https://openclaw.zubbystudio.shop](https://openclaw.zubbystudio.shop)
- **Token:** The gateway token is securely injected during deployment. Check the `.env` file on the server (`OPENCLAW_GATEWAY_TOKEN`) and paste it into the **Settings -> "Auth Token"** field inside the Control UI.

---

## Troubleshooting Remote Pairing

If you encounter a `"pairing required"` or `"unauthorized: gateway token mismatch"` loop when accessing via Traefik:
1. Ensure the Github Action successfully wrote `trustedProxies` into `openclaw.json`.
2. Grab the Token from the `.env` file and paste it directly into the web UI settings.
3. If changing models via CLI fails, always rely on the interactive menus (`onboard`, `configure`, or `tui`) instead of manually editing the JSON structure, as the config schema changes frequently between versions.

---

## Cleanup

To completely remove the installation from the VPS (run directly on the server):

```bash
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/openclaw
docker compose down -v
docker volume rm openclaw_home
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Deployment pipeline fails | Check the GitHub Actions logs. Most likely an SSH connectivity blip. |
| Bad Gateway (502) | Traefik cannot reach the container. Ensure `openclaw-gateway` is running (`docker compose ps`) and attached to `openagile_openagile_network`. |
| Health check failing | Check logs: `docker compose logs -f openclaw-gateway` |

---

## References

- [Official Docs — Docker Install](https://docs.openclaw.ai/install/docker)
- [Infrastructure Contract](../INFRASTRUCTURE_CONTRACT.md) — Traefik and network rules for this VPS
