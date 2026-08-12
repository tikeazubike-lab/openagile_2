# progress-tracker.md — EPM Progress Tracker

**Last updated**: 2026-07-04

---

## Current Phase

Phase 3 — Core pages + Admin restructure + New features
Environment: testdrive.epm.zubbystudio.shop (openagile_2 codebase)

---

## Active Work

**Current priority shift:** Build all pages minimally first (working data + UI), then cycle back for details/bugs/drill-downs.

**New order:** Start with F-010 Claims (which = Dividends in EPM's domain model — see HO-031). F-008 merged into F-010.

---

## Feature Status

### Phase 2-3A (Foundation + Core Trading)

| ID    | Feature         | Status        | Last HO  | Notes                             |
|-------|-----------------|---------------|----------|-----------------------------------|
| F-001 | Authentication  | ✅ Complete   | HO-008   | 30-day cookie, logout fixed       |
|| F-002 | Dashboard       | ⚠️ Bugs open  | AT-003-1 | Charts blank (BUG-001 fixed), bell (BUG-005 deferred)|
| F-003 | Holdings        | ⚠️ Bugs open  | AT-003-1 | Inline edit cursor (BUG-002 fixed), Add 500 (BUG-003 fixed) |
| F-004 | Price Entry     | ✅ Complete   | AT-001   | PDF parser, CSV, audit log        |
| F-005 | Price History   | ✅ Complete   | AT-003-1 | Chart, table, date filter         |
| F-006 | Registrars      | ✅ Complete   | AT-002   | Docs, requirements, linking       |

### Phase 3B (Admin Restructure)

| ID     | Feature                    | Status   | Notes                                              |
|--------|----------------------------|----------|----------------------------------------------------|
| F-NGX-COMPANIES | NGX Listed Companies PDF Upload | ✅ Complete | Backend + frontend deployed. PDF parse, upsert    |
| F-COST-BASIS    | Historical Cost Basis Upload   | ✅ Complete | Quick form + CSV. 3-step ticker matching, claim auto-create |
| F-003b | Holdings Admin Edit View   | PLANNED  | /admin/holdings replaces inline edit toggle        |
| F-006b | Registrars Admin Edit View | PLANNED  | /admin/registrars replaces inline edit toggle      |
| F-017  | Remove editMode toggle     | PLANNED  | Delete uiStore.editMode, role guards replace it    |

### Phase 3C (New Core Features)

| ID    | Feature         | Status   | Notes                                              |
|-------|-----------------|----------|----------------------------------------------------|
| F-016 | User Management | ✅ Complete | HO-026   | Backend CRUD + frontend deployed. Reports/hidden for deactivated users (SUPERADMIN only). Admin-only creation.
| F-007 | NAV History     | PLANNED  | Gherkin SC-025-031 written. Needs scipy, APScheduler |
| F-008 | Dividends       | MERGED INTO F-010 | Claim = Dividend in EPM domain. F-010 replaces both |
| F-009 | Transactions    | PLANNED  | CRUD + auto-generate from holdings                 |
| F-010 | Claims          | ✅ BUILT | HO-031 | Dividend tracking dashboard. ClaimRecord = dividend record. Deployed to testdrive. |
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
| F-021 | Production Cutover  | PLANNED  | DNS cutover to production               |

### Phase 4 (Future — Not Yet Specced)

| ID       | Feature                   | Notes                                        |
|----------|---------------------------|----------------------------------------------|
| F-P4-01  | Stock Purchase Workflow   | Registrar + calendar + inbox — needs design  |
| F-P4-02  | Multi-portfolio           | Separate portfolios per user                 |
| F-P4-03  | Eurobonds / Real Estate   | Asset abstraction layer                      |
|| F-P4-04  | Export to Excel           | Tax filing aid                               |
|| F-022    | AI Assisted Interactive ChatBot | Blocked on F-007–F-016 |

---

## Open Bugs (fix before Phase 3C)

| ID      | Feature   | Description                       | Status     |
|---------|-----------|-----------------------------------|------------|
| BUG-001 | Dashboard | Charts blank (Recharts data shape)| ✅ Fixed   |
| BUG-002 | Holdings  | Inline edit cursor jumps          | ✅ Fixed   |
| BUG-003 | Holdings  | POST /api/v1/holdings 500 error   | ✅ Fixed   |
| BUG-004 | Dashboard | Theme toggle icon static          | ✅ Fixed   |
|| BUG-005 | Dashboard | Bell not showing action items     | ⏳ Deferred |

---

## Missing Dependencies (add to requirements.txt before implementing)

```
scipy==1.13.1          needed for F-007 XIRR
APScheduler==3.10.4    needed for F-007 NAV snapshot + F-019 NGX refresh
beautifulsoup4==4.12.3 needed for F-013 NGX companies scraper
feedparser==6.0.11     needed for F-018 RSS news feeds
praw==7.7.1            needed for F-018 Reddit API
```

---

## Admin Section Navigation Map

| Route | Purpose |
|-------|---------|
| /admin/holdings | All Holdings CRUD (replaces inline edit toggle) |
| /admin/registrars | All Registrar CRUD (replaces inline edit toggle) |
|| /admin/data-upload | Renamed from price-entry. Prices, Companies + Cost Basis tabs |
| /admin/corporate-actions | Planned (F-014) |
| /admin/data-import | Already exists |
| /admin/users | F-016 |
| /admin/roles | F-016 |
| /admin/deleted-records | Already exists |
| /admin/companies-refresh | F-019 NGX data refresh trigger |

**Read-only for all users** (no edit controls anywhere):
/dashboard /holdings /companies /claims /price-history /transactions /registrars /watchlist

**Hidden from read-only users entirely:**
/nav-history /rebalancing /admin/*

---

## Priority Order (Active Sprint)

1. ~~F-016 User Management~~ ✅ Done
2. ~~F-010 Claims (Dividend Tracking)~~ ✅ Done — HO-031
3. Run BUG-AT-001 + BUG-AT-002 acceptance (F-NGX-COMPANIES + F-COST-BASIS)
4. F-017 Remove editMode toggle — spec needed
5. F-009 Transactions
6. F-012 Watchlist
7. F-013 Companies + Company Profile
8. F-007 NAV History (needs scipy dep added first)
