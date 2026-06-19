# Domain Migration: v2 → v3 (testdrive.epm.zubbystudio.shop) Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Fork the existing v2 Docker infrastructure (docker-compose.v2.yml, Dockerfile.v2, .env.v2) into v3, changing all domain references from `demo.estate.zubbystudio.shop` to `testdrive.epm.zubbystudio.shop`, and updating all 19 files across the repo that reference the old domain.

**Architecture:** In-place rename: `*.v2.*` → `*.v3.*`, `epm_v2` container → `epm_v3`, `estate_portfolio_v2` → `estate_portfolio_v3`. Deploy.sh rewritten to target the new v3 stack. All documentation/test files get the domain string replaced.

**Tech Stack:** Docker Compose v3 format, Dockerfile multi-stage, sed/replace for domain changes across docs.

**User Directives:**
1. Domain = `testdrive.epm.zubbystudio.shop`  (DNS A record configured, resolves, 1 min TTL)
2. Q2 = B (edit v2 files in-place → v3)
3. Q4 = just change ALLOWED_ORIGINS to new domain (no dual-origin)
4. Every file referencing the old domain gets updated
5. This is a fork of v2 — project is already on the VPS
6. Fix deploy.sh

---

## Files That Need Changing (Complete Inventory)

### Infrastructure Files (Core — 6 files)

| File | Change |
|------|--------|
| `docker-compose.v2.yml` | Rename to `docker-compose.v3.yml`. Update domain, container name, service name, router names |
| `Dockerfile.v2` | Rename to `Dockerfile.v3` |
| `.env.v2` | Rename to `.env.v3`. Update `ALLOWED_ORIGINS` |
| `deploy.sh` | Rewrite entirely — wrong project path, wrong compose file, wrong domain |
| `backend/app/config.py` | Update comment on line 25, column 0 — `demo.estate` → `testdrive.epm` |

### Test Files (4 files)

| File | Change |
|------|--------|
| `backend/tests/performance/locustfile.py` | Update host URL |
| `epm-tests/frontend/tests/e2e/auth.spec.ts` | Update base URL |
| `epm-tests/backend/tests/performance/locustfile.py` | Update host URL |

### Handover & Onboarding Docs (5 files)

| File | Change |
|------|--------|
| `docs/handover/HO-009-dashboard-holdings-registrars-pricelist.md` | Domain string replace |
| `docs/handover/HO-013-claude-to-antigravity.md` | Domain string replace |
| `docs/handover/HO-018-claude-to-both-agents.md` | Domain string replace |
| `docs/onboarding/OB-001-onboarding.md` | Domain string replace + `epm_v2` → `epm_v3` |
| `docs/onboarding/OB-002-agent-delegation.md` | Domain string replace |

### Context & Status Docs (2 files)

| File | Change |
|------|--------|
| `docs/context/MASTER_CONTEXT.md` | Domain string replace + `Dockerfile.v2`/`docker-compose.v2` → v3 |
| `docs/context/PROJECT_STATUS.md` | Domain string replace |

### Acceptance Test Docs (4 files)

| File | Change |
|------|--------|
| `docs/testing/acceptance-tests/AT-001-price-entry-2026-05-05.md` | Domain string replace |
| `docs/testing/acceptance-tests/AT-002-registrars-2026-05-05.md` | Domain string replace |
| `docs/testing/acceptance-tests/AT-003-1-followup-test.md` | Domain string replace |
| `docs/testing/acceptance-tests/AT-003-dashboard-holdings-registrars-pricehist-root-copy.md` | Domain string replace |

### Architecture Docs (1 file)

| File | Change |
|------|--------|
| `docs/architecture/ADR-004-ngx-pdf-parser.md` | Domain string replace |

### Archive Docs (2 files — update only, keep as historical record)

| File | Change |
|------|--------|
| `docs/archive/2026-05-23-root-cleanup/Urgent_eodhd_fix.md` | Domain string replace |
| `docs/archive/2026-05-23-root-cleanup/ESTATE_PORTFOLIO_FINAL_HANDOVER.md` | Domain string replace |

### .context/ Files (reference the compose file by name)

| File | Change |
|------|--------|
| `.context/AGENT.md` | `docker-compose.v2.yml` → `docker-compose.v3.yml`, `epm_v2` → `epm_v3`, "EPM v2" → "EPM v3" in line 3 |
| `.cursor/rules/backend.mdc` | deployment section: `docker-compose.v2.yml` → `docker-compose.v3.yml`, `epm_v2` → `epm_v3` |
| `.cursor/rules/frontend.mdc` | deployment section: `docker-compose.v2.yml` → `docker-compose.v3.yml`, `epm_v2` → `epm_v3` |

**Total: ~28 files need changes.**

---

## Task 1: Rename Infrastructure Files (3 files)

**Objective:** Rename the core infrastructure files from v2 to v3 with updated domain content.

**Files:**
- Rename: `docker-compose.v2.yml` → `docker-compose.v3.yml`
- Rename: `Dockerfile.v2` → `Dockerfile.v3`
- Rename: `.env.v2` → `.env.v3`

**Step 1: Rename files**
```bash
mv docker-compose.v2.yml docker-compose.v3.yml
mv Dockerfile.v2 Dockerfile.v3
mv .env.v2 .env.v3
```

**Step 2: Update docker-compose.v3.yml content**

All occurrences of `demo.estate.zubbystudio.shop` → `testdrive.epm.zubbystudio.shop`
All occurrences of `estate_portfolio_v2` → `estate_portfolio_v3`
All occurrences of `epm-v2` → `epm-v3` (Traefik router names)
Header comment: update "Phase 2" → "Phase 3", "demo.estate" → "testdrive.epm"
Build: `dockerfile: Dockerfile.v2` → `dockerfile: Dockerfile.v3`
Env file: `.env.v2` → `.env.v3`

**Step 3: Update Dockerfile.v3 content**

Build context reference: no domain in Dockerfile itself, so just the header comment to update.

**Step 4: Update .env.v3 content**

```diff
- ALLOWED_ORIGINS=https://demo.estate.zubbystudio.shop
+ ALLOWED_ORIGINS=https://testdrive.epm.zubbystudio.shop
```

**Step 5: Verify**
```bash
grep -c "demo.estate.zubbystudio.shop" docker-compose.v3.yml
```
Expected: 0

---

## Task 2: Update AGENT.md and .cursor/rules (3 files)

**Objective:** Update the entry point docs that reference the v2 compose file and container name.

**Files:**
- Modify: `.context/AGENT.md` — lines 3, 30, 52, 58, 61
- Modify: `.cursor/rules/backend.mdc` — deployment section
- Modify: `.cursor/rules/frontend.mdc` — deployment section

**Step 1: AGENT.md changes**

| Current | Replacement |
|---------|-------------|
| `EPM v2 — Test Drive` | `EPM v3 — Test Drive` |
| `docker-compose.v2.yml` | `docker-compose.v3.yml` |
| `epm_v2` | `epm_v3` |

**Step 2: backend.mdc changes**

```
# Before
docker compose -f docker-compose.v2.yml up -d --build epm_v2
# After
docker compose -f docker-compose.v3.yml up -d --build epm_v3
```

**Step 3: frontend.mdc changes**

Same pattern — `docker-compose.v2.yml` → `docker-compose.v3.yml`, `epm_v2` → `epm_v3`.

---

## Task 3: Fix deploy.sh (1 file)

**Objective:** Rewrite deploy.sh to target v3 stack with correct paths and domain.

**Files:**
- Rewrite: `deploy.sh`

**Complete content:**
```bash
#!/bin/bash
# EPM v3 — Test Drive Deployment Script
# Executed directly on Netcup VPS
set -e

PROJECT_DIR="/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio"

echo "========================================"
echo "EPM v3 — Test Drive Deployment"
echo "========================================"
echo ""

cd "$PROJECT_DIR" || exit 1

echo "📦 Pulling latest changes from GitHub..."
git pull origin main

# Check if Dockerfile.v3 or requirements.txt changed
if git diff HEAD@{1} --name-only | grep -qE 'Dockerfile.v3|requirements.txt'; then
    echo "🔨 Detected changes in dependencies, rebuilding images..."
    docker compose -f docker-compose.v3.yml up -d --build epm_v3
else
    echo "♻️  No dependency changes, restarting..."
    docker compose -f docker-compose.v3.yml up -d
fi

echo "⏳ Waiting for services to stabilize..."
sleep 10

echo "🏥 Running health check..."
if docker compose -f docker-compose.v3.yml ps | grep -q "Up"; then
    echo "✅ Containers are running"
    docker compose -f docker-compose.v3.yml ps
else
    echo "❌ Some containers failed to start"
    docker compose -f docker-compose.v3.yml ps
    exit 1
fi

echo ""
echo "========================================"
echo "✨ Deployment Complete!"
echo "========================================"
echo "Dashboard: https://testdrive.epm.zubbystudio.shop"
echo ""
```

**Verification:** `bash -n deploy.sh` — no syntax errors.

---

## Task 4: Update config.py (1 file)

**Objective:** Update the CORS comment to reflect new domain.

**Files:**
- Modify: `backend/app/config.py:25`

**Change:**
```diff
-    # In production: https://demo.estate.zubbystudio.shop
+    # In production: https://testdrive.epm.zubbystudio.shop
```

**NOTE:** The actual ALLOWED_ORIGINS value comes from `.env.v3`, not config.py. Only the comment changes.

---

## Task 5: Update All Test Files (4 files)

**Objective:** Replace `demo.estate.zubbystudio.shop` with `testdrive.epm.zubbystudio.shop` in all test configs.

**Files:**
- Modify: `backend/tests/performance/locustfile.py`
- Modify: `epm-tests/frontend/tests/e2e/auth.spec.ts`
- Modify: `epm-tests/backend/tests/performance/locustfile.py`

**Step 1: Simple string replace for each file**

Each file contains the domain in comments and URL strings. Replace all occurrences.

**Step 2: Verify**
```bash
grep -rn "demo.estate.zubbystudio.shop" backend/tests/ epm-tests/
```
Expected: 0

---

## Task 6: Update Documentation Files (14 files)

**Objective:** Replace `demo.estate.zubbystudio.shop` with `testdrive.epm.zubbystudio.shop` across all docs.

**Files (sorted by category):**

Context:
- `docs/context/MASTER_CONTEXT.md` — also update `Dockerfile.v2`/`docker-compose.v2`/`epm_v2` references
- `docs/context/PROJECT_STATUS.md`

Handovers:
- `docs/handover/HO-009-dashboard-holdings-registrars-pricelist.md`
- `docs/handover/HO-013-claude-to-antigravity.md`
- `docs/handover/HO-018-claude-to-both-agents.md`

Onboarding:
- `docs/onboarding/OB-001-onboarding.md` — also has `epm_v2` references
- `docs/onboarding/OB-002-agent-delegation.md`

Acceptance Tests:
- `docs/testing/acceptance-tests/AT-001-price-entry-2026-05-05.md`
- `docs/testing/acceptance-tests/AT-002-registrars-2026-05-05.md`
- `docs/testing/acceptance-tests/AT-003-1-followup-test.md`
- `docs/testing/acceptance-tests/AT-003-dashboard-holdings-registrars-pricehist-root-copy.md`

Architecture:
- `docs/architecture/ADR-004-ngx-pdf-parser.md`

Archive (update for consistency, keep as historical record):
- `docs/archive/2026-05-23-root-cleanup/Urgent_eodhd_fix.md`
- `docs/archive/2026-05-23-root-cleanup/ESTATE_PORTFOLIO_FINAL_HANDOVER.md`

**Step 1: Batch string replace**

Use `patch` (replace mode) or `sed` for each file. Each file has 1–5 occurrences.

**Step 2: Verify after all updates**
```bash
grep -rn "demo.estate.zubbystudio.shop" docs/
```
Expected: 0 hits (all replaced).

---

## Verification (Final)

After all tasks:

- [ ] `docker-compose.v3.yml` exists (v2 no longer the canonical file)
- [ ] `Dockerfile.v3` exists
- [ ] `.env.v3` exists with `ALLOWED_ORIGINS=https://testdrive.epm.zubbystudio.shop`
- [ ] `deploy.sh` runs without syntax errors and references v3
- [ ] `backend/app/config.py` comment updated
- [ ] No file in `backend/tests/` or `epm-tests/` references `demo.estate.zubbystudio.shop`
- [ ] No file in `docs/` references `demo.estate.zubbystudio.shop`
- [ ] `.context/AGENT.md` references `docker-compose.v3.yml` and `epm_v3`
- [ ] `.cursor/rules/*.mdc` references v3
- [ ] `grep -rn "demo.estate.zubbystudio.shop" .` returns 0 (excluding `.git/`)
- [ ] `grep -rn "\.v2" .context/AGENT.md .cursor/rules/backend.mdc .cursor/rules/frontend.mdc` shows no v2 references

## Risks

- **Risk:** Archive docs reference a domain that no longer exists. **Accept.** They're historical records; the content was accurate at the time.
- **Risk:** Some files in `docs/archive/` reference `estate.zubbystudio.shop` (the old Streamlit app, not `demo.estate`). These should NOT be changed — they're a different domain for a different app.
- **Risk:** If `docker-compose.yml` (the original Streamlit one) also references `demo.estate`, it should be left alone. **Verification:** `docker-compose.yml` references `estate.zubbystudio.shop`, not `demo.estate.zubbystudio.shop` — safe.
- **Risk:** The rename (v2 → v3) means the old v2 stack won't be runnable without reverting. **Accept** — v2 was the beta/test domain, v3 is the production cutover.

## Open Questions

1. Should the old v2 files (`docker-compose.v2.yml`, `Dockerfile.v2`, `.env.v2`) be DELETED after the v3 fork, or kept for rollback?
2. Should `docs/archive/` files be updated at all (they're historical snapshots), or left with the original domain?
3. Are there GitHub Actions workflow files that reference the domain or the v2 compose file? (No `.github/workflows/` directory was found, but double-check.)