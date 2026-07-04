# BUG-TRIAGE-001 — Manual Test Run Disposition
# Date: 2026-07-03
# Triaged by: Claude (The Brain / Architect)
# Source: Manual test run by Product Owner (Zubbyik)
# Test run date: 2026-07-03 11:30 UTC

---

## Summary Table

| Test ID | Result | Disposition | Action Owner |
|---------|--------|-------------|--------------|
| DASH-VIEW-FE-E2E-001 | PASS | Close — no action | — |
| DASH-VIEW-FE-SMK-001 | PASS | Close — no action | — |
| DASH-VIEW-FE-SMK-002 | FAIL | Deferred — standalone bug ticket | hermes[nemotron] (post-F016) |
| HOLD-UPDATE-FE-E2E-001 | FAIL | Closed — superseded by HO-023 | — |
| HOLD-VIEW-BE-E2E-001 | FAIL | Blocked — xfail, depends on F-INV-001 | [hermes]Deepseek:flash |
| PRIC-UPDATE-BE-E2E-001 | PASS (conditional) | Pass with note — depends on F-INV-001 | — |

---

## Detailed Dispositions

---

### DASH-VIEW-FE-E2E-001 — PASS ✅

**Verdict:** Close. No action required.

All four assertions passed (sector_allocation name field, value as string,
donut chart segments, bar chart horizontal bars). Implementation confirmed
correct against spec.

---

### DASH-VIEW-FE-SMK-001 — PASS ✅

**Verdict:** Close. No action required.

Theme toggle (sun ↔ moon, light ↔ dark) behaves as specified.

---

### DASH-VIEW-FE-SMK-002 — FAIL ❌ → DEFERRED BUG

**Verdict:** Standalone deferred bug ticket. Do NOT fix in current sprint.

**All four sub-assertions failed:**
- Bell shows amber badge when draft holdings exist
- Bell shows badge when prices are stale (>7 days)
- Clicking bell opens dropdown with up to 5 items
- No console errors from useActionItems

**Root cause direction:**
The `useActionItems` hook is either not implemented, returning empty,
or throwing silently. This is isolated to the notification/action-items
subsystem — no cascade risk to other features.

**Backlog placement:**
```
Backlog location: Bug Tracker → Dashboard → Notifications
Ticket ID:        BUG-DASH-NOTIFY-001
Priority:         LOW (standalone, no blocking dependency)
Fix window:       First available sprint AFTER F-016 ships and
                  AT-004 is green.
                  Do NOT schedule before then.
```

**When fixing — scope for builder:**
1. Audit `useActionItems` hook — confirm it is wired to an API endpoint
2. Verify endpoint `/api/v1/action-items` or equivalent exists in backend
3. Check bell component mounts the hook and passes count to badge
4. Console errors likely reveal the actual failure (undefined, 404, or
   schema mismatch)

**Test must be re-run after fix with all 4 assertions green before closing.**

---

### HOLD-UPDATE-FE-E2E-001 — FAIL ❌ → CLOSED (Superseded)

**Verdict:** Closed. Will not fix. Superseded by HO-023.

**Reason:**
HO-023 established the locked architectural decision:
> All inline editing is removed. All CRUD activities for holdings and
> other entities are performed in the Admin section.

The three failing assertions (cursor position in shares field, cancel
button on editing row, editMode toggle clearing row) are all inline
editing behaviours. These UI patterns no longer exist in the
post-HO-023 architecture.

**Action required:**
- [ ] Mark HOLD-UPDATE-FE-E2E-001 as CLOSED/SUPERSEDED in test tracker
- [ ] Add comment: "Replaced by Admin CRUD — see HO-023. New test to be
      written post-F016 covering admin-side holdings edit."
- [ ] A replacement test (HOLD-UPDATE-ADMIN-BE-INT-001 or similar) will be
      scoped inside F-016 admin implementation work.
- [ ] grep check (AT-004-B04) must confirm zero editMode references remain.

---

### HOLD-VIEW-BE-E2E-001 — FAIL ❌ → BLOCKED (xfail)

**Verdict:** Blocked. Not a code bug. Depends on F-INV-001 (see below).

**Reason:**
Test expects updated values in holdings and other boards after a price
update. The calculation chain requires `initial_cost` of each stock
(cost basis / average purchase price). This data has not been uploaded.
The feature to upload it does not yet exist.

**This is a data dependency, not a code defect.**

**Action required:**
- [ ] Mark test as `@pytest.mark.xfail(reason="Blocked: F-INV-001 (initial
      stock cost upload) not yet implemented")`
- [ ] Do not attempt to fix this test until F-INV-001 is complete and
      initial cost data is loaded into the database
- [ ] After F-INV-001 ships: re-run test with real data, remove xfail

---

### PRIC-UPDATE-BE-E2E-001 — PASS (Conditional) ✅⚠️

**Verdict:** Pass with conditional note. Recorded as PASS in official log.

**What passed:**
Price update logic executes correctly — values are written to the
price table. The endpoint itself is working as designed.

**What is not yet verifiable:**
End-to-end value reflection in /holdings and /dashboard requires
`initial_cost` data (same dependency as HOLD-VIEW-BE-E2E-001 above).
The downstream calculation errors on the missing cost basis variable.

**Official record:**
```
PRIC-UPDATE-BE-E2E-001: PASS
Note: Price write confirmed. E2E reflection blocked pending F-INV-001.
      Re-verify full chain after initial stock costs are loaded.
```

---

## New Feature Spec Required

### F-INV-001 — Initial Stock Cost Upload (One-Off Task)

**Priority:** P1 — blocks HOLD-VIEW-BE-E2E-001 and
             PRIC-UPDATE-BE-E2E-001 full verification

**Nature:** One-off admin data-entry task, similar in pattern to the
Obsidian one-off transfer task. Not a recurring user-facing feature.

**Scope:**
- Admin uploads a CSV (or uses a simple form) containing:
  ticker | avg_purchase_price | total_shares | purchase_date
- System writes these as the cost basis records for each holding
- No recurring workflow needed — this runs once to seed historical data
- After seeding, normal holdings CRUD maintains the data going forward

**Pre-conditions:**
- F-016 (User Management / Admin section) must be live first,
  since this task lives in the admin section
- Holdings table must already contain the relevant tickers

**Suggested CSV format:**
```csv
ticker,avg_purchase_price,quantity,purchase_date
DANGCEM,245.50,500,2024-01-15
GTCO,33.20,1000,2024-03-01
...
```

**Spec file to be written:** `F-INV-001-initial-stock-cost-upload.md`
**Author:** Claude (next session or this session on request)
**Implementation agent:** [hermes]Deepseek:flash (backend CSV import)
                          hermes[nemotron] (admin UI form)

**Gate:** F-016 must be complete before F-INV-001 implementation begins.

---

## Updated Sequencing (post-triage)

```
CURRENT GATE:
  HO-026 (hermes[nemotron] confirms HO-024 complete)
    ↓
  AT-004 (14/14 green)
    ↓
  F-016 — User Management (backend + frontend)
    ↓
  F-INV-001 — Initial Stock Cost Upload (one-off admin task)
    ↓
  Re-run HOLD-VIEW-BE-E2E-001 and PRIC-UPDATE-BE-E2E-001 (full chain)
    ↓
  BUG-DASH-NOTIFY-001 fix (bell / useActionItems)
    ↓
  F-007 — NAV History
```

---

## Open Items from This Triage (Product Owner)

| ID | Question | Status |
|----|----------|--------|
| OQ-F016-1 | Deactivated users' portfolios: hidden or read-only? | Open |
| OQ-F016-2 | Account creation: admin-only or invitation flow? | Open |
| OQ-F007-3 | Non-trading days: carry-forward NAV or skip? | Open |
| OQ-FINV-1 | CSV upload or admin form for initial stock costs? | New — needs answer before F-INV-001 spec |
| OQ-FINV-2 | Do all holdings need cost basis, or only specific portfolios? | New — needed for F-INV-001 scope |

---

End of BUG-TRIAGE-001.
Next expected action: hermes[nemotron] produces HO-026.
