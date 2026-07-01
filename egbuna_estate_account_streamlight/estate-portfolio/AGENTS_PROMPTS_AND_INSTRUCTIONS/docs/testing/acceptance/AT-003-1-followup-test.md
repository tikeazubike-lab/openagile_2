---
type: AT
id: AT-003-1
title: Dashboard, Holdings, Registrars, Price History — Follow-Up Test Run
status: PENDING
version: 1.0
created: 2026-05-19
tester: [fill in]
environment: demo.estate.zubbystudio.shop
branch: test
parent: AT-003
fixes_from: HO-011 through HO-016
related: SC-UI-001 through SC-UI-046
---

# [AT] AT-003-1 — Follow-Up Test Run
> **Type**: Acceptance Test · **Status**: 🟡 PENDING
> **Parent**: AT-003 (original run)
> **Purpose**: Verify all fixes from HO-011 to HO-016. Carries over
> all FAIL, PENDING, and SKIP items from AT-003.

---

## How to Use This Document

Only re-test items that were FAIL, PENDING, or SKIP in AT-003.
Items already marked PASS in AT-003 are not repeated here unless
a fix in HO-011 to HO-016 could have regressed them.

Mark each item:
- `[x]` PASS
- `[fail]` FAIL: describe what happened
- `[skip]` SKIP: state reason
- `[pending]` not yet tested

---

## SECTION 1 — Dashboard Page [/dashboard]

*Items previously PASS in AT-003 that may have been affected by dashboard fixes:*

### Charts (were BLANK in AT-003 — primary fix in HO-015)
- [ ] SC-UI-009: Sector allocation donut renders with coloured segments and percentage labels
- [ ] SC-UI-010: Segment sizes reflect ₦ value of holdings (not count of stocks)
- [ ] SC-UI-011: Top Holdings chart shows bars by current value (₦) on page load; "By Value" toggle active
- [ ] SC-UI-012: Clicking "By Shares" changes bars to num_shares; toggle switches correctly
- [ ] SC-UI-013: Chart shows at most 10 holdings

### Recent Transactions (showed zeroes in AT-003 — fixed in HO-014)
- [ ] SC-UI-014: Recent transactions card shows real data — Date, Ticker, Type, Shares, Amount — not zeroes
- [ ] SC-UI-015: Empty state renders correctly when no transactions exist

### Action Items (was throwing errors in AT-003 — fixed in HO-014)
- [ ] SC-UI-016: Draft holdings alert appears and links to /holdings
- [ ] SC-UI-017: Stale price alert appears when prices > 7 days old
- [ ] SC-UI-018: All-clear state shows green checkmark when nothing pending
- [ ] SC-UI-019: Approved claim alert appears when a claim has status "approved"

### Previously Passing — Regression Check
- [ ] SC-UI-001: Edit mode toggle NOT visible on Dashboard (regression guard)
- [ ] SC-UI-003: Theme toggle switches light → dark
- [ ] SC-UI-006: Bell badge shows count when action items exist
- [ ] SC-UI-007: Bell dropdown shows last 5 items; clicking outside closes it

---

## SECTION 2 — Holdings Page [/holdings]

### Inline Editing (was 500 error in AT-003 — primary fix in HO-015)
- [ ] SC-UI-024: Changing Shares and clicking Save calls PATCH correctly; row updates in place with new values
- [ ] SC-UI-024b: Check DevTools Network tab — request body contains `avg_purchase_price` as a string (e.g. `"400.00"`), not `avg_cost` as a float
- [ ] SC-UI-025: Clicking Cancel discards changes; row returns to original values; no API call made
- [ ] SC-UI-026: Entering negative Shares shows client-side validation error on the row; Save button blocked; no API call made
- [ ] SC-UI-026b: Entering "0" for avg cost shows client-side error; no API call made

### Add Holding Drawer (was inline row, redesigned in HO-011)
- [ ] SC-UI-027: Clicking [+ Add Holding] opens a slide-out drawer from the right; holdings table remains visible
- [ ] SC-UI-027b: Pressing Escape or clicking × closes the drawer; no API call; form resets
- [ ] SC-UI-028: Filling Company, Shares, Avg Cost and clicking Save as Draft creates holding with status "draft"; DRAFT badge appears
- [ ] SC-UI-028b: Clicking Save & Publish creates holding with status "live"; LIVE badge appears
- [ ] SC-UI-029: Adding a holding for a company that already exists shows error in drawer; no API call

### Edit Mode Reset (was leaving stale inputs in AT-003 — fixed in HO-012)
- [ ] SC-UI-022b: Toggling edit mode OFF while a row is being edited clears the inline inputs immediately; no stale form visible

### Delete Holding (was not persisting in AT-003 — fixed in HO-012)
- [ ] SC-UI-031: Clicking Delete shows confirmation dialog; confirming removes row from table; refresh confirms row is gone from database

### Previously Passing — Regression Check
- [ ] SC-UI-020: All columns visible including exact header "return[%]"
- [ ] SC-UI-021: Computed columns (Curr Value, Cost Basis, return[%]) show correct values
- [ ] SC-UI-030: Publish button on draft row changes badge to LIVE; dashboard total updates

---

## SECTION 3 — Registrars Page [/registrars]

### Company Linking (was 405 in AT-003 — fixed in HO-008, verify persists)
- [ ] SC-UI-032: Linking a company returns HTTP 200; company appears in Linked Companies card
- [ ] SC-UI-033: Unlinking a company removes it from the card; count badge decrements

### Extended Contact Fields (layout was "horrible" in AT-003 — fixed in HO-014)
- [ ] SC-UI-034: [+ Add Field] shows type selector: phone, email, address, website, other
- [ ] SC-UI-035: Adding a second phone field shows in 3-column grid layout (badge | input | × button); readable and aligned
- [ ] SC-UI-036: Adding website field saves and shows clickable URL in detail panel

### Modal (was off-center in AT-003 — fixed in HO-014)
- [ ] SC-UI-034b: Edit Registrar modal is centered on screen (not pushed to one side)
- [ ] SC-UI-037: Add Registrar modal is also centered; has [+ Add Field] button

### Delete Registrar (button was missing in AT-003 — fixed in HO-014)
- [ ] SC-UI-038: [Delete] button (red/danger) is visible next to [Edit Registrar] in detail panel when edit mode ON
- [ ] SC-UI-039: Clicking Delete shows confirmation; confirming removes registrar from left panel
- [ ] SC-UI-040: Confirmation mentions number of linked companies if any exist

---

## SECTION 4 — Price History Page [/price-history]

### Searchable Dropdown (was plain select in AT-003 — fixed in HO-014)
- [ ] SC-UI-041: Company dropdown is searchable — typing filters the list by ticker or name

### Chart Loading (was not loading in AT-003 — fixed in HO-014)
- [ ] SC-UI-042: Selecting a company loads a line chart in lavender colour
- [ ] SC-UI-042b: Chart shows price on Y-axis and date on X-axis with correct data points

### Table (was missing in AT-003 — fixed in HO-014)
- [ ] SC-UI-043: A table appears below the chart showing Date, Price (₦), Source with source badges

### Date Range Filter
- [ ] SC-UI-044: Clicking "30D" filter shows only last 30 days of data

### Empty State
- [ ] SC-UI-045: Selecting a company with no price records shows empty state message (not blank/broken chart)

### Access Control
- [ ] SC-UI-046: Readonly user can access /price-history and view data; no edit controls

---

## SECTION 5 — New Verifications (Not in AT-003)

These verify fixes introduced in HO-011 to HO-016 that have no
parent test in AT-003:

### Dashboard API Contract
- [ ] NEW-001: GET /api/v1/dashboard response — `sector_allocation` entries have `"name"` field (not just `"sector"`)
- [ ] NEW-002: GET /api/v1/dashboard response — `value` in sector_allocation is a JSON string (e.g. `"1500000.00"`) not a float
- [ ] NEW-003: GET /api/v1/dashboard response — `value` in top_holdings is a JSON string not a float

### Holdings PATCH API Contract
- [ ] NEW-004: PATCH /api/v1/holdings/{id} with `{"avg_purchase_price": "400.00", "num_shares": 100}` returns 200
- [ ] NEW-005: PATCH /api/v1/holdings/{id} with `{"avg_purchase_price": "-5.00"}` returns 422
- [ ] NEW-006: PATCH /api/v1/holdings/{id} with `{"num_shares": 0}` returns 422

### PDF Date Extraction
- [ ] NEW-007: Uploading a PDF named "DAILY SUMMARY FOR 17-05-2026.pdf" creates price_history records dated 2026-05-17 (not today)
- [ ] NEW-008: Uploading a PDF with no recognisable date in filename falls back to today's date (no crash)

### Soft Delete Timezone
- [ ] NEW-009: After soft-deleting a holding, refreshing the page confirms the holding does not reappear

---

## Issues Found

| ID | Page | SC Reference | Description | Severity | Fix Needed |
|----|------|-------------|-------------|----------|------------|
| | | | | | |

---

## Summary Table

| Section | Total Items | Pass | Fail | Skip | Pending |
|---------|-------------|------|------|------|---------|
| Dashboard | 15 | | | | |
| Holdings | 14 | | | | |
| Registrars | 10 | | | | |
| Price History | 6 | | | | |
| New Verifications | 9 | | | | |
| **TOTAL** | **54** | | | | |

---

## Sign-Off

- [ ] All items from AT-003 that were FAIL are now PASS
- [ ] No regressions introduced in previously passing items
- [ ] PROJECT_STATUS.md updated with results
- [ ] Ready to proceed to Phase 3C (NAV History, Dividends, Transactions)

**Tested by**: _______________
**Date**: _______________
**Result**: PASS / FAIL / PARTIAL
