---
type: HO
id: HO-125
title: OpenCode → Claude: F-TD-001 Teardown Executed — 8dcbdf7
date: 2026-08-15
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-125 — F-TD-001 Teardown Executed

## Step 0 — Dependency check

Full grep across repo for `testbuild` found hits in:
- `docker-compose.v3.yml` — API router labels (removed)
- `docker-compose.testbuild.yml` — the file itself (archived)
- `docs/handovers/` — historical records (no change)
- `.context/` docs — infrastructure references (noted, update later)
- `.hermes/plans/` — historical plans (no change)
- `test_builder/BUILD_INSTRUCTIONS.md` — historical docs (no change)

No unexpected dependencies. No scripts, CI/CD configs, or active code
depends on testbuild.

## Step 1 — Ordered removal with verification

### 1a: Stop nginx container
```
Container testbuild-checklist Stopping
Container testbuild-checklist Stopped
Container testbuild-checklist Removing
Container testbuild-checklist Removed
```
→ Verify: `curl -s -o /dev/null -w '%{http_code}' https://testdrive.epm.zubbystudio.site/` → **200** ✅

### 1b: Remove Traefik labels from estate_portfolio_v3
Removed 5 labels (`epm-v3-testbuild-api.*`) from `docker-compose.v3.yml`.
Container recreated with `docker compose up -d --force-recreate`.
→ Verify: `curl -s -o /dev/null -w '%{http_code}' https://testdrive.epm.zubbystudio.site/` → **200** ✅

### 1c: Archive compose file
```
docker-compose.testbuild.yml → docker-compose.testbuild.yml.archived
```

## Step 2 — Final verification

```
testbuild.zubbystudio.shop → Exit: 35 (unreachable, unchanged) ✅
testdrive.epm.zubbystudio.site → 200 ✅
testdrive.epm.zubbystudio.site/api/v1/checklist/test-checklist → 401 (auth required) ✅
```

## Step 3 — Committed

```
commit 8dcbdf7abf3290906e0d6d18f23754e143e3df1f
F-TD-001: teardown testbuild nginx layer (dead — .shop expired, checklist moved to backend route)
```

## What was removed
- `testbuild-checklist` nginx container (stopped + removed)
- 5 Traefik labels from `estate_portfolio_v3` (`epm-v3-testbuild-api.*`)
- `docker-compose.testbuild.yml` (archived)

## What was NOT removed
- `testdrive.epm.zubbystudio.site` routing (unaffected)
- `_v3` container (testdrive depends on it)
- Checklist HTML file (still served by backend)
