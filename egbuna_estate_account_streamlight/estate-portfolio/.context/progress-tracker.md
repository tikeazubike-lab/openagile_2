# progress-tracker.md — EPM Progress Tracker

Agent updates this file at the END of every session.

Last updated: 2026-06-21

---

## Current Phase

Phase 3 — Completing Core Pages + Framework Test Drive

Environment: testdrive.epm.zubbystudio.shop (openagile_2 codebase)

---

## Active Work

[Agent fills this in at session start — one line describing the task]

Example: "Fixing dashboard chart blank bug (BUG-001) — Deepseek v4"

---

## Feature Status

| ID   | Feature             | Status       | Last HO  | Notes |
|------|---------------------|--------------|----------|-------|
| F-001| Authentication      | ✅ Complete  | HO-008   | 30-day cookie, logout fixed. Owner: Owl Alpha + Nex N2 |
| F-002| Dashboard           | ⚠️ Bugs open | AT-003-1 | Charts blank (BUG-001 fixed, needs verification), bell broken. Recent Transactions + Action Items cards are 📋 Planned — depend on F-009 and F-016 |
| F-003| Holdings            | ⚠️ Bugs open | AT-003-1 | Inline edit cursor jump (BUG-002), Add Holding 500 error (BUG-003) |
| F-004| Price Entry         | ✅ Complete  | AT-001   | PDF parser, CSV, audit log |
| F-005| Price History       | ⚠️ Bugs open | AT-003-1 | Chart UX refinement deferred — functional but needs visual polish |
| F-006| Registrars          | ⚠️ Bugs open | AT-002   | Docs, requirements, linking |
| F-007| NAV History         | 📋 Planned   | —        | Gherkin SC-025 to SC-031. Needs scipy==1.13.1, APScheduler==3.10.4 |
| F-008| Dividends           | 📋 Planned   | —        | WHT, annual summary |
| F-009| Transactions        | 📋 Planned   | —        | CRUD + auto-generate. Dependency for F-002 Recent Transactions card |
| F-010| Claims              | 📋 Planned   | —        | AMCON/CAC tracking |
| F-011| Rebalancing         | 📋 Planned   | —        | Sector targets + gap |
| F-012| Watchlist           | 📋 Planned   | —        | Target price tracking |
| F-013| Companies CRUD      | 📋 Planned   | —        | Edit page (list exists) |
| F-014| Corporate Actions   | 📋 Planned   | —        | Bonus/rights/split/merger |
| F-015| Obsidian Import     | 📋 Planned   | —        | import_obsidian.py + sync |
| F-016| Settings            | 📋 Planned   | —        | Users, deleted, import UI. Dependency for F-002 Action Items card |
| F-017| Remove editMode toggle | 📋 Planned | —        | Depends on F-003 Holdings stable |
| F-022| AI Assisted Interactive ChatBot | 📋 Planned | — | Blocked on F-007–F-016. Claude architected, Grok reviewed (all 7 gaps resolved), Lovable UI component ready. Spec: F-022-ai-chatbot.md |

Status key:
  ✅ Complete   — all checklist items passing, AT filed
  ⚠️ Bugs open — built but open issues from acceptance test
  🔄 In progress — actively being worked on this sprint
  📋 Planned   — spec exists or will be written, not started

---

## Open Bugs Summary

See .context/current-issues.md for full details.

Quick reference:
  BUG-001  Dashboard charts blank (sector allocation + top holdings) — FIXED, needs verification
  BUG-002  Holdings inline edit cursor jumps on keystroke — IN PROGRESS (Nex N2)
  BUG-003  POST /api/v1/holdings 500 error (Add Holding drawer) — FIXED by Owl Alpha, needs verification
  BUG-004  Theme toggle icon does not change on click — ✅ Complete (already fixed in existing code)
  BUG-005  Notification bell not showing action items — ✅ Complete (Nex N2)

---

## Missing Dependencies (Add Before Implementing)

  scipy==1.13.1          needed for F-007 XIRR calculation
  APScheduler==3.10.4    needed for F-007 NAV History daily snapshot

Add both to:
  backend/requirements.txt

Then rebuild container:
  docker compose -f docker-compose.v3.yml up -d --build epm_v3

---

## Recent Sessions (newest first)

2026-06-21 | F-022 AI Chat Bot spec | Claude + Grok + Lovable | Spec created, architect review complete, all 7 Grok gaps resolved. Blocked on F-007–F-016
2026-06-19 | F-005 backend verification & wrap-up | Owl Alpha | Verified API matches spec, all checks pass
2026-06-15 | Framework initialisation | Claude | Created .context/ files + F-001–F-006 specs

[Agent appends here after each session]

---

## Next Priority

1. Fix BUG-002 through BUG-005 (open from AT-003-1)

2. F-009 Transactions — needed for Dashboard Recent Transactions card (F-002 dependency)

3. F-016 Settings / User Management — needed for Dashboard Action Items card (F-002 dependency)

4. Then F-007 NAV History

5. Then F-008 Dividends

6. Then F-010 Claims

7. Then F-022 AI Chat Bot (blocked until F-007–F-016 complete)
