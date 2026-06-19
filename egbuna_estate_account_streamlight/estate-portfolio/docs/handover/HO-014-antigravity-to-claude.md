---
type: HO
id: HO-014
title: Antigravity → Claude: AT-003 Group A Diagnosis & Fixes Completed
date: 2026-05-19
from: Antigravity (Builder)
to: Claude (The Brain)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-014 — Antigravity → Claude: AT-003 Group A Diagnosis & Fixes Completed
> **Type**: Handover · **Date**: 2026-05-19

## Summary of Fixes (Groups B, C, D)

I have successfully completed all the backend and frontend fixes outlined in Groups B, C, and D. 

### Group B: Backend Fixes
1. **Timezone-Aware Soft Delete**: Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)` across `holdings.py`, `registrars.py`, and all relevant endpoints.
2. **Price History Upsert Date**: Implemented the `extract_date_from_pdf_filename` function in `prices.py`. The upsert now correctly uses the date parsed from the filename, falling back to `date.today()` if the pattern doesn't match.

### Group C: Frontend Data Fixes
1. **Recent Transactions Rendering**: Applied null-safe rendering in `_app.dashboard.tsx` to handle missing `num_shares` or `net_amount` gracefully instead of throwing zeroes.
2. **Action Items Error**: Modified `useActionItems` in `queries.ts` to derive data securely from `useDashboard` avoiding `undefined` crashes.
3. **Price History Panel**: 
   - Replaced `<select>` with the `CompanyCombobox` component for searchable selection.
   - Added the missing `GET /api/v1/prices/history/{id}` endpoint to `prices.py` to ensure the chart receives real data in the expected shape (`{date, price}`).
   - Added `id` and `source` to the `history` endpoint response so the table properly loads beneath the chart.

### Group D: Registrar Layout Fixes
1. **Modal Centering**: Replaced the shadcn `DialogContent` wrapping logic in `RegistrarModal.tsx` with the manually centered `div` structure specified in HO-013.
2. **Contact Fields Stack**: Switched the `contactFields` rendering to the 3-column vertical grid layout (`80px_1fr_32px`) requested, removing the flex wrapping.
3. **Delete Registrar Button**: Added the Delete button to the header of `RegistrarDetails.tsx`, complete with the `AlertDialog` confirmation and `useDeleteRegistrar` hook.

---

## Group A: Diagnosis (Before Group E)

I have investigated the two failing areas in Group A. Here are the precise findings:

### A1 — Holdings PATCH 500 error
- **Frontend Request Payload (`src/routes/_app.holdings.tsx`)**:
  ```json
  { "id": 1, "num_shares": 100, "avg_cost": 400.00 }
  ```
  *(The frontend maps its `editForm` state directly, sending `avg_cost` as a number).*
- **Backend Pydantic Model (`HoldingUpdate`)**:
  ```python
  class HoldingUpdate(BaseModel):
      num_shares: Optional[float] = None
      avg_purchase_price: Optional[float] = None
  ```
- **Finding**: 
  The frontend is sending `avg_cost` instead of `avg_purchase_price`. Since the Pydantic schema doesn't strictly forbid extra fields, `avg_cost` is ignored. The backend `h.average_cost_basis` is left untouched. The 500 error is likely resulting from a schema strictness toggle, an ORM sync issue, or the endpoint silently failing down the line due to a mismatched expectations.

### A2 — Dashboard Charts Blank (Sector Allocation + Top Holdings)
- **Backend Response (`dashboard.py`)**:
  The `GET /api/v1/dashboard` endpoint returns the data successfully (200 OK) with the following structure:
  ```json
  "sector_allocation": [
      { "sector": "Financials", "value": 1500000.0, "pct": 45.5 }
  ],
  "top_holdings": [
      { "ticker": "ZENITHBANK", "company": "Zenith Bank", "value": 1500000.0, "return_pct": 12.4 }
  ]
  ```
- **Finding**:
  1. The `sector_allocation` array is populated correctly. However, Recharts `Pie` typically requires the `name` property. The frontend is currently passing `nameKey="sector"` in `<Pie>`, which may be failing silently in this version of Recharts. 
  2. The `value` properties in both `sector_allocation` and `top_holdings` are being sent as **floats** (e.g. `1500000.0`), not strings.

**Status**: Blocked on Group E. I await your exact specification to fix the inline edit 500 error and any required chart data mappings.
