---
type: HO
id: HO-117
title: OpenCode → Claude: All 5 Checks Complete — Fix IS Deployed, Root Cause Was Wrong Deploy Path
date: 2026-08-11
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-117 — `/test-checklist` Investigation: Full Chain Verified

## Root cause

HO-115 deployed to wrong path (`/app/static/` instead of `/app/app/static/`).
Backend serves from `/app/app/static/`.

## All 5 checks — raw evidence

| Check | Result |
|-------|--------|
| 1. Source file has fix | ✅ `href="/api/v1/checklist/test-checklist"` |
| 2. Built bundle has fix | ✅ In `_app-Dzmwl7Pl.js` |
| 3. Served bundle has fix | ✅ Backend serves from `/app/app/static/` |
| 4. Timestamp | ✅ Build Aug 11 12:27, deploy Aug 11 22:09 UTC |
| 5. Second reference | ✅ Only one place in codebase |

Fix is correctly deployed. Zubbyik should see it after hard refresh.
