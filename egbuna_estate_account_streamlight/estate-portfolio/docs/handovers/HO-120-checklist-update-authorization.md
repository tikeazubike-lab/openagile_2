---
type: HO
id: HO-120
title: Claude → OpenCode (deepseek-flash builder): Apply Checklist Update, Commit Immediately
date: 2026-08-12
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-120 — Apply Checklist Content Update

## Decision

HO-119's Tasks 1–4 approved as proposed:

- **Remove** the 6 redundant F-017 toggle-check items (1–6) — now a
  locked architectural decision confirmed via the HO-107/108/109 audit,
  not something worth re-verifying by hand every deployment
- **Update** item 12's hardcoded "77 positions" to a generic phrasing
  (e.g. "Holdings count matches expected total, values look correct")
  so it doesn't go stale as the holdings count changes
- **Keep** the other 28 existing items as-is
- **Add** the 17 proposed new items (F-007 ×5, F-022 ×6, F-026 ×5,
  F-017-consolidated ×1)

Resulting checklist: 46 items total (28 kept + 1 updated + 17 new + the
1 consolidated F-017 item replacing the 6 removed).

## Task 1 — Apply to `backend/app/static/checklist/index.html`

Update the static HTML per the above. Follow the existing item
formatting/structure already in the file — don't restructure the page
layout, just update section content.

## Task 2 — Commit immediately, this time

Per this session's file-loss incident: **a handover isn't complete until
it's committed.** After applying the change:

```bash
git add backend/app/static/checklist/index.html
git commit -m "F-TD-001: refresh pre-merge checklist for F-007/F-022/F-026, remove redundant F-017 items"
git log -1 --format="%H %s"
```

Report the actual commit hash in your reply — not "committed," the real
hash from `git log`. This is now the standard for closing out any
handover that touches files: show the commit, don't just say it happened.

## Task 3 — Verify the deploy path this time

Given HO-115's earlier mistake (deployed to `/app/static/` instead of the
correct `/app/app/static/`), double-check the deployment target before
copying anything, and confirm post-deploy that the live served content
actually reflects the change — same verification pattern as HO-117,
not just "file was copied."

---

## Reply format

Raw commit hash, raw confirmation the live checklist page now shows 46
items with the updated content — not a narrated "done."

Reply as **HO-121**.
