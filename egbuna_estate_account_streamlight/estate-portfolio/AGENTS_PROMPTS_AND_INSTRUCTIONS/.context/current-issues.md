# current-issues.md — Active Bugs Only
# GITIGNORED — do not commit this file
# Delete entries when bugs are resolved

---

## BUG-001 — Dashboard Charts Blank

Layer: Frontend (UI) + Backend (API contract)
Component: _app.dashboard.tsx + dashboard.py
Severity: High — core feature non-functional

Root cause:
  Backend sends sector_allocation with "sector" field (not "name")
  Recharts Pie requires dataKey="value" (number) but backend sends strings
  Backend top_holdings "value" field is a float not a string

Fix spec: HO-015 Fixes 4 and 5
Files to change:
  backend/app/routers/dashboard.py
    → Add "name" field to sector_allocation items (same value as "sector")
    → Stringify all numeric fields: str(total), str(round(pct, 2))
  estate-portfolio-manager/src/routes/_app.dashboard.tsx
    → Parse strings to floats at Recharts boundary only
    → parseFloat(d.value) for chart sizing, fmtNaira(d.value) for tooltip
    → Wrap charts in <div style={{width:'100%', height:N}}><ResponsiveContainer>
    → Filter zero-value items before passing to Recharts

Acceptance:
  [API] sector_allocation items have "name" field
  [API] "value" in sector_allocation is a JSON string
  [UI]  Donut chart renders with coloured segments
  [UI]  Bar chart renders with horizontal bars

---

## BUG-002 — Holdings Inline Edit Cursor Jumps

Layer: Frontend (UI)
Component: _app.holdings.tsx
Severity: High — feature unusable

Root cause:
  Edit form state is held in the parent HoldingsPage component.
  Every keystroke updates parent state → React re-renders entire table
  → input element unmounts and remounts → cursor position lost.

Fix spec: HO-018 BUG-3
Files to change:
  estate-portfolio-manager/src/components/holdings/InlineEditRow.tsx (CREATE NEW)
    → Child component with its own useState for shares and avgCost
    → Parent table never re-renders on keystroke
    → onSave(id, data) and onCancel() callbacks to parent

  estate-portfolio-manager/src/routes/_app.holdings.tsx
    → Replace inline edit cells with <InlineEditRow> component
    → editingRowId state stays in parent (just the ID, not the form values)

Acceptance:
  [UI]  Typing in shares field does not lose cursor position
  [UI]  Cancel button is visible on the editing row
  [UI]  Toggling edit mode OFF clears editing row immediately

---

## BUG-003 — POST /api/v1/holdings 500 Error

Layer: Backend (API)
Component: backend/app/routers/holdings.py
Severity: Critical — Add Holding completely broken

Root cause: Unconfirmed. Most likely one of:
  A: Missing user_id on Holding insert
  B: UNIQUE(company_id) constraint violation (company already has holding)
  C: Missing NOT NULL field in insert payload

Diagnosis needed:
  docker compose -f docker-compose.v2.yml logs epm_v2 --tail=50 | grep -A5 "500\|Error\|holding"

Fix depends on log output. See HO-018 BUG-1 for full diagnosis tree.

Acceptance:
  [API]  POST /api/v1/holdings with valid payload returns 201
  [DB]   New row appears in holdings table after POST
  [UI]   Add Holding drawer creates holding and shows in table

---

## BUG-004 — Theme Toggle Icon Does Not Change

Layer: Frontend (UI)
Component: src/hooks/useTheme.ts + Navbar.tsx
Severity: Medium — visual feedback missing

Root cause:
  useTheme hook reads resolvedTheme from document.documentElement.classList
  without storing it in useState. No state = no re-render = icon never updates.

Fix spec: HO-018 BUG-4
Files to change:
  src/hooks/useTheme.ts
    → Add useState<'light'|'dark'> for resolvedTheme
    → toggleTheme() calls setResolvedTheme(next) to trigger re-render
  src/components/layout/Navbar.tsx
    → Icon conditional on resolvedTheme from hook
    → resolvedTheme === 'light' ? <Moon /> : <Sun />

Acceptance:
  [UI]  Moon icon visible in light mode
  [UI]  Clicking moon shows Sun icon and dark theme activates
  [UI]  Clicking sun shows Moon icon and light theme restores
  [UI]  Theme persists after page reload (no flash)

---

## BUG-005 — Notification Bell Not Showing Items

Layer: Frontend (UI)
Component: src/api/queries.ts (useActionItems hook)
Severity: Medium — action items invisible

Root cause:
  useActionItems() crashes when useDashboard() returns undefined (loading state)
  .filter() called on undefined → TypeError thrown → hook returns nothing

Fix spec: HO-018 BUG-5
Files to change:
  src/api/queries.ts
    → const { data: holdings = [] } = useHoldings()
    → const { data: dashboard, isLoading } = useDashboard()
    → if (isLoading || !dashboard) return { items: [], count: 0 }
    → All array operations with optional chaining

Acceptance:
  [UI]  Bell shows amber numbered badge when draft holdings exist
  [UI]  Bell shows badge when prices are stale (> 7 days)
  [UI]  Clicking bell opens dropdown with up to 5 items
  [UI]  No console errors from useActionItems
