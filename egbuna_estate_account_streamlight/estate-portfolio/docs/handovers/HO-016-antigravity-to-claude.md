---
type: HO
id: HO-016
title: Antigravity → Claude: Group E Complete Fix Spec Implementation
date: 2026-05-19
from: Antigravity (Builder)
to: Claude (The Brain)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-016 — Antigravity → Claude: Group E Complete Fix Spec Implementation
> **Type**: Handover · **Date**: 2026-05-19

## Summary of Completed Work

As requested in **HO-015**, I have successfully implemented all six fixes for Group E (Holdings inline edit bug and Dashboard charts rendering issue).

1. **Fix 1 — Backend: `HoldingUpdate` Pydantic Model**
   - File: `backend/app/routers/holdings.py`
   - Updated the `HoldingUpdate` model to accept `num_shares` as `Optional[int]` and `avg_purchase_price` as `Optional[str]`.
   - Added Pydantic field validators `validate_shares` and `validate_avg_price` to catch non-positive integers/numbers and invalid decimals.
   - Updated the `PATCH` endpoint logic to assign `Decimal(payload.avg_purchase_price)` to `holding.average_cost_basis` (using the correct ORM attribute).

2. **Fix 2 & 3 — Frontend: Holdings Inline Edit Payload & Validation**
   - Files: `estate-portfolio-manager/src/routes/_app.holdings.tsx` & `queries.ts`
   - Updated `updateHoldingMutation.mutateAsync` to correctly send `avg_purchase_price` as a string (`avgCost.toFixed(2)`) and `num_shares` as a number.
   - Restructured the inline-edit component rows by encapsulating them with `<Fragment>` and rendering a `rowError` right below the edit form if client-side validation triggers an error.
   - Adjusted `queries.ts` to strictly type the `useUpdateHolding` payload.

3. **Fix 4 — Backend: Dashboard Serialisation**
   - File: `backend/app/routers/dashboard.py`
   - Ensured string serialisation for numeric values in `sector_allocation` (`value` and `pct`) and `top_holdings` (`value` and `return_pct`).
   - Sorted sector allocation cleanly prior to assigning the final array items to avoid string-sorting issues.
   - Added the explicit `name` field to `sector_allocation` arrays, fulfilling Recharts structural dependencies.

4. **Fix 5 & 6 — Frontend: Recharts Data Parsing & Null Safety**
   - File: `estate-portfolio-manager/src/routes/_app.dashboard.tsx`
   - Standardized safe parsing mappings `safeParseFloat`, `displayValueStr`, and `displayPctStr` at the top level of `DashboardPage`.
   - Adapted `<PieChart>` and `<BarChart>` to use properly hydrated arrays (`sectorChartData` and `topHoldingsChartData`), correctly referencing mapped `value`s as parsed floats while displaying tooltip information via the formatted string variants.
   - Included `LabelList` rendering within the `<BarChart>`.
   - Applied extensive null-safety arrays (`?? []`) to data variables mapped out from the `useDashboard` payload.

5. **PROJECT_STATUS.md Updates**
   - Updated the open bugs table reflecting that items 1, 2, 3, 5, and 6 are now ✅ DONE via `HO-014` and `HO-016`.

** All the fixed bugs will now be subject to the test that will be carried out on the next HO from Claude. Most of the fixed features have not been properly tested. 

## Next Steps for [Malachy E] and Claude
Please verify the implementations by running AT-003 for both Holdings (`SC-UI-020` to `SC-UI-031`) and Dashboard Charts (`SC-UI-009` to `SC-UI-013`).

### Important SDLC Process Update Request
The USER explicitly requested that moving forward, **instead of mutating an existing test case file (e.g., modifying `AT-003`)**, you should create a **follow-up test case with a 4-digit number (e.g., `AT-0031`)**. 
This new file should carry over all the skipped, failed, and pending cases from the previous run. Please incorporate this into your testing process and SDLC governance for the next phase.

**End of HO-016**
