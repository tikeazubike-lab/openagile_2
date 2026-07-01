---
id: F-003
title: Holdings
status: BUGS-OPEN
owner-backend: Antigravity
owner-frontend: Deepseek v4
sprint: Phase 2B (bugs from AT-003-1)
open-bugs: BUG-002 BUG-003
---

# F-003 — Holdings

## Goal
Display all portfolio holdings in two tables (Active + Claims), allow
inline editing of individual rows, add new holdings via a slide-out
drawer, publish drafts, and soft-delete holdings. The grand total
row below both tables shows combined net worth.

## What Is Built

Backend (backend/app/routers/holdings.py):
  GET    /api/v1/holdings                  — list all (with computed fields)
  POST   /api/v1/holdings                  — create (default: draft)
  PATCH  /api/v1/holdings/{id}             — update shares + avg cost
  PUT    /api/v1/holdings/{id}/publish     — draft → live
  DELETE /api/v1/holdings/{id}             — soft delete

Frontend:
  src/routes/_app.holdings.tsx
  src/components/holdings/InlineEditRow.tsx  (child component — cursor fix)
  src/components/holdings/AddHoldingDrawer.tsx
  src/api/queries.ts → useHoldings(), useUpdateHolding(), etc.

## API Contract

GET /api/v1/holdings response per item:
{
  "id": 1,
  "ticker": "DANGCEM",
  "company_name": "Dangote Cement PLC",
  "sector": "Industrial Goods",
  "num_shares": 1000,
  "avg_purchase_price": "400.00",
  "current_price": "450.00",
  "current_value": "450000.00",
  "cost_basis": "400000.00",
  "return_pct": "+12.50",
  "div_yield": "3.20",
  "xirr_pct": null,
  "status": "live",
  "holding_type": "active",
  "cost_basis_override": null
}

Claim holdings:
  return_pct: null  (never computed — division undefined with zero cost basis)
  cost_basis_override: "0.00"
  xirr_pct: null

PATCH /api/v1/holdings/{id} request body:
{
  "num_shares": 150,
  "avg_purchase_price": "410.00"   ← string, not float
}
Field name is avg_purchase_price — NOT avg_cost (confirmed bug in AT-003-1)

## Open Bugs to Fix Before Marking Complete

BUG-002 — Inline edit cursor jumps:
  Create InlineEditRow child component with its own useState
  Parent table holds only editingRowId (number | 'new' | null)
  InlineEditRow owns shares and avgCost state — parent never re-renders on keystroke
  useEffect in parent: if (!editMode) setEditingRowId(null)

BUG-003 — POST /api/v1/holdings 500 error:
  Diagnose first: docker compose logs epm_v2 --tail=50 | grep "500\|Error"
  Most likely: user_id missing on Holding insert or UNIQUE constraint
  Fix after confirming root cause from logs

## Layout

Page structure:
  Header: "Holdings" + [+ Add Holding] button (admin + edit mode only)

  TABLE 1 — Active Portfolio (holding_type = 'active'):
    Label: "Active Portfolio" (green dot badge)
    Columns: Ticker | Company | Sector | Shares | Avg Cost |
             Curr Price | Curr Value | Cost Basis | return[%] | Div Yield | Status | Actions
    Column header EXACTLY: "return[%]" (no variations)
    Subtotal row: sum of current_value for live holdings

  TABLE 2 — Claims Portfolio (holding_type = 'claim'):
    Label: "Claims Portfolio" (amber dot badge)
    Columns: Ticker | Company | Sector | Shares | Status |
             Claim Authority | Claim Status | Expected Payout | Actual Payout | Actions
    NOTE: return[%] column ABSENT (claim holdings have null return_pct)
    Subtotal row: sum of actual_payout (paid) or expected_payout (pending)

  GRAND TOTAL ROW:
    "Total Assets: ₦XX,XXX,XXX.XX"
    "Active: ₦X,XXX,XXX + Claims: ₦XXX,XXX"
    Style: accent-gold (#DABF82), DM Mono, font-weight 600

## Inline Editing (Child Component Pattern)

editingRowId state in HoldingsPage: number | 'new' | null

When editingRowId === holding.id:
  Render <InlineEditRow> instead of read-only row
  InlineEditRow has local useState for shares and avgCost
  onSave(id, {num_shares, avg_purchase_price}) → PATCH → invalidate queries
  onCancel() → setEditingRowId(null), no API call

Client-side validation before API call:
  shares must be integer > 0 → error on row if not
  avgCost must be Decimal > 0 → error on row if not
  Error displayed as a row below the editing row, not a modal

## Add Holding Drawer

Trigger: [+ Add Holding] button (admin + edit mode only)
Layout: slide-out from right, 420px width
Holdings table stays fully visible behind drawer

Drawer fields:
  Company *     — searchable dropdown (useCompanies())
  Shares *      — DM Mono input, integer, min 1
  Avg Cost (₦) * — DM Mono input, decimal, min 0.01
  Purchase Date  — date picker, optional, defaults today
  Notes         — textarea, optional
  Status        — toggle: [Draft] [Publish now], default Draft

Drawer footer:
  [Cancel]          — closes drawer, no API call, form resets
  [Save as Draft]   — POST with status='draft'
  [Save & Publish]  — POST with status='live'

Duplicate check: if company already has a holding → show error in drawer, no API call

## Acceptance Checklist

### [DB]
- [ ] holdings table has holding_type column with values 'active' or 'claim'
- [ ] holdings table has cost_basis_override column (nullable)
- [ ] After PATCH, updated num_shares and avg_purchase_price visible in DB
- [ ] After DELETE, row has deleted_at timestamp (not hard deleted)

### [API]
- [ ] GET /api/v1/holdings → 200, monetary values are strings
- [ ] GET /api/v1/holdings?holding_type=active → only active holdings
- [ ] GET /api/v1/holdings?holding_type=claim → only claim holdings
- [ ] POST /api/v1/holdings with valid payload → 201
- [ ] POST /api/v1/holdings with duplicate company → 409
- [ ] PATCH with {"num_shares":150,"avg_purchase_price":"410.00"} → 200
- [ ] PATCH with {"avg_purchase_price":"-5.00"} → 422
- [ ] PATCH with {"num_shares":0} → 422
- [ ] DELETE /api/v1/holdings/{id} → 200
- [ ] GET after DELETE does not return deleted holding

### [UI]
- [ ] Two separate tables render (Active + Claims)
- [ ] Grand total row shows below both tables
- [ ] Column header is exactly "return[%]"
- [ ] Claims table has no return[%] column
- [ ] Claim holdings show "—" for return percentage
- [ ] Edit mode OFF → Actions column hidden
- [ ] Edit mode ON → Edit + Delete icons visible per row
- [ ] Clicking Edit on a row → InlineEditRow renders for that row only
- [ ] Typing in shares field → cursor stays in input (no jump)
- [ ] Cancel button visible on editing row
- [ ] Clicking Cancel → row returns to read-only, no API call
- [ ] Entering negative shares → inline error, no API call
- [ ] Save → row updates in place, dashboard total refreshes
- [ ] [+ Add Holding] → slide-out drawer opens from right
- [ ] Table remains visible behind drawer
- [ ] Save as Draft → DRAFT badge on new row
- [ ] Save & Publish → LIVE badge on new row
- [ ] Delete → confirmation dialog → row disappears → page refresh confirms gone
- [ ] Toggling edit mode OFF while row editing → inputs clear immediately

## Sign-Off
- [ ] All checklist items passing
- [ ] BUG-002 and BUG-003 resolved
- [ ] progress-tracker.md updated to ✅ Complete
- [ ] HO filed in docs/handovers/
