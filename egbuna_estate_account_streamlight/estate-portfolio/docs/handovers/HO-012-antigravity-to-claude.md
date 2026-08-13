---
type: HO
id: HO-012
title: Handover from Antigravity to Claude (Post HO-011 Fixes)
status: ACTIVE
version: 1.0
created: 2026-05-19
owner: Antigravity
---

# [HO] HO-012 — Antigravity to Claude (Post HO-011 Fixes)

## 1. What Was Just Completed (HO-011)

I have executed the requirements from `HO-011` and addressed the subsequent bug found during testing. All code is pushed to the `test` branch:

1. **Price Upload 500 Error Fix**: 
   - The `POST /api/v1/prices/upload-pdf` endpoint was throwing an `IntegrityError` (500) because the `price_history` table has a `UNIQUE(company_id, price_date)` constraint, and NGX PDFs can contain duplicate tickers. 
   - **Resolution**: Implemented an upsert pattern. The endpoint now pre-fetches `today`'s price history into a dictionary, updates the object if it exists, and appends newly created objects to the dictionary during the loop to prevent duplicate inserts for the same company.
   - **History Tracking**: The endpoint now correctly inserts records into the `price_history` table, which powers the charts.

2. **Holdings Soft Delete**: 
   - **Resolution**: Updated `soft_delete_holding` to use `datetime.utcnow()` instead of timezone-aware UTC. This resolves the filtering mismatch where the row remained in the UI despite a 200 OK response.

3. **Global Edit Mode Glitch**: 
   - **Resolution**: Added a `useEffect` to `_app.holdings.tsx` that clears `editingRowId` and closes any open drawers whenever `editMode` is toggled off.

4. **Add Holding Drawer Redesign**: 
   - **Resolution**: Removed the inline "new" row from the Holdings table. Created the `AddHoldingDrawer` component and wired it to the `[+ Add Holding]` button. It handles duplicate checks and properly submits the `status` flag.

5. **Phase 3C Documentation**: 
   - **Resolution**: Added `Section 9` to `BR-002-price-entry.md` documenting the Batch Upload spec and created `features/batch_upload.feature` covering the scenarios.

## 2. Current State & Failing Acceptance Tests

The user has provided an updated run of `AT-003-dashboard-holdings-registrars-pricehist.md`. The test shows significant UI/UX bugs that require your architectural review and planning:

### Key Failing Areas for Claude to Address:
- **Holdings Inline Editing (SC-UI-024 to SC-UI-026)**: User is unable to save edits. API throws 500 errors ("Average cost must be a positive number"), negative numbers aren't blocked intuitively, and the UI layout is cramped.
- **Registrar UI (SC-UI-034 to SC-UI-040)**: The layout for extra fields is "horrible" (bad flex/grid gaps), the modal is off-center, and the Delete button is completely missing from the UI.
- **Price History Page (SC-UI-041 to SC-UI-046)**: Dropdown is not searchable, chart does not load, and the table below the chart is missing.
- **Dashboard Charts (SC-UI-009 to SC-UI-018)**: Sector allocation chart is blank. Top Holdings chart is blank. Recent Transactions shows zeroes and old data. Action Item cards are throwing errors or failing to clear.

## 3. Next Steps for Claude

**Claude (The Brain)**, please take over and:
1. Review the `AT-003` failures in detail.
2. Provide a structured plan (e.g., `HO-013`) prioritizing these UI fixes. 
3. Determine if backend model adjustments are required for the 500 errors occurring on Holdings inline edit patches, or if it's strictly a frontend payload mismatch.
4. Provide layout/CSS token instructions for the Registrar modal and contact fields to resolve the user's aesthetic complaints.
