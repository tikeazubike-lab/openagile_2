---
type: HO
id: HO-121
title: OpenCode → Claude: Checklist Updated, Committed, Deployed — ec151c8
date: 2026-08-13
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-121 — Checklist Update Applied + Committed

## Task 1 — Checklist updated

Changes applied to `backend/app/static/checklist/index.html`:

- **Removed** 6 redundant F-017 toggle-check items (locked architectural decision, audit-confirmed)
- **Updated** Holdings count from hard-coded "77" to generic "positions load, values look correct"
- **Added** consolidated F-017 item referencing HO-107/108/109 audit
- **Added** 5 F-007 NAV History items (chart, range, coverage, cron, empty state)
- **Added** 6 F-022 AI Chatbot items (widget, sector/price/claim/company queries, RBAC)
- **Added** 5 F-026 Registrar items (dashboard, health, tracker, settings, unmapped)
- **Updated** subtitle domain from `.shop` to `.site`
- **Fixed** stale "20" total count placeholder

Final count: **46 items** across 8 sections.

## Task 2 — Committed immediately

```
commit ec151c8f179cc979f220fb008979e304bdd819cb
F-TD-001: refresh pre-merge checklist for F-007/F-022/F-026, remove redundant F-017 items
```

## Task 3 — Deploy path verified

Deployed to `/app/app/static/checklist/index.html` (correct path — not `/app/static/`).

Live content verified:
- ✅ F-007 NAV History section: FOUND
- ✅ F-022 AI Chatbot section: FOUND
- ✅ F-026 Registrar section: FOUND
- ✅ F-017 consolidated item: FOUND
- ✅ Old hardcoded 77: REMOVED
- ✅ Updated domain: CORRECT
