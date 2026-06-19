---
type: HO
id: HO-013
title: Claude → Antigravity: AT-003 Fix Plan
date: 2026-05-19
from: Claude (The Brain)
to: Antigravity (Builder)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-013 — Claude → Antigravity: AT-003 Fix Plan
> **Type**: Handover · **Date**: 2026-05-19

---

## Execution Order

Fix in this exact sequence. Do not move to the next group until the
current group passes its acceptance criteria.

```
Group A — Diagnose first (you need information before fixing)
Group B — Backend fixes (no frontend changes needed)
Group C — Frontend data fixes (charts, transactions)
Group D — Frontend layout fixes (registrar modal, contact fields)
Group E — Holdings inline edit (blocked on Group A diagnosis)
```

---

## GROUP A — Diagnose Before Fixing (Do This First)

### A1 — Holdings PATCH 500 error

**Before writing any fix**, open DevTools → Network tab, trigger a
Holdings inline edit save, and capture the exact request payload.

Look for the PATCH request to `/api/v1/holdings/{id}`. Click it.
Go to the **Request** tab (not Response). Copy the exact JSON body.

Expected shape (what the backend's Pydantic model requires):
```json
{
  "num_shares": 100,
  "avg_purchase_price": "400.00"
}
```

Check whether the frontend is sending:
- `avg_purchase_price` as a float (`400.0`) → backend Pydantic rejects
- `avg_purchase_price` as empty string (`""`) → fails positive check
- `avg_purchase_price` as a valid string (`"400.00"`) → should pass
- A field name mismatch (`avg_cost` vs `avg_purchase_price`) → 422

Also check the **Response** tab for the full error detail — the 500
message body will tell you exactly which field failed validation and why.

Report the exact request payload and response body in HO-014.
**Do not attempt the fix until you have this information.**

### A2 — Dashboard charts blank (Sector Allocation + Top Holdings)

Open DevTools → Network tab → reload `/dashboard`.
Find the `GET /api/v1/dashboard` request.

Check:
1. Does it return 200?
2. Does the response body contain `sector_allocation` as a non-empty array?
3. Does `top_holdings` contain entries with `current_value` as non-null strings?
4. Are `current_value` fields strings or numbers?

If `sector_allocation` is an empty array `[]`:
- The issue is backend — holdings exist but their sectors are not
  being grouped correctly in `dashboard.py`
- Check: `SELECT sector, COUNT(*) FROM companies WHERE deleted_at IS NULL GROUP BY sector`
  — if this returns data, the aggregation query in dashboard.py is wrong

If `sector_allocation` has data but chart is blank:
- The issue is frontend — Recharts is receiving data but not rendering
- Check: add `console.log(sectorData)` before the PieChart render
- Common cause: data shape mismatch (Recharts expects `{name, value}`,
  not `{sector, pct}`)

Report findings in HO-014 alongside the Holdings payload.

---

## GROUP B — Backend Fixes (No diagnosis needed)

### B1 — Holdings soft delete: use timezone-aware datetime

The fix in HO-012 used `datetime.utcnow()` (naive datetime).
This can still cause filtering mismatches with timezone-aware columns.

Replace with:
```python
# routers/holdings.py — soft_delete_holding
from datetime import datetime, timezone

holding.deleted_at = datetime.now(timezone.utc)   # ✅ timezone-aware
# NOT: datetime.utcnow()                           # ❌ naive — causes tz mismatch
```

Apply the same pattern to ALL soft-delete operations across all routers.
Check: registrars.py, companies.py, dividends.py, transactions.py.
Any use of `datetime.utcnow()` for `deleted_at` must be replaced.

### B2 — Price history upsert: use date from PDF not always today

The current upsert uses `today` as the price date for all records.
This means uploading a PDF from last week incorrectly records all
prices as today's date, making the price history chart useless for
historical data.

Fix: extract the date from the PDF filename or first-page header.

```python
# routers/prices.py — upload_ngx_pdf

def extract_date_from_pdf_filename(filename: str) -> date | None:
    """
    NGX filenames follow patterns like:
      DAILY SUMMARY FOR 17-05-2026.pdf
      DAILY OFFICIAL LIST 17052026.pdf
    """
    import re
    # Try DD-MM-YYYY
    m = re.search(r'(\d{2})[.\-_ ](\d{2})[.\-_ ](\d{4})', filename)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    # Try DDMMYYYY
    m = re.search(r'(\d{2})(\d{2})(\d{4})', filename)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    return None

# In upload_ngx_pdf endpoint:
price_date = extract_date_from_pdf_filename(file.filename) or date.today()
# Use price_date everywhere instead of date.today()
```

If the filename contains no recognisable date, fall back to today.
Log a warning when the fallback is used so the user knows.

---

## GROUP C — Frontend Data Fixes

### C1 — Recent Transactions showing zeroes and old data

Cause: the dashboard API response's `recent_transactions` array likely
has `null` or `"0"` for `num_shares` and `net_amount`.

**Backend check** — in `dashboard.py`, the recent transactions query
must join to the `transactions` table and return real values:
```python
# Ensure the query returns:
{
    "date": tx.transaction_date.isoformat(),
    "ticker": tx.ticker,
    "type": tx.transaction_type,
    "num_shares": tx.num_shares,         # must not be null
    "net_amount": str(tx.net_amount),    # string per API contract
}
```

If `transactions` table is empty (no records yet), the card should
show the empty state — not zeroes. Check whether the frontend
renders `"0"` when the API returns `null` for these fields.

**Frontend fix** — in the Recent Transactions component:
```typescript
// Null-safe rendering
{tx.num_shares ?? "—"}
{tx.net_amount ? fmtNaira(tx.net_amount) : "—"}
```

### C2 — Action Items card errors

The `useActionItems()` hook derives data from `useHoldings()` and
`useDashboard()`. If either query is failing or returning unexpected
shapes, the hook throws.

Add a null-safe guard at the top of the hook:
```typescript
export function useActionItems() {
  const { data: holdings = [] } = useHoldings();
  const { data: dashboard } = useDashboard();

  return useMemo(() => {
    const items = [];
    // All array operations use optional chaining
    const draftCount = holdings?.filter(h => h.status === 'draft').length ?? 0;
    // ... rest of hook
  }, [holdings, dashboard]);
}
```

If `holdings` is undefined (query loading or error), default to `[]`
so `.filter()` never throws on undefined.

### C3 — Price History: dropdown not searchable, chart not loading, table missing

Three separate issues — fix in this order:

**C3a — Dropdown not searchable**

The company dropdown must use a combobox pattern, not a plain `<select>`.
Use the shadcn/ui `Command` + `Popover` pattern already used in the
Price Entry page company selector. Copy that component exactly.

```typescript
// src/components/price-history/CompanySelector.tsx
// Mirror the CompanyCombobox from price-entry page
// Key: filter companies client-side by typing ticker or name
```

**C3b — Chart not loading**

Check `usePriceHistory(companyId, days)` hook:
1. Is `companyId` being passed as a number or string?
   The hook's `enabled` condition checks `companyId !== null` —
   if companyId is `0` or `undefined`, the query never fires.
2. Does `GET /api/v1/prices/history/{id}?days=30` return data?
   Test with curl: `curl https://testdrive.epm.zubbystudio.shop/api/v1/prices/history/1?days=30`
3. Is the Recharts data array in `{date, price}` shape?
   Recharts LineChart requires: `[{ date: "2026-05-01", price: 450.00 }]`
   If the API returns `[{ recorded_date: "...", price: "450.00" }]`,
   the field names must be mapped before passing to Recharts.

**C3c — Table missing**

The table below the chart renders `price_history` records.
If the chart data loads but the table is missing, the table component
is likely conditionally rendered on a variable that is undefined.

Check: is the table inside an `{data && data.length > 0 && <Table />}`
guard that is never true because `data` is an object not an array?
Ensure `usePriceHistory` returns `r.data` (the array), not the full
`{data: [], meta: {}, error: null}` envelope.

---

## GROUP D — Registrar Layout Fixes

### D1 — Modal off-center

The Edit/Add Registrar modal must be centered in the viewport.
Use fixed positioning with CSS transform centering:

```typescript
// Modal overlay + container
<div className="fixed inset-0 z-50 flex items-center justify-center
                bg-black/40 backdrop-blur-sm">
  <div className="relative w-full max-w-lg mx-4
                  bg-[var(--bg-surface)] border border-[var(--border)]
                  rounded-xl shadow-[var(--shadow-modal)]
                  max-h-[90vh] overflow-y-auto p-6">
    {/* modal content */}
  </div>
</div>
```

Key classes:
- `fixed inset-0` — covers full viewport
- `flex items-center justify-center` — centers the modal card
- `max-h-[90vh] overflow-y-auto` — scrollable if content is tall
- `mx-4` — 16px margin on mobile

### D2 — Contact fields layout "horrible"

The extra contact fields list must use a clean vertical stack,
not flex-wrap. Each field row has three elements: type badge,
input, remove button.

```typescript
// ContactFieldsList.tsx
<div className="flex flex-col gap-3 mt-4">
  {extraFields.map((field, idx) => (
    <div key={idx}
         className="grid grid-cols-[80px_1fr_32px] gap-2 items-center">

      {/* Type badge — fixed 80px */}
      <span className="text-xs font-medium px-2 py-1 rounded-full
                       bg-[var(--bg-subtle)] text-[var(--text-secondary)]
                       text-center capitalize">
        {field.field_type}
      </span>

      {/* Input — fills remaining space */}
      <input
        value={field.field_value}
        onChange={e => updateField(idx, e.target.value)}
        placeholder={placeholderFor(field.field_type)}
        className="h-9 px-3 rounded-lg border border-[var(--border)]
                   bg-[var(--bg-surface)] text-[var(--text-primary)]
                   text-sm focus:outline-none focus:ring-2
                   focus:ring-[var(--accent-lavender)]"
      />

      {/* Remove button — fixed 32px */}
      <button
        onClick={() => removeField(idx)}
        className="w-8 h-8 flex items-center justify-center
                   text-[var(--text-muted)] hover:text-[var(--accent-red)]
                   rounded-lg hover:bg-[var(--bg-subtle)] transition-colors">
        <X size={14} />
      </button>

    </div>
  ))}
</div>
```

Placeholder helper:
```typescript
const placeholderFor = (type: string) => ({
  phone:   "e.g. 0800-555-0100",
  email:   "e.g. info@registrar.com.ng",
  address: "e.g. 2 Broad Street, Lagos",
  website: "e.g. https://registrar.com.ng",
  other:   "e.g. WhatsApp: 080...",
}[type] ?? "Enter value");
```

### D3 — Delete Registrar button missing from UI

The Delete button must appear in the registrar detail panel header,
alongside the Edit Registrar button. It is only visible when a
registrar is selected AND edit mode is ON.

```typescript
// RegistrarDetails.tsx — detail panel header
<div className="flex items-center gap-2">
  <h2 className="text-lg font-semibold text-[var(--text-primary)] flex-1">
    {registrar.name}
  </h2>

  {isAdmin() && editMode && (
    <>
      <button
        onClick={() => setShowEditModal(true)}
        className="btn-secondary text-sm px-3 py-1.5">
        Edit Registrar
      </button>
      <button
        onClick={() => setShowDeleteConfirm(true)}
        className="px-3 py-1.5 text-sm rounded-lg font-medium
                   text-[var(--accent-red)] border border-[var(--accent-red)]
                   hover:bg-[var(--accent-red)] hover:text-white
                   transition-colors">
        Delete
      </button>
    </>
  )}
</div>

{/* Confirmation dialog */}
{showDeleteConfirm && (
  <ConfirmDialog
    title={`Delete ${registrar.name}?`}
    message={`This will remove all linked requirements and documents.
      ${registrar.linked_company_count > 0
        ? `${registrar.linked_company_count} companies will be unlinked.`
        : ''}`}
    confirmLabel="Delete"
    danger
    onConfirm={() => {
      deleteRegistrarMutation.mutate(registrar.id);
      setShowDeleteConfirm(false);
    }}
    onCancel={() => setShowDeleteConfirm(false)}
  />
)}
```

---

## GROUP E — Holdings Inline Edit Fix

**Blocked until Group A diagnosis is complete.**

Once Antigravity captures the exact PATCH request payload and 500
response body, report them in HO-014. Claude will then specify
the exact fix — either:

- Frontend: fix the field name or type being sent
- Backend: fix the Pydantic validator to accept the incoming format
- Both: align the contract on both sides

Do not attempt to fix the inline edit 500 error by guessing.
The diagnosis in Group A takes 5 minutes and prevents 2 hours
of wrong fixes.

---

## Acceptance Criteria for HO-014

Antigravity's next handover (HO-014) must confirm:

```
Group A:
  [ ] Exact PATCH /api/v1/holdings/{id} request payload reported
  [ ] Exact 500 response body reported
  [ ] Dashboard /api/v1/dashboard response shape confirmed
      (sector_allocation and top_holdings arrays inspected)

Group B:
  [ ] datetime.utcnow() replaced with datetime.now(timezone.utc)
      across ALL routers
  [ ] PDF date extraction from filename implemented and tested

Group C:
  [ ] Recent Transactions shows real data or correct empty state
  [ ] useActionItems() null-safe — no more crashes
  [ ] Price History dropdown is searchable (combobox pattern)
  [ ] Price History chart loads when company selected
  [ ] Price History table renders below chart

Group D:
  [ ] Registrar modal is centered on screen
  [ ] Contact fields use grid layout (80px badge / 1fr input / 32px X)
  [ ] Delete Registrar button visible in detail panel (edit mode, admin)
  [ ] Delete confirmation dialog mentions linked company count

Group E:
  [ ] Holdings inline edit PATCH succeeds (after diagnosis in A1)
  [ ] Negative shares blocked client-side before API call
  [ ] Avg cost validation gives clear error message
```

---

## Update PROJECT_STATUS.md After This Sprint

When HO-014 confirms items complete, update `docs/PROJECT_STATUS.md`:
- Move fixed items from ⚠️ PARTIAL to ✅ DONE
- Move diagnosed items from unknown to their correct state
- Add Group E fix to ✅ DONE once complete

**End of HO-013**
**Next**: Antigravity completes Group A diagnosis → reports in HO-014