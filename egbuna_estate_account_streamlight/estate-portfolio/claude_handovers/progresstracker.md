# progress-tracker.md — EPM Progress Tracker

**Last updated**: 2026-06-24 (F-016 User Management → COMPLETE)

---

## Current Phase

Phase 3 — Core pages + Admin restructure + New features
Environment: testdrive.epm.zubbystudio.shop (openagile_2 codebase)

---

## Active Work

[Agent fills this in at session start]

---

## Feature Status

### Phase 2-3A (Foundation + Core Trading)

| ID    | Feature         | Status        | Last HO  | Notes                             |
|-------|-----------------|---------------|----------|-----------------------------------|
| F-001 | Authentication  | COMPLETE      | HO-008   | 30-day cookie, logout fixed       |
| F-002 | Dashboard       | BUGS-OPEN     | AT-003-1 | Charts blank, bell broken         |
| F-003 | Holdings        | BUGS-OPEN     | AT-003-1 | Inline edit cursor, Add 500 error |
| F-004 | Price Entry     | COMPLETE      | AT-001   | PDF parser, CSV, audit log        |
| F-005 | Price History   | COMPLETE      | AT-003-1 | Chart, table, date filter         |
| F-006 | Registrars      | COMPLETE      | AT-002   | Docs, requirements, linking       |

### Phase 3B (Admin Restructure)

| ID     | Feature                    | Status   | Notes                                              |
|--------|----------------------------|----------|----------------------------------------------------|
| F-003b | Holdings Admin Edit View   | COMPLETE | /admin/holdings replaces inline edit toggle        |
| F-006b | Registrars Admin Edit View | COMPLETE | /admin/registrars replaces inline edit toggle      |
| F-017  | Remove editMode toggle     | COMPLETE | Delete uiStore.editMode, role guards replace it    |

### Phase 3C (New Core Features)

| ID    | Feature         | Status   | Notes                                              |
|-------|-----------------|----------|----------------------------------------------------|
| F-016 | User Management | COMPLETE  | F-016    | Admin-gated user CRUD + role definitions |
| F-007 | NAV History     | PLANNED  | Gherkin SC-025-031 written                         |
| F-008 | Dividends       | PLANNED  | WHT, annual summary, DRIP                          |
| F-009 | Transactions    | PLANNED  | CRUD + auto-generate from holdings                 |
| F-010 | Claims          | PLANNED  | AMCON/CAC tracking, ClaimRecord table              |
| F-011 | Rebalancing     | PLANNED  | Sector targets + gap analysis                      |
| F-012 | Watchlist       | PLANNED  | Track stocks, target price, gap-to-target          |

### Phase 3D (Companies + News)

| ID     | Feature              | Status   | Notes                                          |
|--------|----------------------|----------|------------------------------------------------|
| F-013  | Companies Page       | PLANNED  | NGX scrape to DB cache, Market/Sector filters  |
| F-013b | Company Profile Page | PLANNED  | Hidden from nav, click from Companies table    |
| F-018  | Financial News Bell  | PLANNED  | Reddit + Nigerian RSS + Substack RSS           |
| F-019  | NGX Data Refresh     | PLANNED  | Manual trigger + optional daily schedule       |

### Phase 3E (Settings + Cutover)

| ID    | Feature             | Status   | Notes                                   |
|-------|---------------------|----------|-----------------------------------------|
| F-014 | Corporate Actions   | PLANNED  | Bonus, rights, split, merger            |
| F-015 | Obsidian Import     | PLANNED  | import_obsidian.py + vault sync         |
| F-020 | Admin Section Hub   | PLANNED  | /admin/* routes consolidated            |
| F-021 | Production Cutover  | PLANNED  | estate.zubbystudio.shop to v2           |

### Phase 4 (Future — Not Yet Specced)

| ID       | Feature                   | Notes                                        |
|----------|---------------------------|----------------------------------------------|
| F-P4-01  | Stock Purchase Workflow   | Registrar + calendar + inbox — needs design  |
| F-P4-02  | Multi-portfolio           | Separate portfolios per user                 |
| F-P4-03  | Eurobonds / Real Estate   | Asset abstraction layer                      |
| F-P4-04  | Export to Excel           | Tax filing aid                               |

---

## Open Bugs (fix before Phase 3C)

| ID      | Feature   | Description                       | Fix Spec |
|---------|-----------|-----------------------------------|----------|
| BUG-001 | Dashboard | Charts blank (Recharts data shape)| HO-015   |
| BUG-002 | Holdings  | Inline edit cursor jumps          | HO-018   |
| BUG-003 | Holdings  | POST /api/v1/holdings 500 error   | HO-018   |
| BUG-004 | Dashboard | Theme toggle icon static          | HO-018   |
| BUG-005 | Dashboard | Bell not showing action items     | HO-018   |

---

## Missing Dependencies (add to requirements.txt before implementing)

scipy==1.13.1          needed for F-007 XIRR
APScheduler==3.10.4    needed for F-007 NAV snapshot + F-019 NGX refresh
beautifulsoup4==4.12.3 needed for F-013 NGX companies scraper
feedparser==6.0.11     needed for F-018 RSS news feeds
praw==7.7.1            needed for F-018 Reddit API

---

## Admin Section Navigation Map

/admin/holdings          all Holdings CRUD (replaces inline edit toggle)
/admin/registrars        all Registrar CRUD (replaces inline edit toggle)
/admin/price-entry       already exists
/admin/corporate-actions planned (F-014)
/admin/data-import       already exists
/admin/users             F-016
/admin/roles             F-016
/admin/deleted-records   already exists
/admin/companies-refresh F-019 NGX data refresh trigger

Read-only for all users (no edit controls anywhere on these pages):
  /dashboard /holdings /companies /dividends
  /price-history /transactions /registrars /watchlist

Hidden from read-only users entirely:
  /nav-history /rebalancing /admin/*

---

## Priority Order (Next Sprint)

1.  Fix BUG-001 through BUG-005
2.  F-007 NAV History
6.  F-012 Watchlist
7.  F-013 Companies + Company Profile
8.  F-008 Dividends
9.  F-009 Transactions
10. F-010 Claims
