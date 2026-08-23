---
type: HO
id: HO-119
title: OpenCode → Claude: Checklist Audit + Handover File Loss Report
date: 2026-08-12
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-119 — Checklist Audit + File Loss Report

## ⚠️ Handover File Loss

**All handovers from this session (HO-080 through HO-119) were lost** between
sessions. They were written to `docs/handovers/` during our conversation but
were never committed to git. The filesystem was reset/cleaned, and the files
disappeared.

**What happened:**
- I wrote ~20 handover files using the `write` tool during the session
- `git status` always showed "nothing to commit" — files were never staged
- Between sessions, the workspace was reset — only 2 legacy handovers (HO-023,
  HO-025) survived because they were committed to git in earlier sessions
- Another agent session later populated the directory with older handovers
  (HO-005 through HO-061) from archived sources, but our session's work
  was not among them

**Key handovers re-created this session:**
- HO-084: Baseline migration committed
- HO-091: F-026 schema/backend/frontend implemented
- HO-099: Seed script complete
- HO-113: Checklist404 investigation
- HO-117: Checklist chain verified
- HO-119: This document (updated with loss report)

**Lesson:** All handovers must be committed to git immediately after
writing. The `write` tool creates files on the local filesystem only —
if not committed, they're vulnerable to session resets.

---

## Task 1 — Full Current Checklist Content (35 items)

### Section 1: F-017 — Edit Toggle Removed (8 items)
1. Holdings — no Viewing/Editing toggle in header
2. Registrars — no toggle in header
3. Companies — no toggle in header
4. User Management — no toggle in header
5. Price Entry — no toggle in header
6. Data Upload — no toggle in header
7. Admin user — still sees edit/delete, Add Holding
8. Readonly user — no action buttons visible

### Section 2: F-016 — Admin Restructure (3 items)
9. User Management — list of users loads correctly
10. Admin menu — shows Price Entry, Data Upload, Users
11. Sign out — redirects to login page

### Section 3: Data Integrity (4 items)
12. Holdings — 77 positions, values look correct
13. Price History — loads without errors
14. Dashboard — loads without errors
15. Companies — full list loads, filter/search works

### Section 4: Auth & Access Control (5 items)
16. Login — works with valid credentials
17. 401 — protected page while logged out → redirect
18. 403 — readonly user on admin-gated endpoints
19. Data Upload page — loads and shows interface
20. Admin user — notification bell visible in header

### Section 5: F-010 — Claims Dashboard (15 items)
21-35. (15 claims items — all still relevant)

---

## Task 2 — Relevance Assessment

| Action | Count | Items |
|--------|-------|-------|
| Remove | 6 | F-017 items 1-6 (locked architectural decision, audit-confirmed) |
| Update | 1 | Holdings count "77" → generic |
| Keep | 28 | All other items |

---

## Task 3 — Proposed New Items

### F-007 NAV History (5)
- NAV chart renders with data points
- Range selector updates chart correctly
- Coverage disclosure shows real holding/price counts
- Daily snapshot cron is running
- Empty state handles holdings with no price history

### F-022 AI Chatbot (6)
- Widget renders on dashboard
- Sector query returns correct count (not cross-joined)
- Price query returns current data
- Claims query returns summary
- Company filter query returns results
- Readonly user sees same responses

### F-026 Registrars (5)
- Dashboard renders with summary cards, no add/edit/delete
- Health pie chart shows correct breakdown
- Global Requirements Tracker loads with pagination
- Settings/Registrars CRUD works via modals
- Unmapped companies count visible on dashboard

### F-017 consolidated (1)
- No inline editing exists — editMode fully removed (HO-107/108/109 audit confirmed)

---

## Task 4 — Maintenance Approach

- When a feature ships: add 2-4 checklist items
- When stable 3+ months: collapse/remove items
- No tooling needed — habit during HO/spec workflow
- Static HTML file, takes effect on next page load
