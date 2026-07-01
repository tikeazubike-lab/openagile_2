# EPM — Project Status Board
**Maintained by**: Claude (The Brain)
**Last updated**: 2026-05-18
**Source**: All handovers HO-001 through HO-011 + AT-001 through AT-003
**Branch**: test → main

---

## Legend
```
✅ DONE        — implemented, tested, deployed to demo.estate.zubbystudio.shop
⚠️ PARTIAL     — built but has known bugs or incomplete features
🔄 IN PROGRESS — currently being worked on (this sprint)
📋 PLANNED     — designed and specced, not yet built
🔮 FUTURE      — identified need, not yet designed (Phase 4+)
❌ REMOVED     — was in scope, deliberately cut
```

---

## INFRASTRUCTURE & CI/CD

| Item | Status | Notes |
|------|--------|-------|
| Docker single-container (FastAPI + React static) | ✅ DONE | Multi-stage build |
| Traefik SSL routing | ✅ DONE | demo.estate.zubbystudio.shop |
| Shared openagile_postgres | ✅ DONE | estate_portfolio DB |
| GitHub Actions fast-path CI | ✅ DONE | Static analysis + build + deploy |
| GitHub Actions full-path CI | ⚠️ PARTIAL | Unit tests not yet fully wired |
| SSH heredoc quote fix (ENDSSH) | ✅ DONE | << 'ENDSSH' |
| bcrypt==4.0.1 pin | ✅ DONE | passlib compatibility fixed |
| EODHD scraper removed from CI | ✅ DONE | Replaced with API health check |
| epm-tests/ reinstated in repo | 📋 PLANNED | Was gitignored — needs reinstatement |
| Test schema isolation (estate_portfolio_test) | 📋 PLANNED | For CI integration tests |
| Branch protection rules on main | ⚠️ PARTIAL | Free GitHub account — manual discipline only |
| AGENTS.md (EPM-level) | ✅ DONE | In estate-portfolio/ subdirectory |
| .cursor/rules/ (4 rule files) | ✅ DONE | backend, frontend, infrastructure, general |
| Cursor onboarding (CURSOR_FIRST_STEPS.md) | ✅ DONE | |
| docs/ folder structure (governance) | ✅ DONE | BR, ADR, TC, AT, HO naming convention |
| GitHub Wiki | ❌ REMOVED | Free account limitation — replaced by docs/README.md |
| Obsidian vault → private GitHub repo sync | 📋 PLANNED | vault-sync.yml not yet created |
| Stooq scraper standalone script | 📋 PLANNED | scripts/stooq_scraper/ — documented in README |

---

## PHASE 2A — Foundation (COMPLETE)

| Item | Status | Notes |
|------|--------|-------|
| FastAPI app skeleton | ✅ DONE | app/main.py, config, database |
| SQLAlchemy async + asyncpg | ✅ DONE | |
| Alembic migrations (base schema) | ✅ DONE | |
| JWT auth (httpOnly cookie, 30-day) | ⚠️ PARTIAL | 30-day restored but verify Max-Age in response |
| Users table + seed_admin.py | ✅ DONE | Idempotent, reads from env vars |
| Login / logout / /me endpoints | ✅ DONE | |
| beforeLoad hydration (_app.tsx) | ✅ DONE | GET /me on mount |
| Logout bug fix (sidebar sequence) | ✅ DONE | API first → clearUser → navigate |
| React skeleton (Vite + TypeScript) | ✅ DONE | TanStack Start file-based routing |
| Tailwind v4 + oklch tokens | ✅ DONE | |
| Design system (light/dark CSS vars) | ✅ DONE | |
| Theme toggle (system + dark override) | ⚠️ PARTIAL | Renders but onClick not wired — HO-009 fix |
| authStore + uiStore (Zustand) | ✅ DONE | |
| useTheme hook (anti-FOUC) | ✅ DONE | |
| TanStack Router file-based routing | ✅ DONE | src/routes/ |
| Protected route guard | ✅ DONE | |
| Login page | ✅ DONE | |
| Sidebar navigation | ✅ DONE | |
| Navbar | ✅ DONE | |
| Traefik label for demo subdomain | ✅ DONE | |

---

## PHASE 2B — Core Data Pages (PARTIAL)

| Item | Status | Notes |
|------|--------|-------|
| **Dashboard** | | |
| Dashboard API endpoint (KPIs) | ✅ DONE | Dynamic aggregations |
| Dashboard React page (4 KPI cards) | ✅ DONE | |
| Count-up animation (KPI values) | ✅ DONE | useCountUp hook |
| Edit mode toggle hidden on Dashboard | ✅ DONE | HO-009 fix |
| Sector allocation donut chart | ✅ DONE | |
| Top Holdings bar chart | ✅ DONE | |
| Top Holdings By Value / By Shares toggle | ✅ DONE | HO-009 |
| Recent Transactions card | ✅ DONE | |
| Action Items card | ✅ DONE | useActionItems() hook |
| Notification bell dropdown | ✅ DONE | HO-009 |
| Dashboard total_assets (active + claims) | 📋 PLANNED | Needs Phase 2B claims data |
| Dashboard claims_summary | 📋 PLANNED | |
| | | |
| **Holdings** | | |
| Holdings API endpoint (list + computed fields) | ✅ DONE | return_pct, current_value etc |
| Holdings React page (TanStack Table) | ✅ DONE | |
| return[%] exact column header | ✅ DONE | |
| Draft/live row treatment (amber border) | ✅ DONE | |
| Edit mode (Actions column) | ✅ DONE | |
| Inline row editing | ✅ DONE | |
| Global edit mode reset bug | 🔄 IN PROGRESS | useEffect fix — HO-011 |
| Delete holding bug | 🔄 IN PROGRESS | Investigating mutation — HO-011 |
| Add Holding — inline row (REMOVED) | ❌ REMOVED | Too clunky per AT-003 |
| Add Holding — slide-out drawer | 🔄 IN PROGRESS | HO-011 redesign |
| Publish draft holding | ✅ DONE | |
| Soft delete + restore | ✅ DONE | |
| Dual Holdings table (Active + Claims) | 📋 PLANNED | Phase 2B — needs import_obsidian data |
| Claims portfolio subtotal | 📋 PLANNED | |
| Grand total assets row | 📋 PLANNED | |
| Div Yield column computed | ⚠️ PARTIAL | Field added, formula verify needed |
| XIRR per holding | 📋 PLANNED | Gherkin spec written (SC-032–SC-037) |
| Holdings pagination (25 rows) | ⚠️ PARTIAL | Spec says 25/page — verify implemented |
| | | |
| **Companies** | | |
| Companies API (list) | ✅ DONE | GET /api/v1/companies |
| Companies React page | 📋 PLANNED | CRUD UI not yet built |
| Sector badge colours | ✅ DONE | Consistent across pages |
| Registrar link in companies table | 📋 PLANNED | Depends on Companies page |
| | | |
| **Price Entry** | | |
| Quick price entry endpoint | ✅ DONE | POST /api/v1/prices/quick |
| Quick price entry UI | ✅ DONE | |
| Price audit log (last 20) | ✅ DONE | |
| Revert price change | ✅ DONE | |
| Bulk CSV import (2-stage) | ✅ DONE | preview → commit |
| CSV column mapping | ✅ DONE | flexible header normalisation |
| NGX PDF upload + parser | ✅ DONE | Right-to-left parsing, fuzzy name match |
| Client-side 20MB file size guard | ✅ DONE | |
| PDF upload writes to price_history | ⚠️ PARTIAL | Verify — may only update current_price |
| Batch historical PDF upload | 📋 PLANNED | Phase 3C — SC-045/SC-046 specced |
| Stooq scraper reference in README | 📋 PLANNED | |
| | | |
| **Price History** | | |
| Price history API endpoint | ✅ DONE | GET /api/v1/prices/history/{id} |
| Price History React page | ✅ DONE | HO-009 |
| Company selector (searchable) | ✅ DONE | |
| Line chart (lavender) | ✅ DONE | |
| Date range filter pills | ✅ DONE | |
| Source badges in table | ✅ DONE | |
| Empty state | ✅ DONE | |
| Historical data population (manual) | 🔄 IN PROGRESS | User uploading past 30 days PDFs |
| | | |
| **Registrars** | | |
| Registrars API (list + CRUD) | ✅ DONE | |
| Company linking endpoints | ✅ DONE | 405 fix deployed (HO-008) |
| Registrars React page (two-panel) | ✅ DONE | |
| Linked companies card | ✅ DONE | |
| Requirements accordion | ✅ DONE | |
| Document upload (per requirement) | ✅ DONE | PDF/JPG/PNG, 20MB max |
| Document download (auth-gated) | ✅ DONE | |
| Document version history | ✅ DONE | |
| Document status tracking | ✅ DONE | pending/submitted/completed/rejected |
| Delete requirement | ✅ DONE | |
| Delete registrar | ✅ DONE | HO-009 |
| Extended contact fields (multi phone/email) | ✅ DONE | registrar_contact_fields table |
| Edit Registrar modal with field types | ✅ DONE | |
| Linked companies as clickable pills | 📋 PLANNED | Needs Companies page first |

---

## PHASE 3A — Price Entry Complete ✅

*(Already captured above — Price Entry and Price History sections)*

---

## PHASE 3B — Registrars + Document Management ✅

*(Already captured above — Registrars section)*

---

## PHASE 3C — Remaining Pages (CURRENT SPRINT)

| Item | Status | Notes |
|------|--------|-------|
| **Dividends** | | |
| Dividends API (CRUD + annual summary) | 📋 PLANNED | Endpoint spec in Final Handover Part B |
| Dividends React page (3 tabs) | 📋 PLANNED | All / Annual Summary / Import CSV |
| WHT configurable per entry | 📋 PLANNED | Default 10%, user can change |
| DRIP (scrip dividend) tracking | 📋 PLANNED | is_scrip + scrip_shares fields |
| Annual summary for tax filing | 📋 PLANNED | |
| | | |
| **Transactions** | | |
| Transactions API (CRUD) | 📋 PLANNED | Includes auto-generation from holdings |
| Transactions React page | 📋 PLANNED | |
| Auto-generated rows from Holdings create | 📋 PLANNED | |
| Auto-generated rows from Corporate Actions | 📋 PLANNED | |
| Draft/live on transactions | 📋 PLANNED | |
| CSV bulk import | 📋 PLANNED | |
| | | |
| **NAV History** | | |
| NAV history API + APScheduler | 📋 PLANNED | 18:00 WAT daily + price-update trigger |
| NAV History React page | 📋 PLANNED | Area chart, period filter, stats row |
| Manual snapshot trigger | 📋 PLANNED | Admin only |
| Gherkin spec | ✅ DONE | SC-025 through SC-031 |
| | | |
| **Rebalancing** | | |
| Sector targets table + API | 📋 PLANNED | |
| Rebalancing gap computation | 📋 PLANNED | |
| Rebalancing React page | 📋 PLANNED | Visual bar + gap table |
| Edit Targets drawer | 📋 PLANNED | Must sum to 100% |
| | | |
| **Watchlist** | | |
| Watchlist API (CRUD) | 📋 PLANNED | |
| Watchlist React page | 📋 PLANNED | Gap to target column |
| Add to Holdings shortcut | 📋 PLANNED | One-click pre-fill |
| | | |
| **Claims** | | |
| ClaimRecord table (Alembic) | 📋 PLANNED | Phase 2B spec written |
| Claims API (CRUD) | 📋 PLANNED | |
| Claims React page | 📋 PLANNED | |
| Claims portfolio subtotal | 📋 PLANNED | |
| AMCON/CAC reference tracking | 📋 PLANNED | |
| | | |
| **Corporate Actions** | | |
| Corporate Actions table (Alembic) | 📋 PLANNED | bonus, rights, split, merger |
| Corporate Actions API | 📋 PLANNED | Auto-generates transaction rows |
| Corporate Actions React page | 📋 PLANNED | |
| | | |
| **Obsidian Import** | | |
| import_obsidian.py script | 📋 PLANNED | Full spec in Phase 2B architecture doc |
| Dry-run mode | 📋 PLANNED | |
| Vault sync pipeline (GitHub Actions) | 📋 PLANNED | vault-sync.yml in private vault repo |
| VPS vault mirror setup | 📋 PLANNED | One-time Antigravity setup |
| obsidian_sync_log table | 📋 PLANNED | |
| | | |
| **Batch PDF Upload** | | |
| POST /api/v1/prices/batch-upload-pdf | 📋 PLANNED | SC-045/SC-046 specced |
| Batch upload UI (multi-file drop zone) | 📋 PLANNED | Second tab in Price Entry |
| | | |
| **XIRR** | | |
| scipy added to requirements.txt | 📋 PLANNED | scipy==1.13.1 |
| calculate_xirr() in portfolio.py | 📋 PLANNED | brentq implementation specced |
| xirr_pct field in Holdings response | 📋 PLANNED | null if < 2 transactions |
| Gherkin spec | ✅ DONE | SC-032 through SC-037 |

---

## PHASE 3D — Settings Pages

| Item | Status | Notes |
|------|--------|-------|
| Settings: User Management | 📋 PLANNED | Add/deactivate users, reset passwords |
| Settings: Deleted Records | 📋 PLANNED | Restore soft-deleted items |
| Settings: Data Import | 📋 PLANNED | Obsidian import trigger UI |
| Settings: Sector Targets | 📋 PLANNED | For rebalancing page |

---

## PHASE 3E — Cutover to Production

| Item | Status | Notes |
|------|--------|-------|
| All 16 pages implemented | 📋 PLANNED | |
| Real API queries (no mock data) | ✅ DONE | |
| authStore initial state = null | ✅ DONE | |
| Skip to demo link removed | ✅ DONE | |
| fmtNaira moved to lib/format.ts | ✅ DONE | |
| Stooq scraper in scripts/ with README | 📋 PLANNED | |
| Old Streamlit container stopped | 📋 PLANNED | |
| estate.zubbystudio.shop → new app | 📋 PLANNED | DNS/Traefik cutover |
| MASTER_CONTEXT.md updated | ⚠️ PARTIAL | v4.0 done, needs Phase 3 additions |

---

## PHASE 4 — Future (Not Yet Designed)

| Item | Status | Notes |
|------|--------|-------|
| Multi-portfolio (separate portfolios per user) | 🔮 FUTURE | Requires row-level isolation design |
| Eurobonds / fixed income tracking | 🔮 FUTURE | Needs Asset abstraction layer |
| Real estate tracking | 🔮 FUTURE | Property asset type |
| Treasury bills / money market | 🔮 FUTURE | Maturity date tracking |
| NGX index benchmark comparison | 🔮 FUTURE | |
| Mobile responsive polish | 🔮 FUTURE | Bottom nav, table scroll |
| Export to Excel (tax purposes) | 🔮 FUTURE | openpyxl |
| Annual dividend summary export | 🔮 FUTURE | Tax filing aid |

---

## TEST COVERAGE STATUS

| Stage | Status | Count |
|-------|--------|-------|
| Unit tests — frontend (vitest) | ✅ DONE | 21 tests passing |
| Unit tests — backend (pytest) | ✅ DONE | 12 tests passing |
| Gherkin specs written | ✅ DONE | 46 scenarios (SC-001 to SC-046 excl UI) + SC-UI-001 to SC-UI-046 |
| Integration tests | 📋 PLANNED | Blocked on test schema setup |
| E2E Playwright | 📋 PLANNED | |
| Performance (Locust) | 📋 PLANNED | |
| AT-001 (Price Entry) | ✅ DONE | All P0 items passing |
| AT-002 (Registrars) | ⚠️ PARTIAL | Some items pending / fixed |
| AT-003 (Dashboard/Holdings/Registrars/PriceHist) | 🔄 IN PROGRESS | Bugs being fixed |

---

## KNOWN BUGS (Open)

| # | Page | Bug | Status | HO Reference |
|---|------|-----|--------|-------------|
| 1 | Holdings | Delete mutation not persisting | 🔄 Investigating | HO-011 |
| 2 | Holdings | Edit mode off doesn't clear inline fields | 🔄 Fix in progress | HO-011 |
| 3 | Price Entry | PDF upload may not write to price_history | ⚠️ Verify needed | HO-011 |
| 4 | Auth | 30-day cookie Max-Age — verify in Set-Cookie header | ⚠️ Verify needed | HO-011 |

---

## WHAT TO WORK ON NEXT (Priority Order)

```
THIS SPRINT (P0 — fix before adding features):
  1. Fix Holdings delete mutation bug
  2. Fix editMode reset useEffect
  3. Build AddHoldingDrawer (slide-out, replaces inline row)
  4. Verify price_history write in PDF upload endpoint
  5. Complete AT-003 re-run after fixes

NEXT SPRINT (Phase 3C — in this order):
  6. NAV History (APScheduler + page)
  7. Dividends (API + page)
  8. Transactions (API + page)
  9. Claims (table + API + page)
  10. Obsidian import (import_obsidian.py + vault sync)

FOLLOWING SPRINT:
  11. Rebalancing
  12. Watchlist
  13. Corporate Actions
  14. XIRR (scipy)
  15. Batch PDF upload
  16. Settings pages

FINAL SPRINT (cutover):
  17. Companies CRUD page
  18. Production cutover (estate.zubbystudio.shop)
```

---

**This document should be updated after every HO handover.**
**File location**: `docs/PROJECT_STATUS.md` in the estate-portfolio repo.
