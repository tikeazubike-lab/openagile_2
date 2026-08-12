# HO-030 — Testbuilder Teardown + Standalone Checklist on testbuild

**Status:** COMPLETE
**Date:** 2026-07-05
**Agent:** Hermes (governance + execution)

## Summary

Tore down the abandoned `docker-compose.test-builder.yml` service (port 8000, SQLite) and redeployed `testbuild.zubbystudio.shop` as a standalone one-page HTML test tool.

## What Changed

| File | Action |
|------|--------|
| `backend/app/static/checklist/index.html` | Added login form + auth gating |
| `docker-compose.testbuild.yml` | **NEW** — nginx:alpine serving checklist HTML |
| `docker-compose.v3.yml` | Added API router for `testbuild.zubbystudio.shop/api/*` → EPM backend |
| `backups/testbuilder-2026-07-05.sqlite` | Backup of old SQLite data |
| `backups/docker-compose.test-builder.yml.archived` | Archived compose file |

## Architecture

```
testbuild.zubbystudio.shop
    │
    ├──  /  →  nginx:alpine → index.html (standalone checklist page)
    │
    └──  /api/*  →  Traefik (path match) → estate_portfolio_v3:8000
```

- **Static HTML** served by nginx:alpine (fast, no Python overhead)
- **API calls** (`/api/v1/checklist/runs`, `/api/v1/auth/login`) are relative → Traefik routes to EPM backend
- **Same-origin** — no CORS issues, cookies for testbuild domain work naturally
- **Login**: User enters credentials on the page → POST to `/api/v1/auth/login` on same domain → JWT cookie set for testbuild

## Verification Results

| Check | Result |
|-------|--------|
| `GET /` | 200 — checklist HTML served |
| Page has "Pre-Merge" content | ✅ (3 matches, not SPA) |
| `GET /api/v1/checklist/runs` (no auth) | 401 — reached EPM ✅ |
| `POST /api/v1/auth/login` | 200 — cookie set for testbuild ✅ |
| `GET /api/v1/auth/me` (with cookie) | 200 — user zubbyik, admin role ✅ |
| `GET /api/v1/checklist/runs` (with cookie) | 200 — empty data ✅ |

## Current Checklist Items (ITEMS array)

The checklist has 20 items across 4 sections:

1. **F-017 — Edit Toggle Removed** (8 items): Holdings, Registrars, Companies, Users, Price Entry, Data Upload, Admin actions, Readonly actions
2. **F-016 — Admin Restructure** (3 items): User list, Admin menu, Sign out
3. **Data Integrity** (4 items): Holdings 77 positions, Price History, Dashboard, Companies
4. **Auth & Access Control** (5 items): Login, 401 redirect, 403 readonly, Uploads, Notifications

## Rollover Workflow

After each fix/feature commit, Hermes will:
1. Update `ITEMS` array in `index.html` with the new feature's test cases
2. Roll over previously skipped/failed items (keep them in the list)
3. Human visits `https://testbuild.zubbystudio.shop/`, logs in, tests manually
4. Human clicks "Generate Sign-off", copies markdown to PR/Merge

## File Details

**Checklist HTML:** `backend/app/static/checklist/index.html`
- Mounted read-only in nginx container. HTML edits are live after `docker restart testbuild-checklist`
- Permissions: 644 (readable by nginx worker)

**Nginx container:** `testbuild-checklist`
- Network: `openagile_openagile_network`
- Image: `nginx:alpine`
- Auto-restart: `unless-stopped`

**Traefik router:** `epm-v3-testbuild-api` on the EPM container
- Rule: `Host(testbuild.zubbystudio.shop) && PathPrefix(/api)`
- Routes to existing `epm-v3` service on port 8000
- Uses `cloudflare` certresolver (same as testdrive)
