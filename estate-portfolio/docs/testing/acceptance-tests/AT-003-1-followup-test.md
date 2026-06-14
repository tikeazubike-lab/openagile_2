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
- [fail] SC-UI-009: Sector allocation donut renders with coloured segments and percentage labels. reason: no donut nor graph displayed
- [fail] SC-UI-010: Segment sizes reflect ₦ value of holdings (not count of stocks). reason: no bar nor graph displayed
- [fail] SC-UI-011: Top Holdings chart shows bars by current value (₦) on page load; "By Value" toggle active. reason: no bars displayed.
- [skipped] SC-UI-012: Clicking "By Shares" changes bars to num_shares; toggle switches correctly
- [skipped] SC-UI-013: Chart shows at most 10 holdings

### Recent Transactions (showed zeroes in AT-003 — fixed in HO-014)
- [fail] SC-UI-014: Recent transactions card shows real data — Date, Ticker, Type, Shares, Amount — not zeroes. no transactions displayed
- [skip] SC-UI-015: Empty state renders correctly when no transactions exist

### Action Items (was throwing errors in AT-003 — fixed in HO-014)
- [pending] SC-UI-016: Draft holdings alert appears and links to /holdings
- [pending] SC-UI-017: Stale price alert appears when prices > 7 days old
- [pending] SC-UI-018: All-clear state shows green checkmark when nothing pending
- [pending] SC-UI-019: Approved claim alert appears when a claim has status "approved"
reason: The feature above has not been built

### Previously Passing — Regression Check
- [x] SC-UI-001: Edit mode toggle NOT visible on Dashboard (regression guard)
- [fail] SC-UI-003: Theme toggle switches light → dark. reason: the icon doesn't change on click. it stays as sun(I think it might be that the system has a default dark theme throughout the day, so the icon reflect the present state of the sytem, but might it not be better to give the user the proper feedback on the actions they are taking?)
- [fail] SC-UI-006: Bell badge shows count when action items exist
- [fail] SC-UI-007: Bell dropdown shows last 5 items; clicking outside closes it

---

## SECTION 2 — Holdings Page [/holdings]

### Inline Editing (was 500 error in AT-003 — primary fix in HO-015)
- [fail] SC-UI-024: Changing Shares and clicking Save calls PATCH correctly; row updates in place with new values. reason: The ux is still below par.
    - first when the the edit button is clicked and the inline edit too, it shows a cell without the increment/decrement arrow
    - once i start typing the number to change the original value, for example in okomu oil[1530 -> 1560], the cursor keeps jumping out of the cell
- [fail] SC-UI-024b: Check DevTools Network tab — request body contains `avg_purchase_price` as a string (e.g. `"400.00"`), not `avg_cost` as a float. reason: on save shows this error: api/v1/auth/me:1  Failed to load resource: the server responded with a status of 401 ()

- [fail] SC-UI-025: Clicking Cancel discards changes; row returns to original values; no API call made. reason: no cancel button visible.
- [skipped] SC-UI-026: Entering negative Shares shows client-side validation error on the row; Save button blocked; no API call made
- [skipped] SC-UI-026b: Entering "0" for avg cost shows client-side error; no API call made

### Add Holding Drawer (was inline row, redesigned in HO-011)
- [x] SC-UI-027: Clicking [+ Add Holding] opens a slide-out drawer from the right; holdings table remains visible
- [x] SC-UI-027b: Pressing Escape or clicking × closes the drawer; no API call; form resets
- [fail] SC-UI-028: Filling Company, Shares, Avg Cost and clicking Save as Draft creates holding with status "draft"; DRAFT badge appears. Reason: "queries-eMM2o_QQ.js:1  POST https://demo.estate.zubbystudio.shop/api/v1/holdings 500 (Internal Server Error)"

- [fail] SC-UI-028b: Clicking Save & Publish creates holding with status "live"; LIVE badge appears. Reason: queries-eMM2o_QQ.js:1  POST https://demo.estate.zubbystudio.shop/api/v1/holdings 500 (Internal Server Error)
...

- [skipped] SC-UI-029: Adding a holding for a company that already exists shows error in drawer; no API call. Reason: This test builds on the previous tests, which are not working.

### Edit Mode Reset (was leaving stale inputs in AT-003 — fixed in HO-012)
- [x] SC-UI-022b: Toggling edit mode OFF while a row is being edited clears the inline inputs immediately; no stale form visible

### Delete Holding (was not persisting in AT-003 — fixed in HO-012)
- [fail] SC-UI-031: Clicking Delete shows confirmation dialog; confirming removes row from table; refresh confirms row is gone from database. Reason: This test builds on the previous tests, which are not working. Reason: confirm but fails to save the changes. Error: queries-eMM2o_QQ.js:1  DELETE https://demo.estate.zubbystudio.shop/api/v1/holdings/2 500 (Internal Server Error)
S @ queries-eMM2o_QQ.js:1
...
$v @ index-F2uLzylf.js:10
queries-eMM2o_QQ.js:1 Uncaught (in promise) Error: Request failed (500)
...
$v @ index-F2uLzylf.js:10


### Previously Passing — Regression Check
- [x] SC-UI-020: All columns visible including exact header "return[%]"
- [fail] SC-UI-021: Computed columns (Curr Value, Cost Basis, return[%]) show correct values. Reason: All computed values are either showing "-" or "" or "0.00". None of them are showing the correct values. 
- [fail] SC-UI-030: Publish button on draft row changes badge to LIVE; dashboard total updates. Reason: This test builds on the previous tests, which are not working. 

---

## SECTION 3 — Registrars Page [/registrars]

### Company Linking (was 405 in AT-003 — fixed in HO-008, verify persists)
- [skipped] SC-UI-032: Linking a company returns HTTP 200; company appears in Linked Companies card. Reason: The 
- [ ] SC-UI-033: Unlinking a company removes it from the card; count badge decrements

### Extended Contact Fields (layout was "horrible" in AT-003 — fixed in HO-014)
- [x] SC-UI-034: [+ Add Field] shows type selector: phone, email, address, website, other
- [fail] SC-UI-035: Adding a second phone field shows in 3-column grid layout (badge | input | × button); readable and aligned. Reason Adds second phone number, but the UI is horribe. The second number is currently on the same line and the far right end of where the first number is. I wanted the information to be displayed below each other with the title of each field highlighted in bold legible font and the values in non bold underneath it.
 for example:
    **Phone**:
      xxxx-yyyyyyyyyy
      aaaa-bbbbbbbbbb 

- [x] SC-UI-036: Adding website field saves and shows clickable URL in detail panel

### Modal (was off-center in AT-003 — fixed in HO-014)
- [x] SC-UI-034b: Edit Registrar modal is centered on screen (not pushed to one side)
- [x] SC-UI-037: Add Registrar modal is also centered; has [+ Add Field] button

### Delete Registrar (button was missing in AT-003 — fixed in HO-014)
- [x] SC-UI-038: [Delete] button (red/danger) is visible next to [Edit Registrar] in detail panel when edit mode ON
- [x] SC-UI-039: Clicking Delete shows confirmation; confirming removes registrar from left panel
- [fail] SC-UI-039b: Delete of the registrar has failed on confirming delete. Reason: queries-eMM2o_QQ.js:1  DELETE https://demo.estate.zubbystudio.shop/api/v1/registrars/5 500 (Internal Server Error)
- [x] SC-UI-040: Confirmation mentions number of linked companies if any exist

---

## SECTION 4 — Price History Page [/price-history]

### Searchable Dropdown (was plain select in AT-003 — fixed in HO-014)
- [x] SC-UI-041: Company dropdown is searchable — typing filters the list by ticker or name

### Chart Loading (was not loading in AT-003 — fixed in HO-014)
- [fail] SC-UI-042: Selecting a company loads a line chart in lavender colour. Reason Absolutely nothing loads
- [fail] SC-UI-042b: Chart shows price on Y-axis and date on X-axis with correct data points. Reason: nothing shows

### Table (was missing in AT-003 — fixed in HO-014)
- [fail] SC-UI-043: A table appears below the chart showing Date, Price (₦), Source with source badges. Reason: nothing shows

### Date Range Filter
- [fail] SC-UI-044: Clicking "30D" filter shows only last 30 days of data. Reason: nothing shows

### Empty State
- [fail] SC-UI-045: Selecting a company with no price records shows empty state message (not blank/broken chart). Reason: building on previous tests that are not working

### Access Control
- [skipped] SC-UI-046: Readonly user can access /price-history and view data; no edit controls. Reason: User Management not implemented yet

---

## SECTION 5 — New Verifications (Not in AT-003)

These verify fixes introduced in HO-011 to HO-016 that have no
parent test in AT-003:

### Dashboard API Contract
- [skipped] NEW-001: GET /api/v1/dashboard response — `sector_allocation` entries have `"name"` field (not just `"sector"`)
- [skipped] NEW-002: GET /api/v1/dashboard response — `value` in sector_allocation is a JSON string (e.g. `"1500000.00"`) not a float
- [skipped] NEW-003: GET /api/v1/dashboard response — `value` in top_holdings is a JSON string not a float

### Holdings PATCH API Contract
- [skipped] NEW-004: PATCH /api/v1/holdings/{id} with `{"avg_purchase_price": "400.00", "num_shares": 100}` returns 200
- [skipped] NEW-005: PATCH /api/v1/holdings/{id} with `{"avg_purchase_price": "-5.00"}` returns 422
- [skipped] NEW-006: PATCH /api/v1/holdings/{id} with `{"num_shares": 0}` returns 422

### PDF Date Extraction
- [fail] NEW-007: Uploading a PDF named "DAILY SUMMARY FOR 17-05-2026.pdf" creates price_history records dated 2026-05-17 (not today). Reason: query returns no results
- [fail] NEW-008: Uploading a PDF with no recognisable date in filename falls back to today's date (no crash). Reason: query returns no results

### Soft Delete Timezone
- [fail] NEW-009: After soft-deleting a holding, refreshing the page confirms the holding does not reappear

---

## Issues Found

| ID | Page | SC Reference | Description | Severity | Fix Needed |
|----|------|-------------|-------------|----------|------------|
| | | | | | |

---

ps: 
1. There should be helful tooltips for the clickable links and buttons to give the user better feedback on what they are doing, their actions and the system's reponse to those actions.
2. How do i test the API responses? I have been assuming they are working. It may be useful to have a section that allows us to inspect the API responses. especially NEW-001 - NEW-006.

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