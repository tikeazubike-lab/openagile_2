# F-TD-001 — Testbuilder Teardown + Standalone Checklist on testbuild

> **For Hermes:** Execute this plan task-by-task using subagent-driven-development.

**Goal:** Tear down the abandoned `docker-compose.test-builder.yml` service (port 8000, SQLite). Deploy a standalone Nginx container serving the existing checklist HTML at `testbuild.zubbystudio.shop`. API persistence still works via Traefik path-routing to the EPM backend.

**Architecture:**

```
testbuild.zubbystudio.shop
         │
    ┌────┴────┐  Traefik (path-based routing)
    │         │
    ▼         ▼
  Nginx     EPM (estate_portfolio_v3)
 (static)   (/api/v1/checklist/runs)
    │
    └── / → index.html (checklist page)
```

- Browser loads static HTML from Nginx (fast, no Python overhead)
- JS fetch to `/api/v1/checklist/runs` → Traefik sees `PathPrefix(/api)` + `Host(testbuild...)` → routes to EPM container (same port 8000)
- Login at `testbuild.zubbystudio.shop/api/v1/auth/login` → EPM auth → cookie set for testbuild domain
- Everything same-origin from browser's perspective — no CORS issues, cookies work

**Tech Stack:** Docker Compose, nginx:alpine, FastAPI (EPM backend), Traefik v2

---

## Context Audit — Verified State

| Item | Value |
|------|-------|
| Old testbuilder container | Up 6 days, port 8000 behind old testbuild labels |
| Old compose file | `docker-compose.test-builder.yml` (1420 bytes) |
| Old SQLite volume | `estate-portfolio_test_builder_data` |
| Checklist HTML location | `backend/app/static/checklist/index.html` (384 lines) |
| Checklist JS API calls | Relative `/api/v1/checklist/runs` (POST on save, GET on load) |
| EPM API router | `backend/app/routers/checklist.py` with `require_admin` guard |
| EPM CORS | `ALLOWED_ORIGINS=https://testdrive.epm.zubbystudio.shop` |
| EPM compose file | `docker-compose.v3.yml` using `cloudflare` certresolver |
| DNS | `testbuild.zubbystudio.shop` A record resolves to VPS IP |
| Traefik network | `openagile_openagile_network` (external) |

---

## Step-by-Step Plan

### Task 1: Create Standalone Nginx Compose File

**Objective:** Create `docker-compose.testbuild.yml` with an Alpine Nginx container serving the checklist HTML on port 80, plus API path routing labels.

**Files:**
- Create: `docker-compose.testbuild.yml`

**Step 1: Write the compose file.**

```yaml
# ═══════════════════════════════════════════════════════════════════════════════
# F-TD-001 — Standalone Test Checklist Tool
#
# Serves static checklist HTML at testbuild.zubbystudio.shop.
# API calls (/api/v1/checklist/runs, /api/v1/auth/login) are routed via Traefik
# to the EPM backend container on the same network.
# ═══════════════════════════════════════════════════════════════════════════════

services:
  nginx:
    image: nginx:alpine
    container_name: testbuild-checklist
    volumes:
      - ./backend/app/static/checklist:/usr/share/nginx/html:ro
    networks:
      - openagile_openagile_network
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=openagile_openagile_network"

      # ── Main Router: serve static checklist ─────────────────────────────────
      - "traefik.http.routers.testbuild.rule=Host(`testbuild.zubbystudio.shop`) && !PathPrefix(`/api`)"
      - "traefik.http.routers.testbuild.entrypoints=websecure"
      - "traefik.http.routers.testbuild.tls=true"
      - "traefik.http.routers.testbuild.tls.certresolver=cloudflare"
      - "traefik.http.routers.testbuild.priority=10"

      # ── HTTP → HTTPS Redirect ──────────────────────────────────────────────
      - "traefik.http.routers.testbuild-http.rule=Host(`testbuild.zubbystudio.shop`)"
      - "traefik.http.routers.testbuild-http.entrypoints=web"
      - "traefik.http.routers.testbuild-http.middlewares=testbuild-redirect"
      - "traefik.http.middlewares.testbuild-redirect.redirectscheme.scheme=https"

      # ── Service Port ────────────────────────────────────────────────────────
      - "traefik.http.services.testbuild.loadbalancer.server.port=80"

networks:
  openagile_openagile_network:
    external: true
```

**Key design decisions:**
- `!PathPrefix(`/api`)` on the Nginx router — so API calls fall through to the EPM router
- Priority 10 — low enough that Traefik matches the EPM API router first (implicit ~0) for API paths

---

### Task 2: Add API Path Router to EPM Container Labels

**Objective:** Add a Traefik router label on the EPM container that catches `/api/*` calls from `testbuild.zubbystudio.shop` and routes them to the EPM service.

**Files:**
- Modify: `docker-compose.v3.yml` — add 4 lines to `epm` labels section

**Step 1: Add** router label for testbuild API path after line 34:

```yaml
      # ── API Router (shared from testbuild) ──────────────────────────────────
      - "traefik.http.routers.epm-v3-testbuild-api.rule=Host(`testbuild.zubbystudio.shop`) && PathPrefix(`/api`)"
      - "traefik.http.routers.epm-v3-testbuild-api.entrypoints=websecure"
      - "traefik.http.routers.epm-v3-testbuild-api.tls=true"
      - "traefik.http.routers.epm-v3-testbuild-api.tls.certresolver=cloudflare"
      # NOTE: This reuses the existing epm-v3 service (port 8000) — no new service label needed.
```

**Why this works:** Traefik matches by router name (different names = separate routers). The existing `epm-v3` service label (line 43) serves as the backend for BOTH `epm-v3` (testdrive host) and `epm-v3-testbuild-api` (testbuild + /api prefix). No duplicate service label needed.

---

### Task 3: Backup and Archive Old Testbuilder

**Objective:** Save the old SQLite data, stop the container, archive the compose file.

**Files:**
- Archive: `docker-compose.test-builder.yml` → `backups/docker-compose.test-builder.yml.archived`

**Step 1: Backup SQLite volume.**

```bash
mkdir -p backups
docker run --rm \
  -v estate-portfolio_test_builder_data:/data \
  -v $(pwd)/backups:/backup \
  alpine \
  sh -c 'cp /data/db.sqlite /backup/testbuilder-$(date +%F).sqlite && ls -la /backup/testbuilder-*.sqlite'
```

**Step 2: Stop old container.**

```bash
docker compose -f docker-compose.test-builder.yml down
```
Expected: container removed, network disconnected.

**Step 3: Archive compose file.**

```bash
mv docker-compose.test-builder.yml backups/docker-compose.test-builder.yml.archived
```

**Step 4: Verify cleanup.**

```bash
docker ps --format '{{.Names}}' | grep -i testbuild-old
# Expected: empty (no output)

ls backups/testbuilder-*.sqlite
# Expected: file exists (backup confirmed)
```

---

### Task 4: Deploy Standalone Checklist

**Objective:** Start the Nginx container and verify the full flow.

**Step 1: Start the new container.**

```bash
docker compose -f docker-compose.testbuild.yml up -d
```

Expected: `Container testbuild-checklist  Started`

**Step 2: Ensure EPM container is running with the new API router label.**

```bash
docker compose -f docker-compose.v3.yml up -d epm
```

**Step 3: Verify Nginx serves the checklist page.**

```bash
curl -s -o /dev/null -w '%{http_code}' https://testbuild.zubbystudio.shop/
# Expected: 200 (Nginx serves index.html)

curl -s https://testbuild.zubbystudio.shop/ | head -3
# Expected: <!DOCTYPE html> <html lang="en"> <head> (checklist page)
```

**Step 4: Verify checklist page content (not EPM React app).**

```bash
curl -s https://testbuild.zubbystudio.shop/ | grep -c "Pre-Merge Checklist\|Test Results\|HOLDINGS\|REGISTRARS"
# Expected: ≥ 1 (checklist page content, not SPA)
```

**Step 5: Verify API calls route to EPM.**

```bash
curl -s -o /dev/null -w '%{http_code}' https://testbuild.zubbystudio.shop/api/v1/checklist/runs
# Expected: 401 (requires auth — proves it reached EPM's checklist router)

curl -s -o /dev/null -w '%{http_code}' https://testbuild.zubbystudio.shop/api/v1/auth/login
# Expected: 405 (proves it reached EPM's auth router)
```

**Step 6: Set the right directory for nginx to serve root `index.html` properly.**

After discussion with user, the nginx volume mount may need to be just the directory, and Nginx will serve its `index.html` by default. The Alpine nginx image already has a default config that serves from `/usr/share/nginx/html`, so mounting the checklist directory to that path should work directly.

---

### Task 5: Document and Commit

**Files:**
- Modify: `.context/feature-specs/F-TD-001-test-checklist-teardown.md` — set `status: COMPLETE`
- Modify: `.context/progress-tracker.md` — update
- Add: `.context/AGENT_LOG.md` — log entry
- Add: `docs/handovers/HO-030-testbuilder-teardown-checklist-standalone.md`

**Step 1: Commit.**

```bash
git add docker-compose.testbuild.yml docker-compose.v3.yml backups/ docker-compose.test-builder.yml .context/
git commit -m "feat: F-TD-001 testbuilder teardown + standalone checklist on testbuild

- Created docker-compose.testbuild.yml with nginx:alpine serving checklist HTML
- Added Traefik API router on EPM container for testbuild/api/* → EPM backend
- Backed up old testbuilder SQLite, stopped container, archived compose file
- testbuild.zubbystudio.shop now serves standalone one-page test tool
- API persistence works via Traefik path routing to EPM"
git push origin main
```

---

## Tests / Validation

| Check | Command | Expected |
|-------|---------|----------|
| Checklist page loads on testbuild | `curl https://testbuild.zubbystudio.shop/ -o /dev/null -w '%{http_code}'` | 200 |
| Page content is checklist (not SPA) | `curl -s https://testbuild.zubbystudio.shop/ \| grep -c "Pre-Merge"` | ≥ 1 |
| API routes reach EPM | `curl https://testbuild.zubbystudio.shop/api/v1/checklist/runs -o /dev/null -w '%{http_code}'` | 401 (auth required) |
| Login works via testbuild | `curl -s -X POST https://testbuild.zubbystudio.shop/api/v1/auth/login -H 'Content-Type: application/json' -d '{"username":"zubbyik","password":"a123456"}' -w '%{http_code}' -o /tmp/testbuild-login.html` | 200 |
| Old testbuilder container gone | `docker ps \| grep -i test` | empty |
| Backup exists | `ls backups/testbuilder-*.sqlite` | file exists |
| Old compose archived | `ls docker-compose.test-builder.yml 2>&1` | "No such file" |

---

## Risks and Open Questions

1. **Traefik priority**: The Nginx router has `priority=10` and rule `!PathPrefix(/api)`. The EPM API router has implicit priority ~0 (default). Traefik evaluates higher-priority routers first. The Nginx router with `!PathPrefix(/api)` should correctly NOT match `/api/*` paths, letting them fall through to the EPM router. However, if there's a Traefik version difference, test with `curl` first before declaring done.

2. **Cert resolver**: Both routers use `cloudflare` certresolver (matches the EPM setup). Let's Encrypt might be needed if cloudflare doesn't cover testbuild — but the old testbuilder was already running with some cert, so DNS already resolves.

3. **Login experience**: The user must log in at `testbuild.zubbystudio.shop/api/v1/auth/login` (POST) to get a cookie, then refresh the checklist page. The checklist page doesn't currently have a login button. Consider adding one to the standalone page if inconvenient.

4. **Nginx default config**: The Alpine nginx image's default config serves `/usr/share/nginx/html` on port 80 with autoindex off. Mounting `./backend/app/static/checklist:/usr/share/nginx/html:ro` should work out of the box — no custom nginx.conf needed.

5. **testdrive EPM**: The old `/api/v1/checklist/test-checklist` route in EPM's checklist.py becomes dead code (EPM no longer serves the page). Can be removed or left — doesn't hurt. The API endpoints (`/api/v1/checklist/runs`) remain active on both domains.

6. **Static file caching**: Nginx will serve files with its default caching headers. Add `expires -1;` and `add_header Cache-Control "no-cache, no-store, must-revalidate";` to an inline nginx config if the user wants to ensure always-fresh content. Low priority — can be addressed later.
