---
type: AT
id: AT-003
title: Dashboard, Holdings, Registrars, Price History — Acceptance Test
status: PENDING
version: 1.0
created: 2026-05-08
tester: [fill in]
environment: testdrive.epm.zubbystudio.shop
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
- [x] SC-UI-001: Edit mode toggle is NOT visible anywhere on the Dashboard
- [x] SC-UI-002: Navigating to /holdings shows the edit mode toggle; returning to /dashboard hides it again

### Theme Toggle
- [x] SC-UI-003: Clicking the moon icon switches the app to dark mode (html element gets class "dark") note: should the switch not override the OS theme? e.g when the os theme is dark mode, can the switch from dark to system theme still switch it to light mode against the OS theme?
- [x]SC-UI-004: Clicking the sun icon (in dark mode) returns to system theme (class "dark" removed)
- [x]SC-UI-005: Reloading the page in dark mode preserves dark theme — no flash of light theme on load

### Notification Bell
- [ ] SC-UI-006: When draft holdings or stale prices exist, a numbered amber badge appears on the bell icon
- [skipped]SC-UI-007: Clicking the bell opens a dropdown showing the last 5 action items; each item is clickable; clicking outside closes the dropdown. note action could not be created because trying to add a new holding could not be completed successfully. The frontend displays the create holding form but clicking on save returns an error "XHRPOST https://testdrive.epm.zubbystudio.shop/api/v1/holdings [HTTP/2 500 156ms]"
- [skipped]008: When no pending items exist, the bell has no badge

### Sector Allocation Chart
- [failed]SC-UI-009: The sector allocation donut renders with one segment per sector and a percentage label per segment note The chart is blank; there should be one segment per sector with a percentage label per segment, Holding categories does not have any displayed values.
- [failed]I-010: Sector sizes reflect ₦ value of holdings, not count of stocks. note: not showing any value

### Top Holdings Chart
- [failed]-011: On page load, the top holdings chart shows bars representing current value (₦); the "By Value" toggle is active
- [failed]012: Clicking "By Shares" changes the bars to show number of shares held; the toggle switches to active
- [failed]I-013: The chart shows at most 10 holdings (the 10 with highest value)

### Recent Transactions Card
- [failed]I-014: The card shows columns: Date · Ticker · Type · Shares · Amount — with live data only, max 5 rows. note: still showing old record and the amounts displays 0.00
- [failed]I-015: When no transactions exist, the card shows an empty state message (no blank/broken table). note: I recently loaded the pdf on the price entry page; that should have populated the recent transactions card. There should be at least 5 records, but instead I still see the old records with 0.00 amounts[record that it had prior to loading all the new data from price entry].
### Action Items Card
- [failed]-016: Draft holdings alert — "X holdings pending publish" — appears and links to /holdings
- [failed]-017: Stale price alert appears when prices are older than 7 days; links to /settings/price-entry
- [failed]-018: All-clear state shows a green checkmark and "Portfolio up to date" when nothing is pending
- [failed]SC-UI-019: Approved claim alert — "X claim approved — collect payout" — appears and links to /registrars

---

## Holdings Page [/holdings]

### Column Visibility
- [x] SC-UI-020: All columns visible: Ticker, Company, Sector, Shares, Avg Cost, Curr Price, Curr Value, Cost Basis, return[%], Div Yield, Status, Actions
- [x] SC-UI-021: The column header for annualised return is exactly the string "return[%]" (not "Return %" or any variation)
- [failed] SC-UI-021b: Curr Value, Cost Basis, return[%], and Div Yield show computed values (not blank)
- [x] SC-UI-022: In View Mode — Actions column buttons are hidden; in Edit Mode — Edit and Delete icons appear per row

### Inline Editing
- [x] SC-UI-023: Clicking Edit on a row enables inline editing for THAT row only; other rows remain read-only
- [failed] SC-UI-024: Changing Shares and clicking Save calls PATCH /api/v1/holdings/{id} and the row updates in place note: The save button brings up this error: "Average cost must be a positive number", even though the values are the unedited values, and they are all positive values.
- [failed] SC-UI-025: Clicking Cancel discards any changes and the row returns to its original values; no API call is made(I thought there are two buttons, edit and delete. I only disable the edit/view switch button on top to escape the edit mode and thereby "cancelling" edit mode. I did not see any cancel button on the rows. Unless your intention is for the button marked X to be the cancel button? I also tried to enter a positive number in the average cost field and click save, but it still gives the same error message "XHRPATCH https://testdrive.epm.zubbystudio.shop/api/v1/holdings/1 [HTTP/2 500 213ms]")
- [failed] SC-UI-026: Entering a negative number for Shares shows a validation error on the row; Save is blocked note: doesnt even allow the user to enter a negative number.
- [failed] SC-UI-026: During inline editing of the holdings table, the values in the cells are too jammed to the increment/decrement button, at least a 10px gap should be added to the right of the value field
### Add Holding
- [skipped] SC-UI-027: Clicking [+ Add Holding] in Edit Mode inserts a blank inline form row at the TOP of the table(change these statement, it is supposed to insert a form from the right side of the table according to the @Ho-011-claude-to-antigravity.md handover document)
- [failed] SC-UI-028: Filling in Company, Shares, Avg Cost and clicking Save creates the holding with status "draft"; a DRAFT badge appears on the new row note: I got an error on this "Average cost must be a positive number" when i tried to enter a positive number in the average cost field and click save, but it still gives the same error message "XHRPATCH https://testdrive.epm.zubbystudio.shop/api/v1/holdings/1 [HTTP/2 500 213ms]"
- [skipped] SC-UI-029: Attempting to add a holding for a company that already has one shows an error; no API call is made note: I tried adding a new holding with the same company name and ticker as an existing holding, and it still created the holding without any error.

### Draft / Publish / Delete
- [skipped] SC-UI-030: Clicking Publish on a draft row calls /publish endpoint; DRAFT badge changes to LIVE; dashboard total updates note: no error was returned when i clicked on publish, but the badge did not change to live and the dashboard total did not update.
- [skipped] SC-UI-031: Clicking Delete shows a confirmation dialog; confirming soft-deletes the holding and removes the row

---

## Registrars Page [/registrars]

### Company Linking (405 Fix Verification)
- [x] SC-UI-032: Selecting a company and clicking [Link Company] returns HTTP 200 (not 405); company appears in Linked Companies card
- [x] SC-UI-033: Clicking the unlink icon next to a linked company removes it from the card; count badge decrements

### Extended Contact Fields — Edit Registrar
- [failed] SC-UI-034: Clicking [Edit Registrar] opens the edit modal; a [+ Add Field?(says Add Details)] button is present; clicking it shows a type selector: phone, email, address, website, other
- [failed] SC-UI-035: Adding a second phone field and saving stores both numbers; both are visible in the detail panel(The UI is horrible. Looks like a grid with a massive gap inbetween the number and they are positioned horizontally instead of vertically, as in flex column with little breathing space in between. need to be worked on)
- [Passed] SC-UI-036: Adding a website field and saving shows the URL in the detail panel; clicking it opens in a new tab(when the url is clicked,)

### Add Registrar
- [passed] SC-UI-037: Clicking [+ Add Registrar] opens a modal with name, email, phone, address fields AND a [+ Add Field(says Add Details)] button for extra fields(The modal is not centered, it is positioned at the top right corner of the screen)

### Delete Registrar
- [failed] SC-UI-038: A [Delete] button (red/danger colour) is visible next to [Edit Registrar] when a registrar is selected. note: presently no delete button is visible.
- [failed] SC-UI-039: Clicking [Delete] shows a confirmation dialog with a warning about linked data; confirming removes the registrar from the list. because no visible delete button, i was unable to test this.
- [failed] SC-UI-040: When a registrar has linked companies, the confirmation dialog mentions how many companies will be unlinked. because no visible delete button, i was unable to test this.

---

## Price History Page [/price-history]

### Core Functionality
- [failed] SC-UI-041: A searchable company dropdown is visible with placeholder "Select a company to view price history". note: the company dropdown is not searchable, it only shows a list of companies, that doesn't have a search field on top of the first select field where I can search with keyword for a particular company.
- [failed] SC-UI-042: Selecting DANGCEM loads a line chart of price history in lavender (#BCBDFA). note: the chart doesn't load
- [failed] SC-UI-043: A table below the chart shows Date, Price (₦), Source columns with correct values and source badges. note: I couldn't see the table below the chart
- [failed] SC-UI-044: Clicking the "30D" date range filter shows only the last 30 days of data in chart and table. note: clicking the 30D date range filter doesn't show only the last 30 days of data in the chart and table
- [failed] SC-UI-045: A company with no price records shows an empty state message (not a blank/broken chart). note: I don't know how to test this
- [failed] SC-UI-046: A readonly user can access /price-history and view charts; no edit controls are present. note: I don't know how to test this

---

## Issues Found

| ID | Page | SC Reference | Description | Severity | Resolution |
|----|------|-------------|-------------|----------|------------|
| 1  |      |             |             |          |            |

---

## Sign-Off

- [skipped] All P0 failures resolved (SC-UI-032 registrar 405 fix, SC-UI-001 edit toggle, SC-UI-003/004/005 theme)
- [skipped] Deferred items logged with GitHub issue numbers
- [skipped] Ready for Phase 3C (Obsidian import, Claims page)

**Tested by**: Zubby Ikegwu  
**Date**: 2026-05-19  
**Result**: PARTIAL