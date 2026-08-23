---
type: HO
id: HO-123
title: OpenCode → Claude: F-TD-001 Teardown Investigation Complete — nginx Is Dead Weight
date: 2026-08-13
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-123 — F-TD-001 Teardown Investigation Results

## 1. Traefik rules for testbuild (raw)

### On `estate_portfolio_v3` container:
```
traefik.http.routers.epm-v3-testbuild-api.rule: Host(`testbuild.zubbystudio.shop`) && PathPrefix(`/api`)
traefik.http.routers.epm-v3-testbuild-api.entrypoints: websecure
traefik.http.routers.epm-v3-testbuild-api.tls: true
traefik.http.routers.epm-v3-testbuild-api.tls.certresolver: cloudflare
```

### On `testbuild-checklist` (nginx) container:
```
traefik.http.routers.testbuild.rule: Host(`testbuild.zubbystudio.shop`) && !PathPrefix(`/api`)
traefik.http.routers.testbuild.entrypoints: websecure
traefik.http.routers.testbuild.priority: 10
traefik.http.routers.testbuild.tls: true
traefik.http.routers.testbuild.tls.certresolver: cloudflare
traefik.http.routers.testbuild-http.rule: Host(`testbuild.zubbystudio.shop`)
traefik.http.routers.testbuild-http.entrypoints: web
traefik.http.routers.testbuild-http.middlewares: testbuild-redirect
traefik.http.middlewares.testbuild-redirect.redirectscheme.scheme: https
traefik.http.services.testbuild.loadbalancer.server.port: 80
```

**No `.site` rules exist for testbuild.** MASTER_CONTEXT.md was wrong —
testbuild was never migrated from `.shop` to `.site`.

---

## 2. Reachability (raw)

```bash
curl -sI --connect-timeout 5 https://testbuild.zubbystudio.shop/
# Exit: 35 (SSL connection error — .shop expired, permanently dead)

curl -sI --connect-timeout 5 https://testbuild.zubbystudio.site/
# Exit: 35 (no Traefik rule exists for .site, SSL fails)
```

**Both domains are unreachable.** The `.shop` rule is pointing at nothing.

---

## 3. Nginx container analysis

### Container: `testbuild-checklist` (nginx:alpine, running 5 weeks)

### Config: completely default nginx
```
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }
}
```

No custom checklist page. No API reverse proxy. No anything — just the
default nginx Docker image serving static files.

### Volume mount:
```
/home/zubbyik/.../backend/app/static/checklist → /usr/share/nginx/html (ro)
```

The nginx container serves the same `index.html` that the backend now
serves at `/api/v1/checklist/test-checklist`.

### Compose file: `docker-compose.testbuild.yml`
- Single service: `nginx` (image: nginx:alpine)
- Mounts `backend/app/static/checklist` read-only
- Traefik labels for `testbuild.zubbystudio.shop`

---

## 4. What nginx does today

**Nothing useful.** The nginx container:
- Serves the same static checklist HTML that the backend now serves
- Has no custom config (default nginx)
- Has no API reverse proxy (Traefik handles `/api` routing separately)
- Is unreachable via both `.shop` (expired) and `.site` (no rule)

The checklist page moved to a real backend route (`/api/v1/checklist/test-checklist`) as of HO-121. The nginx layer is **purely dead weight**.

---

## 5. Proposed teardown plan

### What to remove:

1. **Stop and remove the nginx container:**
   ```bash
   docker compose -f docker-compose.testbuild.yml down
   ```

2. **Remove Traefik labels from `estate_portfolio_v3`:**
   - `traefik.http.routers.epm-v3-testbuild-api.*` (4 labels)
   - These route `/api` on `testbuild.zubbystudio.shop` to the backend —
     but `.shop` is dead, so this rule is already pointing at nothing

3. **Archive the compose file:**
   ```bash
   mv docker-compose.testbuild.yml docker-compose.testbuild.yml.archived
   ```

### What NOT to remove:
- `testdrive.epm.zubbystudio.site` routing — entirely unaffected
  (separate router: `epm-v3`, no testbuild dependency)
- The `_v3` container itself — `testdrive` depends on it
- The checklist HTML file (`backend/app/static/checklist/index.html`) —
  still served by the backend at `/api/v1/checklist/test-checklist`

### Verification after teardown:
- `curl -sI https://testbuild.zubbystudio.shop/` → connection refused (already is)
- `curl -sI https://testdrive.epm.zubbystudio.site/` → 200 (unchanged)
- `curl -sI https://testdrive.epm.zubbystudio.site/api/v1/checklist/test-checklist` → 401 (unchanged)

### Risk: **None**
The nginx container is unreachable, serves dead content, and has no
dependents. Removing it is a pure cleanup with zero functional impact.
