---
id: F-002
title: Dashboard
status: BUGS-OPEN
owner-backend: Deepseek:flash
owner-frontend: Nemotron
Review/Architect role: DeepSeek v4
sprint: Phase 2B (bugs from AT-003-1)
open-bugs: BUG-001 BUG-004 BUG-005
---

# F-002 — Dashboard

## Goal

A read-only consolidated view answering three morning questions:
net worth, pending administration, and portfolio performance.
No edit mode on this page — it is always read-only.

## What Is Built

Backend (backend/app/routers/dashboard.py):
  GET /api/v1/dashboard — single endpoint returns all KPIs

Frontend:
  src/routes/_app.dashboard.tsx
  src/components/dashboard/SectorAllocationChart.tsx
  src/components/dashboard/TopHoldingsChart.tsx
  src/hooks/useCountUp.ts
  src/api/queries.ts → useDashboard(), useActionItems()

## API Response Shape

GET /api/v1/dashboard must return:

{
  "data": {
    "total_assets": "12795678.00",
    "active_portfolio_value": "12345678.00",
    "claims_portfolio_value": "450000.00",
    "portfolio_change_pct": "+2.34",
    "holdings_count": 42,
    "draft_holdings_count": 3,
    "last_updated": "2026-05-18T18:00:00Z",

    "sector_allocation": [
      {
        "name": "Financial Services",
        "sector": "Financial Services",
        "value": "6500000.00",
        "pct": "52.65"
      }
    ],

    "top_holdings": [
      {
        "ticker": "DANGCEM",
        "company": "Dangote Cement PLC",
        "value": "4500000.00",
        "num_shares": 10000,
        "return_pct": "+12.50"
      }
    ],

    "recent_transactions": [
      {
        "date": "2026-05-18",
        "ticker": "GTCO",
        "type": "buy",
        "num_shares": 500,
        "net_amount": "14375.00"
      }
    ],

    "claims_summary": {
      "total_claims": 40,
      "pending": 28,
      "approved": 5,
      "paid": 7,
      "total_expected": "1200000.00",
      "total_received": "450000.00"
    }
  },
  "error": null
}

CRITICAL: All monetary values are strings. All numeric counts are integers.

## Open Bugs to Fix Before Marking Complete

BUG-001 — Charts blank:
  dashboard.py must add "name" field to sector_allocation (Recharts requires it)
  dashboard.py must stringify all numeric values
  _app.dashboard.tsx must parseFloat at Recharts boundary
  Charts must be wrapped in <div style={{height:N}}><ResponsiveContainer>

BUG-004 — Theme toggle icon static:
  useTheme.ts must use useState for resolvedTheme
  Navbar icon must be conditional on resolvedTheme

BUG-005 — Bell not showing items:
  useActionItems must default holdings to [] when undefined
  Must guard against isLoading state

See .context/current-issues.md for full fix details.

## Layout

Navbar (top):
  Left: "EPM" wordmark
  Right: [Theme toggle] [Bell with badge] [User avatar]
  NO edit mode toggle on dashboard — this page is always read-only

KPI row (4 cards):
  Total Assets | Active Portfolio | Claims Portfolio | Holdings Count
  Values animate with useCountUp hook

Charts row:
  Left (55%): Sector Allocation donut
    data: sector_allocation from API
    dataKey="value" (float, parsed from string)
    nameKey="name" (must be "name" field — not "sector")
  Right (45%): Top Holdings horizontal bar
    Toggle: [By Value ₦] [By Shares]  — default: By Value
    data: top_holdings from API

Bottom row (3 cards):
  Recent Transactions | Action Items | [Reserved]

## Action Items Card Logic

Derived from useActionItems() hook (not a separate API endpoint):

  Draft holdings count > 0  → "N holdings pending publish" → link to /holdings
  Days since last_updated > 7 → "Prices not updated in N days" → link to /settings/price-entry
  claims_summary.approved > 0 → "N claim approved — collect payout" → link to /registrars
  All clear → green checkmark + "Portfolio up to date"

Bell badge = count of action items (amber, top-right of bell icon)
Bell click = dropdown panel with last 5 items, closes on outside click

## Acceptance Checklist

### [API]
- [ ] GET /api/v1/dashboard returns 200
- [ ] sector_allocation items have "name" field (not just "sector")
- [ ] sector_allocation "value" is a JSON string (not float)
- [ ] top_holdings "value" is a JSON string (not float)
- [ ] recent_transactions "net_amount" is a JSON string (not float)
- [ ] last_updated field is present (ISO 8601 string)

### [UI]
- [ ] Edit mode toggle NOT visible anywhere on /dashboard
- [ ] Total assets KPI shows animated count-up
- [ ] Sector allocation donut renders with coloured segments + percentage labels
- [ ] Top holdings bar chart renders (By Value default)
- [ ] Clicking "By Shares" toggle updates chart data
- [ ] Chart shows at most 10 holdings
- [ ] Recent transactions shows real data (not zeroes)
- [ ] Action items card shows correct alerts based on current state
- [ ] Bell badge shows count when items exist
- [ ] Bell dropdown opens on click, closes on outside click
- [ ] Theme toggle: clicking moon → dark mode, icon changes to sun
- [ ] Theme toggle: clicking sun → light mode, icon changes to moon
- [ ] Theme persists after page reload
- [ ] No console errors on load

## Sign-Off
- [ ] All checklist items passing
- [ ] BUG-001, BUG-004, BUG-005 resolved
- [ ] progress-tracker.md updated to ✅ Complete
- [ ] HO filed in docs/handovers/