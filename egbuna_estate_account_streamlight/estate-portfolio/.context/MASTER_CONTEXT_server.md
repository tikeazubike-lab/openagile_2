# MASTER_CONTEXT_server.md — VPS Direct Deploy Overlay

**Inherits**: All rules from `.context/MASTER_CONTEXT.md` unless explicitly overridden below.
**Applies when**: Agent session runs directly on the Netcup VPS (this session).
**Detection**: Working directory is `/home/zubbyik/openagile_2/...` on host `Linux (6.8.0-90-generic)`.

> **Session start rule**: If an agent is unsure which context to load, it must ask:
> "Are we on the **Server** (VPS direct deploy) or **Workstation** (CI/CD pipeline)?"

---

## Override: Execution Rules

| Rule | MASTER_CONTEXT.md (default) | MASTER_CONTEXT_server.md (override) |
|------|----------------------------|--------------------------------------|
| Docker commands | NEVER locally | ✅ YES — VPS IS the execution server |
| `docker compose build` | GitHub Actions only | ✅ YES — run directly |
| `docker compose up -d` | GitHub Actions only | ✅ YES — run directly |
| `npm install` | NEVER locally | ✅ YES — on VPS only |
| `npm run build` | NEVER locally | ✅ YES — on VPS only |
| `python3` / `pytest` | NEVER locally | ✅ YES — on VPS only |
| SSH to server | For verification only | ✅ YES — full operations |
| Git operations | Allowed | ✅ Allowed |

**Why this override exists**: The "Local machine = NO execution" rule targets the Fedora laptop (resource-limited, kernel OOM). The VPS is a full 8vCPU/16GB server explicitly designated for execution. The anti-pattern "SSH into the server and run: docker compose restart" only applies when the agent is ON the Fedora workstation; when the agent IS on the VPS, these operations are native.

---

## Override: Deployment Path

```
git push origin main
       │
       ▼
docker compose build  (direct on VPS, no GitHub Actions)
       │
       ▼
docker compose up -d  (direct on VPS)
       │
       ▼
Verify: curl / browser to testdrive.epm.zubbystudio.shop
```

**Fast deploy** (hotfixes, Phase 3C staging):
- Push to `main`, build, deploy directly, verify immediately
- No CI/CD pipeline, no review gate

**Production deploy** (when cutting over from testdrive):
- Still push to `main`, but must also verify the CI/CD pipeline if applicable
- Create HO-* handover documenting the cutover

---

## Server Environment

```yaml
Host: Linux 6.8.0-90-generic
IP: 185.216.177.250
User: zubbyik
Docker Compose File: docker-compose.v3.yml (EPM), docker-compose.yml (traefik)
Working Directory: /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/
Kernel Version: 6.8.0-90-generic

Staging URL: testdrive.epm.zubbystudio.shop
Production URL: estate.zubbystudio.shop (post-cutover)

Container: estate_portfolio_v3 (EPM)
Database: openagile_postgres (shared, external)
Network: openagile_openagile_network
```

---

## Override: Branch Strategy

```
feature/xyz → main → deploy directly on VPS
```

No `develop`, `test`, or intermediate branches needed for VPS-direct workflow.
The GitHub Actions pipeline and `/approve` gate are only enforced for Workstation (CI/CD) sessions.

**Exception for multi-agent workflows**: When Hermes delegates to OpenCode agents working in parallel, features may land on `main` in batches. Each batch should have a corresponding HO-* handover.

---

## Auth for Testing

```
Username: zubbyik
Password: a123456
```

(Production credentials differ — use ADMIN_USERNAME / ADMIN_PASSWORD env vars for production.)

---

## Override: Anti-Patterns That ARE Allowed on VPS

These are listed as anti-patterns in MASTER_CONTEXT.md but are legitimate here:

```
✅ "docker compose build && docker compose up -d"    — VPS native
✅ "pip install -r requirements.txt"                  — inside container or VPS venv
✅ "npm install && npm run build"                     — VPS native (pre-build server)
✅ "pytest backend/tests/"                            — inside container or VPS venv
```

---

**END OF MASTER_CONTEXT_server.md**
