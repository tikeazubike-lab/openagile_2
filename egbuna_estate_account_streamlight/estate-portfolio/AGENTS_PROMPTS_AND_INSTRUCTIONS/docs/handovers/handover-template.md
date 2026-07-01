---
type: HO
id: HO-XXX
title: [From Agent] → [To Agent]: [Topic in 5 words]
date: YYYY-MM-DD
from: [Agent name + role]
to: [Agent name + role]
protocol: OpenAgile Hybrid Framework v1.0
feature: F-XXX
parent-ho: HO-YYY | null
---

# HO-XXX — [From] → [To]: [Topic]
> **Type**: Handover · **Date**: YYYY-MM-DD · **Feature**: F-XXX

---

## 1. What Was Done

[Specific files changed — not "I updated the auth module" but
"Modified backend/app/routers/auth.py line 47: changed max_age from
None to 60*60*24*30"]

Files changed:
- `[file path]` — [what changed and why]
- `[file path]` — [what changed and why]

Commands run:
```bash
[exact commands, exact output]
```

Tests run:
```
[paste pytest/vitest output]
```

---

## 2. What Is Verified Working

[Exact evidence — not "it works now" but the specific command
run and the specific output seen]

```bash
# Command:
curl -s -X POST https://testdrive.epm.zubbystudio.shop/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"[pass]"}' \
  -v 2>&1 | grep -E "Set-Cookie|HTTP/"

# Output:
< HTTP/2 200
< set-cookie: epm_token=eyJ...; Max-Age=2592000; HttpOnly; SameSite=Strict
```

Acceptance items verified:
- [x] [DB] holdings table has deleted_at column
- [x] [API] POST /api/v1/admin/holdings returns 201
- [ ] [UI] Admin can create holding via drawer — NOT YET TESTED

---

## 3. What Is Broken / Uncertain

[Root cause if known — not "something is wrong with the charts"
but "dashboard.py line 89 returns sector_allocation without the
'name' field — Recharts requires dataKey='name' to render segments"]

| Item | Root Cause | Severity |
|------|-----------|---------|
| [description] | [exact cause] | P0/P1/P2 |

Items added to .context/current-issues.md:
- BUG-XXX: [description]

---

## 4. Next Agent Action List

[Numbered, specific, actionable — not "fix the frontend" but
"In src/routes/_app.dashboard.tsx line 234, replace
parseFloat(s.sector) with parseFloat(s.value ?? '0')"]

1. [Specific action with file + line if known]
2. [Specific action]
3. Run: `grep -r "editMode" src/` → confirm zero results
4. Run AT checklist items [DB-1], [DB-2], [API-3] from F-XXX spec
5. File AT-XXX.md in docs/testing/acceptance/
6. Write HO-XXX+1 to Claude with AT results

---

## 5. Blockers

[What literally cannot proceed until something else happens]

- [ ] Owl Alpha must push backend before Nex N2 starts frontend
- [ ] F-016 User Management must complete before role guards work
- [ ] No blockers — proceed immediately

---

## Test IDs Relevant to This HO

```
[DOMAIN]-[WORKFLOW]-BE-INT-001  — [description]
[DOMAIN]-[WORKFLOW]-FE-E2E-001  — [description]
```

---

## Files to Read Before Responding

If you are the receiving agent, read these before acting:

- .context/AGENTS.md
- .context/feature-specs/F-XXX.md
- .context/current-issues.md
- docs/handovers/HO-YYY.md (previous handover in this chain)
