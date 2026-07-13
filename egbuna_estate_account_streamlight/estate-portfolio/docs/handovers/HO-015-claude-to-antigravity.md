---
type: HO
id: HO-015
title: Claude → Antigravity: Group E Complete Fix Spec
date: 2026-05-19
from: Claude (The Brain)
to: Antigravity (Builder)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-015 — Claude → Antigravity: Group E Fix Spec
> **Type**: Handover · **Date**: 2026-05-19

---

## Root Causes (Confirmed from A1 + A2 Diagnosis)

| Bug | Root Cause | Fix Location |
|-----|-----------|-------------|
| Holdings PATCH 500 | Frontend sends `avg_cost` (wrong name) as float (wrong type) | Frontend + Backend |
| Dashboard charts blank | Backend sends floats not strings; `name` field missing for Recharts | Backend + Frontend |

---

## Fix 1 — Backend: `HoldingUpdate` Pydantic Model

File: `backend/app/routers/holdings.py`

Replace the existing `HoldingUpdate` model with:

```python
from decimal import Decimal, InvalidOperation
from typing import Optional
from pydantic import BaseModel, field_validator

class HoldingUpdate(BaseModel):
    num_shares: Optional[int] = None
    avg_purchase_price: Optional[str] = None

    @field_validator("num_shares")
    @classmethod
    def validate_shares(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Shares must be greater than zero")
        return v

    @field_validator("avg_purchase_price")
    @classmethod
    def validate_avg_price(cls, v):
        if v is None:
            return v
        try:
            d = Decimal(v)
        except (InvalidOperation, TypeError):
            raise ValueError("Average cost must be a valid number")
        if d <= 0:
            raise ValueError("Average cost must be a positive number")
        return v
```

Also update the PATCH endpoint to use the correct field name when
writing to the ORM model:

```python
@router.patch("/{holding_id}")
async def update_holding(
    holding_id: int,
    payload: HoldingUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(Holding)
        .where(Holding.id == holding_id)
        .where(Holding.deleted_at.is_(None))
    )
    holding = result.scalar_one_or_none()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    if payload.num_shares is not None:
        holding.num_shares = payload.num_shares

    if payload.avg_purchase_price is not None:
        holding.avg_purchase_price = Decimal(payload.avg_purchase_price)
        # ↑ Write to avg_purchase_price, not avg_cost or average_cost_basis

    await db.commit()
    await db.refresh(holding)

    return {
        "data": {
            "id": holding.id,
            "num_shares": holding.num_shares,
            "avg_purchase_price": str(holding.avg_purchase_price),
        },
        "error": None,
    }
```

---

## Fix 2 — Frontend: Holdings Inline Edit Payload

File: `estate-portfolio-manager/src/routes/_app.holdings.tsx`

Find the `updateHoldingMutation` call and fix the payload shape:

```typescript
// BEFORE (wrong field name, wrong type)
updateHoldingMutation.mutate({
  id: editingRowId,
  avg_cost: Number(editForm.avg_purchase_price),
});

// AFTER (correct field name, string type, id in URL)
updateHoldingMutation.mutate({
  id: editingRowId,
  num_shares: editForm.num_shares,
  avg_purchase_price: String(editForm.avg_purchase_price),
});
```

Fix the mutation function in `queries.ts`:

```typescript
export function useUpdateHolding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: {
      id: number;
      num_shares?: number;
      avg_purchase_price?: string;  // string per API contract
    }) =>
      fetch(`/api/v1/holdings/${id}`, {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),  // id excluded from body, only in URL
      }).then(r => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
```

---

## Fix 3 — Frontend: Client-Side Validation Before API Call

Add validation in the inline edit save handler — reject before
any API call is made:

```typescript
const handleInlineSave = () => {
  const shares = Number(editForm.num_shares);
  const price = parseFloat(editForm.avg_purchase_price);

  if (!Number.isInteger(shares) || shares <= 0) {
    setRowError("Shares must be a whole number greater than zero");
    return;
  }

  if (isNaN(price) || price <= 0) {
    setRowError("Average cost must be a positive number");
    return;
  }

  setRowError(null);
  updateHoldingMutation.mutate({
    id: editingRowId as number,
    num_shares: shares,
    avg_purchase_price: price.toFixed(2),  // always 2dp string
  });
};
```

Display `rowError` below the inline edit row:

```typescript
{rowError && (
  <tr>
    <td colSpan={12}>
      <p className="text-xs text-[var(--accent-red)] px-3 py-1">
        {rowError}
      </p>
    </td>
  </tr>
)}
```

---

## Fix 4 — Backend: Dashboard Serialisation

File: `backend/app/routers/dashboard.py`

Fix `sector_allocation` and `top_holdings` serialisation:

```python
# sector_allocation — add "name" field, stringify value and pct
"sector_allocation": [
    {
        "name": row.sector,          # Recharts requires "name"
        "sector": row.sector,        # keep for tooltip display
        "value": str(row.total),     # string per API contract
        "pct": str(round(row.pct, 2)),
    }
    for row in sector_rows
],

# top_holdings — stringify all numeric fields
"top_holdings": [
    {
        "ticker": h.ticker,
        "company": h.company_name,
        "value": str(h.current_value) if h.current_value else "0.00",
        "return_pct": str(round(h.return_pct, 2)) if h.return_pct else "0.00",
    }
    for h in top_holdings
],
```

---

## Fix 5 — Frontend: Recharts Data Parsing

Recharts requires numbers for bar/pie sizing. Parse strings at the
component boundary — never in the API hook or query.

File: `estate-portfolio-manager/src/components/dashboard/SectorAllocationChart.tsx`

```typescript
// Parse strings → numbers for Recharts ONLY
const chartData = (sectorAllocation ?? []).map(s => ({
  name: s.name,                    // string — Recharts label
  value: parseFloat(s.value),      // number — Recharts sizing
  displayPct: s.pct,               // string — tooltip display
  displayValue: fmtNaira(s.value), // string — tooltip display
}));

// Recharts Pie
<Pie
  data={chartData}
  dataKey="value"     // the number field
  nameKey="name"      // must be "name"
  cx="50%"
  cy="50%"
>
  {chartData.map((_, idx) => (
    <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
  ))}
</Pie>
```

File: `estate-portfolio-manager/src/components/dashboard/TopHoldingsChart.tsx`

```typescript
const chartData = (topHoldings ?? []).map(h => ({
  ticker: h.ticker,
  value: parseFloat(h.value),           // number for bar width
  return_pct: parseFloat(h.return_pct), // number for end label colour
  displayValue: fmtNaira(h.value),      // string for tooltip
  displayReturn: h.return_pct,          // string for end label
}));

// Bar chart
<BarChart data={chartData} layout="vertical">
  <YAxis dataKey="ticker" type="category" />
  <XAxis type="number" />
  <Bar dataKey="value" fill="var(--accent-lavender)">
    <LabelList
      dataKey="displayReturn"
      position="right"
      style={{
        fill: chartData[0]?.return_pct >= 0
          ? 'var(--accent-green)'
          : 'var(--accent-red)',
        fontSize: 12,
        fontFamily: 'DM Mono',
      }}
    />
  </Bar>
</BarChart>
```

---

## Fix 6 — Null Safety Throughout

Apply these null-safe patterns universally across all chart
and data components:

```typescript
// Arrays — always default to []
const sectorAllocation = dashboard?.sector_allocation ?? [];
const topHoldings = dashboard?.top_holdings ?? [];
const recentTransactions = dashboard?.recent_transactions ?? [];

// Monetary strings — always parse safely
const safeParseFloat = (v: string | null | undefined): number =>
  v ? parseFloat(v) : 0;

// Formatted display — always handle null
const displayValue = (v: string | null | undefined): string =>
  v ? fmtNaira(v) : "—";

const displayPct = (v: string | null | undefined): string =>
  v ? fmtPct(v) : "—";
```

---

## Acceptance Criteria for HO-016

```
Holdings Inline Edit:
  [ ] PATCH /api/v1/holdings/{id} returns 200 when valid payload sent
  [ ] Field name confirmed as avg_purchase_price in request body
  [ ] Field type confirmed as string "400.00" in request body
  [ ] Saving shares = -10 shows client-side error, no API call
  [ ] Saving avg_cost = 0 shows client-side error, no API call
  [ ] Saving valid values updates the row and refreshes dashboard total

Dashboard Charts:
  [ ] Sector allocation donut renders with coloured segments
  [ ] Each segment label shows sector name and percentage
  [ ] Top holdings bar chart renders with horizontal bars
  [ ] Switching By Value / By Shares toggle updates the chart
  [ ] No console errors relating to Recharts nameKey or dataKey
  [ ] sector_allocation API response confirmed: "value" is a string

After all fixes:
  [ ] Re-run AT-003 for SC-UI-020 through SC-UI-031 (Holdings)
  [ ] Re-run AT-003 for SC-UI-009 through SC-UI-013 (Dashboard charts)
  [ ] Update PROJECT_STATUS.md
  [ ] Write HO-016 handover to Claude with AT-003 v2 results
```

---

## Summary: What Has Changed Across HO-011 to HO-015

For PROJECT_STATUS.md update after this sprint:

| Item | New Status |
|------|-----------|
| Holdings soft delete (timezone) | ✅ DONE |
| PDF date extraction from filename | ✅ DONE |
| Recent Transactions null-safe | ✅ DONE |
| useActionItems null-safe | ✅ DONE |
| Price History searchable dropdown | ✅ DONE |
| Price History chart + table | ✅ DONE |
| Registrar modal centered | ✅ DONE |
| Contact fields grid layout | ✅ DONE |
| Delete Registrar button | ✅ DONE |
| Holdings PATCH field name | 🔄 Fix in HO-015 |
| Holdings PATCH type (string) | 🔄 Fix in HO-015 |
| Holdings client-side validation | 🔄 Fix in HO-015 |
| Dashboard sector_allocation name field | 🔄 Fix in HO-015 |
| Dashboard values stringified | 🔄 Fix in HO-015 |
| Recharts data parsing (string→number) | 🔄 Fix in HO-015 |

**End of HO-015**
**Next**: Antigravity implements all 6 fixes → HO-016 to Claude with AT-003 v2
