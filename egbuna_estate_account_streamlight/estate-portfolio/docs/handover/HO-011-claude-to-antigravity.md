---
type: HO
id: HO-011
title: Claude → Antigravity: HO-010 Review, Add Holding Redesign, Bug Fixes, Phase 3C Batch Upload
date: 2026-05-18
from: Claude (The Brain)
to: Antigravity (Builder)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-011 — Claude → Antigravity: HO-010 Review
> **Type**: Handover · **Date**: 2026-05-18

---

## Section 1: Financial Definitions (For User Reference)

Add these to BR-001 Section 6 and to the Wiki under a "Glossary" page.
These are the exact formulas the user should test against.

| Field | Formula | Example |
|-------|---------|---------|
| Average Cost | `(Σ shares_bought × price_per_buy) / total_shares` | 60×₦380 + 40×₦420 / 100 = **₦396** |
| Cost Basis | `num_shares × avg_purchase_price` | 100 × ₦396 = **₦39,600** |
| Current Value | `num_shares × current_price` | 100 × ₦450 = **₦45,000** |
| Return [%] | `((current_value − cost_basis) / cost_basis) × 100` | (45000−39600)/39600 = **+13.64%** |
| Status | Lifecycle flag — `draft` excluded from totals; `live` included | n/a |

**Status clarification for the user**: Status is not a financial calculation.
It controls whether a holding counts toward your portfolio value. A `draft`
holding is one you have added to the system but not yet confirmed — useful
for staging a new purchase before publishing it to your live portfolio view.

---

## Section 2: Architectural Decisions Locked

| Item | Decision |
|------|----------|
| Add Holding UX | **Slide-out drawer** (right side, 420px) |
| Price History ingestion | **Manual now** + **batch endpoint in Phase 3C** |
| Edit mode toggle off → reset editing row | Antigravity fixes via useEffect (confirmed) |
| Delete holding bug | Antigravity investigates useDeleteHolding mutation (confirmed) |

---

## Section 3: Add Holding — Redesign to Slide-Out Drawer

### Why drawer over modal

A modal blocks the entire table — the user cannot see their existing
holdings while adding a new one. A drawer slides in from the right,
leaving the table visible. This is important because the user will
want to check existing positions (sector allocation, avg cost) while
adding a new holding. It also gives room for future fields (notes,
purchase date, broker, transaction reference) without the form feeling
cramped.

### Drawer specification

```
TRIGGER: [+ Add Holding] button (admin, editMode)
         Clicking triggers opens the drawer
         The table remains fully visible and scrollable

DRAWER LAYOUT (right side, 420px width):
  Header:
    "Add Holding"  ×close button
    Subtitle: "New holdings are created as Draft. Publish when ready."

  Form fields (vertical stack, 16px gap):

    Company *
      Searchable dropdown (typeahead from useCompanies())
      Each option: "[TICKER] — Company Name"
      Validates: company must not already have an existing live or
                 draft holding (show error inline if duplicate)

    Number of Shares *
      DM Mono input, integer only, min 1
      Label: "Shares held"

    Average Purchase Price (₦) *
      DM Mono input, decimal, min 0.01
      Label: "Avg cost per share"
      Helper text: "Weighted average across all purchases"

    Purchase Date
      Date picker, optional
      Defaults to today
      Used for XIRR calculation — encourage user to fill this in

    Notes
      Textarea, optional, 3 rows
      Placeholder: "e.g. Purchased via Stanbic IBTC, Ref: TXN12345"

    Status
      Toggle: [Draft] [Publish now]
      Default: Draft
      Helper: "Draft holdings are hidden from portfolio totals"

  Footer (sticky at drawer bottom):
    [Cancel]  ghost button — closes drawer, no API call
    [Save as Draft]  secondary button — POST with status='draft'
    [Save & Publish]  lavender primary — POST with status='live'

DRAWER BEHAVIOUR:
  - Opens with a 250ms slide-in from right animation
  - Backdrop overlay (rgba 0.3) on content area — clicking it closes drawer
  - Form resets when drawer closes
  - On successful save: drawer closes, table row appears (draft or live)
  - On error: error message shown inline in drawer, drawer stays open
  - Keyboard: Escape closes the drawer

GHERKIN UPDATES (SC-UI-027 revised):

  Scenario: SC-UI-027 (REVISED) Add Holding opens a slide-out drawer
    Given edit mode is ON
    When I click the [+ Add Holding] button
    Then a slide-out drawer opens from the right side of the screen
    And the holdings table remains visible behind the drawer
    And the drawer contains: Company dropdown, Shares, Avg Cost,
        Purchase Date, Notes, Status toggle
    And a [Save as Draft] and [Save & Publish] button are present

  Scenario: SC-UI-027b Closing the drawer discards unsaved input
    Given the Add Holding drawer is open with partial data entered
    When I click the × button or press Escape
    Then the drawer closes
    And no API call is made
    And the form is reset for next open
```

### Implementation notes

```typescript
// New component: src/components/holdings/AddHoldingDrawer.tsx
// Props: isOpen: boolean, onClose: () => void

// In Holdings page:
const [addDrawerOpen, setAddDrawerOpen] = useState(false);

// Button:
{isAdmin() && editMode && (
  <button onClick={() => setAddDrawerOpen(true)}>+ Add Holding</button>
)}

// Drawer:
<AddHoldingDrawer
  isOpen={addDrawerOpen}
  onClose={() => setAddDrawerOpen(false)}
/>

// On successful mutation in drawer:
queryClient.invalidateQueries({ queryKey: ['holdings'] });
queryClient.invalidateQueries({ queryKey: ['dashboard'] });
setAddDrawerOpen(false);
```

---

## Section 4: Bug Fixes

### Bug 1 — Global Edit Mode toggle leaves inline fields visible

```typescript
// In Holdings page component — add this useEffect:
useEffect(() => {
  if (!editMode) {
    setEditingRowId(null);    // clear any active inline edit
    setAddDrawerOpen(false);  // close add drawer if open
  }
}, [editMode]);
```

This ensures that when the user switches back to View Mode, all
inline editing state is immediately cleared. No stale input fields
remain visible.

### Bug 2 — Delete holding mutation not persisting

Investigate in this order:

1. Check network tab in DevTools when Delete is clicked:
   - Is `DELETE /api/v1/holdings/{id}` actually being called?
   - What HTTP status does it return?

2. If the request is not firing:
   - The `useDeleteHolding` mutation's `mutationFn` may have a path error
   - Verify: `fetch(\`/api/v1/holdings/${id}\`, { method: 'DELETE', credentials: 'include' })`

3. If the request fires but the row reappears after page refresh:
   - The backend soft-delete is setting `deleted_at` but the GET endpoint
     is not filtering it out
   - Verify in `routers/holdings.py`:
     `query.where(Holding.deleted_at.is_(None))`

4. If the request fires and returns 200 but the UI row stays:
   - The query invalidation is missing after mutation success
   - Add: `onSuccess: () => qc.invalidateQueries({ queryKey: ['holdings'] })`

---

## Section 5: Price History — Data Ingestion Strategy

### Phase 2 (Now): Manual Daily PDF Uploads

The user should upload each day's NGX Daily Official List PDF via
`/settings/price-entry` → Bulk PDF Upload. Each PDF upload creates
price_history records for all companies in the file with `source = 'ngx_pdf_upload'`.

**To populate 30 days of history**:
1. Download the last 30 NGX Daily Official List PDFs from
   `ngxgroup.com/exchange/data/data-library/`
2. Upload them one by one via the Price Entry page
3. The price_history chart will populate as uploads complete

This is manual but takes roughly 5 minutes per PDF upload.
The chart will show data immediately after each upload.

**Clarification on how price_history records are created**:
Each PDF upload should write to TWO places:
- `companies.current_price` — updates the live price (already implemented)
- `price_history` — inserts a historical record with the date from the PDF

**[VERIFY THIS]** — confirm the PDF upload endpoint is writing to
`price_history` table, not just updating `companies.current_price`.
If it is only updating `current_price`, add a `price_history` insert
to the `upload_ngx_pdf` endpoint:

```python
# In routers/prices.py — upload_ngx_pdf endpoint
# After updating company.current_price, also insert into price_history:
db.add(PriceHistory(
    company_id=company.id,
    price=price,
    recorded_date=today,       # or extract date from PDF filename
    source="ngx_pdf_upload",
))
```

### Phase 3C (Planned): Batch Historical Upload

**New endpoint**: `POST /api/v1/prices/batch-upload-pdf`

```
Accepts: multipart/form-data with multiple PDF files
         files[]: file1.pdf, file2.pdf, ... (up to 30 files)

Processing:
  1. Sort files by date (extracted from filename or first-page header)
  2. Process each PDF in chronological order
  3. For each file: run the existing PDF parser logic
  4. Write price_history records (not just current_price) for each file
  5. Update current_price only from the MOST RECENT file

Returns:
  {
    "data": {
      "files_processed": 30,
      "files_failed": 0,
      "total_prices_updated": 4200,
      "date_range": { "from": "2026-04-18", "to": "2026-05-18" },
      "failed_files": []
    }
  }

Frontend:
  /settings/price-entry right panel — add a second tab:
  [Single PDF] | [Batch Upload (up to 30 PDFs)]

  Batch tab:
    Multi-file drop zone (accept multiple .pdf files)
    Shows list of selected files with detected dates
    [Upload All] button
    Progress: "Processing file 12 of 30..."
    Result summary per file
```

**Gherkin spec for Phase 3C** (write .feature file when ready to build):

```gherkin
Feature: Batch historical PDF upload
  Scenario: SC-045 Batch upload processes multiple PDFs in date order
    Given 5 NGX PDF files for dates 2026-05-01 through 2026-05-05
    When I POST /api/v1/prices/batch-upload-pdf with all 5 files
    Then price_history records exist for all 5 dates for known tickers
    And current_price on companies reflects the most recent file (2026-05-05)
    And the response shows files_processed: 5

  Scenario: SC-046 Batch upload reports failed files without aborting
    Given 5 PDF files where file 3 is corrupt
    When I POST /api/v1/prices/batch-upload-pdf with all 5 files
    Then files 1, 2, 4, 5 are processed successfully
    And file 3 appears in failed_files with an error reason
    And files_processed: 4, files_failed: 1
```

---

## Section 6: Updated Gherkin Traceability

SC-UI-027 revised — inline row → slide-out drawer.
Add to BR001_GHERKIN_UI spec file under Holdings section.

SC-UI-027b added — drawer closes and resets on cancel/escape.

Phase 3C batch upload scenarios SC-045 and SC-046 — noted above,
write .feature file when batch endpoint is being built.

---

## Section 7: Antigravity Action List (Priority Order)

```
🔴 P0 — Fix bugs before adding features:
[ ] 1. Bug fix: useEffect to reset editingRowId when editMode turns off
[ ] 2. Bug fix: investigate and fix useDeleteHolding mutation
[ ] 3. Verify: PDF upload writes to price_history table (not just current_price)
       Add price_history insert to upload_ngx_pdf if missing

🟡 P1 — Redesign:
[ ] 4. Remove inline add-holding row from Holdings table
[ ] 5. Build AddHoldingDrawer component (spec in Section 3)
[ ] 6. Wire [+ Add Holding] button to open drawer
[ ] 7. Wire drawer Save/Publish mutations with query invalidation

🟢 P2 — Phase 3C planning (do not build yet):
[ ] 8. Note batch upload endpoint in docs/requirements/BR-002-price-entry.md
[ ] 9. Create Gherkin .feature file for SC-045 and SC-046 (spec exists above)

After completing P0 and P1:
[ ] 10. Re-run AT-003 for affected scenarios (SC-UI-027, SC-UI-028, SC-UI-029)
[ ] 11. Write HO-012 handover to Claude with updated AT-003 results
```

---

**End of HO-011**
**Next**: Antigravity completes P0 bug fixes + P1 drawer redesign → HO-012 to Claude