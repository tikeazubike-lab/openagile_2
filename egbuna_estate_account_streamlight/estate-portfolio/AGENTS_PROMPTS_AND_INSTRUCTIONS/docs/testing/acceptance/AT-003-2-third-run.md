---
type: AT
id: AT-003-2
title: Dashboard, Holdings, Registrars — Third Run (3-Layer Format)
status: PENDING
version: 1.0
created: 2026-05-21
tester: [fill in]
environment: demo.estate.zubbystudio.shop
branch: test
parent: AT-003-1
fixes_from: HO-018
format: 3-layer (DB / API / UI)
---

# [AT] AT-003-2 — Third Run
> **Type**: Acceptance Test · **Status**: 🟡 PENDING
> **Parent**: AT-003-1
> **New format**: Every item labelled [DB], [API], or [UI]
> **Only items still failing from AT-003-1 are included here**

---

## How to Read This Document

Each test item is prefixed with its verification layer:

```
[DB]  — verify in PostgreSQL directly
       How: SSH to VPS → docker compose exec postgres psql -U openagile -d estate_portfolio

[API] — verify via curl or DevTools Network tab
       How: DevTools → Network tab, or curl from VPS with epm_token cookie

[UI]  — verify by looking at the rendered browser page
       How: demo.estate.zubbystudio.shop in Chrome/Firefox
```

Mark each item:
- `[x]` PASS
- `[fail]` FAIL: describe what happened, which layer broke
- `[skip]` SKIP: depends on a failed parent (note which)
- `[pending]` not yet tested

---

## SECTION 1 — Dashboard [/dashboard]

### Charts (still blank in AT-003-1)

- [ ] [API] NEW-001: GET /api/v1/dashboard response contains `sector_allocation`
  as a non-empty array with `name`, `value` (string), `pct` (string) fields
  ```bash
  # Quick check:
  curl -s -b "epm_token=TOKEN" https://demo.estate.zubbystudio.shop/api/v1/dashboard \
    | python3 -c "import sys,json; d=json.load(sys.stdin); \
      print(d['data']['sector_allocation'][:2])"
  ```

- [ ] [API] NEW-002: Each item in `sector_allocation` has a `name` field
  (not just `sector`) — required by Recharts
  ```bash
  # Should print True:
  curl -s -b "epm_token=TOKEN" https://demo.estate.zubbystudio.shop/api/v1/dashboard \
    | python3 -c "import sys,json; d=json.load(sys.stdin); \
      items=d['data']['sector_allocation']; \
      print('name field present:', all('name' in i for i in items))"
  ```

- [ ] [API] NEW-003: `value` in `sector_allocation` is a JSON string not a float
  ```bash
  # Should print <class 'str'>:
  curl -s -b "epm_token=TOKEN" https://demo.estate.zubbystudio.shop/api/v1/dashboard \
    | python3 -c "import sys,json; d=json.load(sys.stdin); \
      items=d['data']['sector_allocation']; \
      print(type(items[0]['value'])) if items else print('EMPTY ARRAY')"
  ```

- [ ] [UI] SC-UI-009: Sector allocation donut renders with coloured segments
  and percentage labels (not blank white circle)

- [ ] [UI] SC-UI-010: Segment sizes visually reflect ₦ value — larger segment
  = larger sector value

- [ ] [UI] SC-UI-011: Top Holdings chart shows horizontal bars on load;
  "By Value" toggle is active

- [ ] [UI] SC-UI-012: Clicking "By Shares" changes chart data;
  toggle switches to "By Shares" active state

- [ ] [UI] NEW-CHART-01: Open browser DevTools Console — confirm zero
  Recharts-related errors (e.g. "No data", "nameKey", NaN warnings)

### Recent Transactions (showed zeroes in AT-003-1)

- [ ] [API] SC-UI-014-api: GET /api/v1/dashboard returns `recent_transactions`
  array where `num_shares` and `net_amount` are non-null and non-zero
  for existing transactions

- [ ] [UI] SC-UI-014: Recent Transactions card shows real data —
  correct Date, Ticker, Type badge, Shares count, ₦ Amount

- [ ] [UI] SC-UI-015: Empty state renders "No transactions recorded yet"
  when no transactions exist (not blank or zero rows)

### Action Items (errors in AT-003-1)

- [ ] [UI] SC-UI-016: Draft holdings alert shows correct count;
  clicking navigates to /holdings

- [ ] [UI] SC-UI-017: Stale price alert appears when last_updated
  is more than 7 days ago

- [ ] [UI] SC-UI-018: All-clear green checkmark appears when no
  pending items exist

- [ ] [UI] SC-UI-006: Bell icon shows numbered amber badge when
  action items exist

- [ ] [UI] SC-UI-007: Clicking bell opens dropdown listing items;
  clicking outside closes it

### Theme Toggle (icon not changing in AT-003-1)

- [ ] [UI] SC-UI-003: Moon icon visible in light mode; clicking it
  switches to dark (html gets class "dark"); icon changes to Sun

- [ ] [UI] SC-UI-004: Sun icon visible in dark mode; clicking it
  returns to system theme; html loses class "dark"; icon changes to Moon

- [ ] [UI] SC-UI-005: Forced dark theme persists after page reload
  (no flash of light theme on load)

---

## SECTION 2 — Holdings [/holdings]

### Add Holding Drawer (500 error in AT-003-1)

- [ ] [API] BUG-1-api: POST /api/v1/holdings with valid payload returns
  201 (not 500)
  ```bash
  curl -s -X POST -b "epm_token=TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"company_id": 1, "num_shares": 100, "avg_purchase_price": "400.00", "status": "draft"}' \
    https://demo.estate.zubbystudio.shop/api/v1/holdings \
    | python3 -m json.tool
  ```

- [ ] [DB]  BUG-1-db: After successful POST, new row exists in holdings table
  ```sql
  SELECT id, company_id, num_shares, avg_purchase_price, status, deleted_at
  FROM holdings ORDER BY id DESC LIMIT 3;
  ```

- [ ] [UI] SC-UI-027: [+ Add Holding] opens slide-out drawer from right;
  table remains visible behind drawer

- [ ] [UI] SC-UI-028: Save as Draft creates holding with DRAFT badge in table

- [ ] [UI] SC-UI-028b: Save & Publish creates holding with LIVE badge in table

- [ ] [UI] SC-UI-029: Adding duplicate company shows error in drawer;
  no API call made (check Network tab — no POST fired)

### Inline Editing (cursor jump + no Cancel in AT-003-1)

- [ ] [UI] SC-UI-023: Clicking Edit on a row enables inline editing
  for that row ONLY; cursor stays in the input field while typing
  (does not jump out mid-keystroke)

- [ ] [UI] SC-UI-023b: A visible Cancel button appears on the
  editing row alongside Save

- [ ] [API] SC-UI-024-api: PATCH /api/v1/holdings/{id} with
  `{"num_shares": 150, "avg_purchase_price": "410.00"}` returns 200
  ```bash
  curl -s -X PATCH -b "epm_token=TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"num_shares": 150, "avg_purchase_price": "410.00"}' \
    https://demo.estate.zubbystudio.shop/api/v1/holdings/1 \
    | python3 -m json.tool
  ```

- [ ] [DB]  SC-UI-024-db: After successful PATCH, holdings table shows
  updated num_shares and avg_purchase_price
  ```sql
  SELECT id, num_shares, avg_purchase_price FROM holdings WHERE id = 1;
  ```

- [ ] [UI] SC-UI-024: Row returns to read-only with updated values after Save;
  portfolio total on Dashboard updates

- [ ] [UI] SC-UI-025: Clicking Cancel returns row to original values;
  DevTools Network tab shows no PATCH request fired

- [ ] [UI] SC-UI-026: Entering negative Shares shows inline error on the row;
  Save is blocked; Network tab shows no PATCH request fired

### Edit Mode Reset (stale inputs in AT-003-1)

- [ ] [UI] SC-UI-022b: Toggling edit mode OFF while a row is in inline
  edit clears inputs immediately; no stale form visible

### Delete (was not persisting in AT-003-1)

- [ ] [API] SC-UI-031-api: DELETE /api/v1/holdings/{id} returns 200
  ```bash
  curl -s -X DELETE -b "epm_token=TOKEN" \
    https://demo.estate.zubbystudio.shop/api/v1/holdings/1 \
    | python3 -m json.tool
  ```

- [ ] [DB]  SC-UI-031-db: After DELETE, holdings row has `deleted_at` set
  (not hard deleted)
  ```sql
  SELECT id, deleted_at FROM holdings WHERE id = 1;
  -- deleted_at should be a timestamp, not NULL
  ```

- [ ] [UI] SC-UI-031: Row disappears from table after confirmation;
  page refresh confirms row stays gone

---

## SECTION 3 — Registrars [/registrars]

These were mostly fixed in AT-003-1. Re-test only if regressions suspected.

- [ ] [UI] SC-UI-032: Link company returns 200; company appears in card
  (regression guard — was 405 originally)
- [ ] [UI] SC-UI-038: Delete button visible in detail panel (edit mode ON)
- [ ] [UI] SC-UI-034b: Edit modal is centered on screen

---

## SECTION 4 — New Features Verified

- [ ] [UI] FEATURE-1a: Hovering over theme toggle shows tooltip
  "Switch to dark mode" or "Return to system theme"

- [ ] [UI] FEATURE-1b: Hovering over Holdings Edit icon shows tooltip
  "Edit this holding"

- [ ] [UI] FEATURE-1c: Hovering over Holdings Delete icon shows tooltip
  "Remove this holding"

- [ ] [UI] FEATURE-1d: Hovering over Holdings Publish button shows tooltip
  "Publish draft to live portfolio"

---

## Issues Found

| ID | Layer | SC Ref | Description | Severity |
|----|-------|--------|-------------|----------|
| | | | | |

---

## Summary Table

| Section | Total | Pass | Fail | Skip | Pending |
|---------|-------|------|------|------|---------|
| Dashboard | 16 | | | | |
| Holdings | 14 | | | | |
| Registrars | 3 | | | | |
| New Features | 4 | | | | |
| **TOTAL** | **37** | | | | |

---

## Sign-Off

- [ ] All P0 bugs resolved (BUG-1, BUG-2, BUG-3)
- [ ] Dashboard charts rendering with real data
- [ ] Holdings CRUD fully functional (add, edit, delete)
- [ ] No regressions from AT-003-1 passing items
- [ ] PROJECT_STATUS.md updated
- [ ] Ready to proceed to Phase 3C planning

**Tested by**: _______________
**Date**: _______________
**Result**: PASS / FAIL / PARTIAL
