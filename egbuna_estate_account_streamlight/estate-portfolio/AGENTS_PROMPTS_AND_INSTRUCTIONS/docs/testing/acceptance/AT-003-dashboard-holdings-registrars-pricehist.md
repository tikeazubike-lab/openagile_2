---
type: AT
id: AT-003
title: Dashboard, Holdings, Registrars, Price History — Acceptance Test
status: PENDING
version: 1.0
created: 2026-05-08
tester: [fill in]
environment: demo.estate.zubbystudio.shop
branch: test
feature: BR-001
related: SC-UI-001 through SC-UI-046
---

# [AT] AT-003 — Dashboard, Holdings, Registrars, Price History
> **Type**: Acceptance Test · **Status**: 🟡 PENDING · **Branch**: test

---

## How to Use This Document

For each test item, replace `[ ]` with one of:
- `[x]` — PASS
- `[fail]` — FAIL: describe what happened
- `[skip]` — SKIP: state reason
- `[pending]` — not yet tested

Group failures at the bottom under **Issues Found**.

---

## Dashboard Page [/dashboard]

### Edit Mode Toggle
- [ ] SC-UI-001: Edit mode toggle is NOT visible anywhere on the Dashboard
- [ ] SC-UI-002: Navigating to /holdings shows the edit mode toggle; returning to /dashboard hides it again

### Theme Toggle
- [ ] SC-UI-003: Clicking the moon icon switches the app to dark mode (html element gets class "dark")
- [ ] SC-UI-004: Clicking the sun icon (in dark mode) returns to system theme (class "dark" removed)
- [ ] SC-UI-005: Reloading the page in dark mode preserves dark theme — no flash of light theme on load

### Notification Bell
- [ ] SC-UI-006: When draft holdings or stale prices exist, a numbered amber badge appears on the bell icon
- [ ] SC-UI-007: Clicking the bell opens a dropdown showing the last 5 action items; each item is clickable; clicking outside closes the dropdown
- [ ] SC-UI-008: When no pending items exist, the bell has no badge

### Sector Allocation Chart
- [ ] SC-UI-009: The sector allocation donut renders with one segment per sector and a percentage label per segment
- [ ] SC-UI-010: Sector sizes reflect ₦ value of holdings, not count of stocks

### Top Holdings Chart
- [ ] SC-UI-011: On page load, the top holdings chart shows bars representing current value (₦); the "By Value" toggle is active
- [ ] SC-UI-012: Clicking "By Shares" changes the bars to show number of shares held; the toggle switches to active
- [ ] SC-UI-013: The chart shows at most 10 holdings (the 10 with highest value)

### Recent Transactions Card
- [ ] SC-UI-014: The card shows columns: Date · Ticker · Type · Shares · Amount — with live data only, max 5 rows
- [ ] SC-UI-015: When no transactions exist, the card shows an empty state message (no blank/broken table)

### Action Items Card
- [ ] SC-UI-016: Draft holdings alert — "X holdings pending publish" — appears and links to /holdings
- [ ] SC-UI-017: Stale price alert appears when prices are older than 7 days; links to /settings/price-entry
- [ ] SC-UI-018: All-clear state shows a green checkmark and "Portfolio up to date" when nothing is pending
- [ ] SC-UI-019: Approved claim alert — "X claim approved — collect payout" — appears and links to /registrars

---

## Holdings Page [/holdings]

### Column Visibility
- [ ] SC-UI-020: All columns visible: Ticker, Company, Sector, Shares, Avg Cost, Curr Price, Curr Value, Cost Basis, return[%], Div Yield, Status, Actions
- [ ] SC-UI-021: The column header for annualised return is exactly the string "return[%]" (not "Return %" or any variation)
- [ ] SC-UI-021b: Curr Value, Cost Basis, return[%], and Div Yield show computed values (not blank)
- [ ] SC-UI-022: In View Mode — Actions column buttons are hidden; in Edit Mode — Edit and Delete icons appear per row

### Inline Editing
- [ ] SC-UI-023: Clicking Edit on a row enables inline editing for THAT row only; other rows remain read-only
- [ ] SC-UI-024: Changing Shares and clicking Save calls PATCH /api/v1/holdings/{id} and the row updates in place
- [ ] SC-UI-025: Clicking Cancel discards any changes and the row returns to its original values; no API call is made
- [ ] SC-UI-026: Entering a negative number for Shares shows a validation error on the row; Save is blocked

### Add Holding
- [ ] SC-UI-027: Clicking [+ Add Holding] in Edit Mode inserts a blank inline form row at the TOP of the table
- [ ] SC-UI-028: Filling in Company, Shares, Avg Cost and clicking Save creates the holding with status "draft"; a DRAFT badge appears on the new row
- [ ] SC-UI-029: Attempting to add a holding for a company that already has one shows an error; no API call is made

### Draft / Publish / Delete
- [ ] SC-UI-030: Clicking Publish on a draft row calls /publish endpoint; DRAFT badge changes to LIVE; dashboard total updates
- [ ] SC-UI-031: Clicking Delete shows a confirmation dialog; confirming soft-deletes the holding and removes the row

---

## Registrars Page [/registrars]

### Company Linking (405 Fix Verification)
- [ ] SC-UI-032: Selecting a company and clicking [Link Company] returns HTTP 200 (not 405); company appears in Linked Companies card
- [ ] SC-UI-033: Clicking the unlink icon next to a linked company removes it from the card; count badge decrements

### Extended Contact Fields — Edit Registrar
- [ ] SC-UI-034: Clicking [Edit Registrar] opens the edit modal; a [+ Add Field] button is present; clicking it shows a type selector: phone, email, address, website, other
- [ ] SC-UI-035: Adding a second phone field and saving stores both numbers; both are visible in the detail panel
- [ ] SC-UI-036: Adding a website field and saving shows the URL in the detail panel; clicking it opens in a new tab

### Add Registrar
- [ ] SC-UI-037: Clicking [+ Add Registrar] opens a modal with name, email, phone, address fields AND a [+ Add Field] button for extra fields

### Delete Registrar
- [ ] SC-UI-038: A [Delete] button (red/danger colour) is visible next to [Edit Registrar] when a registrar is selected
- [ ] SC-UI-039: Clicking [Delete] shows a confirmation dialog with a warning about linked data; confirming removes the registrar from the list
- [ ] SC-UI-040: When a registrar has linked companies, the confirmation dialog mentions how many companies will be unlinked

---

## Price History Page [/price-history]

### Core Functionality
- [ ] SC-UI-041: A searchable company dropdown is visible with placeholder "Select a company to view price history"
- [ ] SC-UI-042: Selecting DANGCEM loads a line chart of price history in lavender (#BCBDFA)
- [ ] SC-UI-043: A table below the chart shows Date, Price (₦), Source columns with correct values and source badges
- [ ] SC-UI-044: Clicking the "30D" date range filter shows only the last 30 days of data in chart and table
- [ ] SC-UI-045: A company with no price records shows an empty state message (not a blank/broken chart)
- [ ] SC-UI-046: A readonly user can access /price-history and view charts; no edit controls are present

---

## Issues Found

| ID | Page | SC Reference | Description | Severity | Resolution |
|----|------|-------------|-------------|----------|------------|
| 1  |      |             |             |          |            |

---

## Sign-Off

- [ ] All P0 failures resolved (SC-UI-032 registrar 405 fix, SC-UI-001 edit toggle, SC-UI-003/004/005 theme)
- [ ] Deferred items logged with GitHub issue numbers
- [ ] Ready for Phase 3C (Obsidian import, Claims page)

**Tested by**: _______________  
**Date**: _______________  
**Result**: PASS / FAIL / PARTIAL
