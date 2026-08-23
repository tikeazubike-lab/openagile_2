---
type: HO
id: HO-113
title: OpenCode → Claude: /test-checklist 404 Confirmed — Frontend Link Path Mismatch
date: 2026-08-02
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-113 — `/test-checklist` 404 Investigation

## Root cause: routing mismatch

Frontend link: `href="/test-checklist"`
Backend route: `GET /api/v1/checklist/test-checklist` (with `/api/v1` prefix)

Traefik routes ALL traffic on `testdrive.epm.zubbystudio.site` to port 8000. Backend SPA catch-all serves `index.html`. React SPA loads, no route match → 404.

## Proposed fix

Change `Navbar.tsx:92` from `href="/test-checklist"` to `href="/api/v1/checklist/test-checklist"`.

## Evidence

- Backend endpoint returns 401 (auth required) when hit directly — confirms route exists
- Browser shows SPA 404 page for `/test-checklist`
- Static HTML file exists at `backend/app/static/checklist/index.html` (17KB)
