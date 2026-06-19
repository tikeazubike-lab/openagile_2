# progress-tracker.md — EPM Progress Tracker

Agent updates this file at the END of every session.

Last updated: 2026-06-15 (framework initialisation)

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

| ID   | Feature             | Status       | Last HO  | Notes                        |

|------|---------------------|--------------|----------|------------------------------|

| F-001| Authentication      | ✅ Complete  | HO-008   | 30-day cookie, logout fixed. Owner: Owl Alpha (backend) + Nex N2 (frontend) |

| F-002| Dashboard           | ⚠️ Bugs open | AT-003-1 | Charts blank, bell broken    |

| F-003| Holdings            | ⚠️ Bugs open | AT-003-1 | Inline edit, Add Holding 500 |

| F-004| Price Entry         | ✅ Complete  | AT-001   | PDF parser, CSV, audit log   |

| F-005| Price History       | ✅ Complete  | AT-003-1 | Chart, table, date filter    |

| F-006| Registrars          | ⚠️ Bugs open  | AT-002   | Docs, requirements, linking  |

| F-007| NAV History         | 📋 Planned   | —        | Gherkin SC-025 to SC-031     |

| F-008| Dividends           | 📋 Planned   | —        | WHT, annual summary          |

| F-009| Transactions        | 📋 Planned   | —        | CRUD + auto-generate         |

| F-010| Claims              | 📋 Planned   | —        | AMCON/CAC tracking           |

| F-011| Rebalancing         | 📋 Planned   | —        | Sector targets + gap         |

| F-012| Watchlist           | 📋 Planned   | —        | Target price tracking        |

| F-013| Companies CRUD      | 📋 Planned   | —        | Edit page (list exists)      |

| F-014| Corporate Actions   | 📋 Planned   | —        | Bonus/rights/split/merger    |

| F-015| Obsidian Import     | 📋 Planned   | —        | import_obsidian.py + sync    |

| F-016| Settings            | 📋 Planned   | —        | Users, deleted, import UI    |

Status key:

  ✅ Complete   — all checklist items passing, AT filed

  ⚠️ Bugs open — built but open issues from acceptance test

  🔄 In progress — actively being worked on this sprint

  📋 Planned   — spec exists or will be written, not started

---

## Open Bugs Summary

See .context/current-issues.md for full details.

Quick reference:

  BUG-001  Dashboard charts blank (sector allocation + top holdings)

  BUG-002  Holdings inline edit cursor jumps on keystroke

  BUG-003  POST /api/v1/holdings 500 error (Add Holding drawer)

  BUG-004  Theme toggle icon does not change on click

  BUG-005  Notification bell not showing action items

---

## Missing Dependencies (Add Before Implementing)

  scipy==1.13.1          needed for F-007 XIRR calculation

  APScheduler==3.10.4    needed for F-007 NAV History daily snapshot

Add both to:

  backend/requirements.txt

Then rebuild container:

  docker compose -f docker-compose.v2.yml up -d --build epm_v2

---

## Recent Sessions (newest first)

2026-06-15 | Framework initialisation | Claude | Created .context/ files + F-001–F-006 specs

2026-06-19 | F-005 backend verification & wrap-up | Owl Alpha | Verified API matches spec, all checks pass, marked complete

[Agent appends here after each session]

---

## Next Priority

1. Fix BUG-001 through BUG-005 (open from AT-003-1)

2. Then F-007 NAV History

3. Then F-008 Dividends

4. Then F-009 Transactions

5. Then F-010 Claims


