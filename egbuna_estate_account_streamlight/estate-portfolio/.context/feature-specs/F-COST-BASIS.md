---
id: F-COST-BASIS
title: Historical Cost Basis Upload
status: PLANNED
owner-backend: [opencode]DeepSeek Flash
owner-frontend: [opencode]Kimi
architect: [opencode]DeepSeek Pro
sprint: Phase 3C (after F-NGX-COMPANIES)
test-domain: HOLD
dependencies:
  - F-016 User Management (admin role guards)
  - F-NGX-COMPANIES (companies table must have listed companies)
  - bcrypt==4.0.1 (pinned)
---

# F-COST-BASIS — Historical Cost Basis Upload

## Goal
Admin uploads historical cost basis data (ticker, avg purchase price, quantity, purchase date) via single-entry form or bulk CSV. The system matches tickers against the companies table, auto-creates new companies when needed, and creates holdings with the correct holding_type (active or claim).

## Location
Built into the **same page** as Price Entry, which is renamed from `/settings/price-entry` to **`/admin/data-upload`**. A 301 redirect from the old path ensures backward compatibility. The cost-basis upload button is **separate** from the price upload button.

## User Story
As an admin, I want to upload historical cost basis data for my portfolio so that the system can calculate current value, unrealized gain/loss, and portfolio performance. If a company is no longer listed, I want it automatically classified as a claim.

## Backend

**Router:** `backend/app/routers/cost_basis.py` (new file)

**Endpoints:**

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/cost-basis/quick` | ADMIN, SUPERADMIN | Single-entry form: one ticker + price + quantity + date |
| POST | `/api/v1/cost-basis/bulk-csv` | ADMIN, SUPERADMIN | Bulk CSV upload with preview + commit (two-stage) |
| GET | `/api/v1/cost-basis` | ADMIN, SUPERADMIN | List all cost-basis records with status |
| GET | `/api/v1/cost-basis/download-template` | ADMIN, SUPERADMIN | Download CSV template |

**Model:** `Holding` (existing model in `backend/app/models.py`)

**No new tables needed** — reuses existing `holdings` and `claim_records` tables.

## CSV Format

```
ticker,company_name,avg_purchase_price,quantity,purchase_date
DANGCEM,Dangote Cement Plc,245.50,500,2024-01-15
GTCO,Guaranty Trust Holding Co,33.20,1000,2024-03-01
UNKNOWN,Some New Company Ltd,100.00,200,2024-06-01
```

- **ticker**: Required, uppercase
- **company_name**: Required — used for fallback matching
- **avg_purchase_price**: Required, decimal (monetary value as string in API)
- **quantity**: Required, positive integer
- **purchase_date**: Required, ISO 8601 date

## Ticker Matching Workflow (CRITICAL — from Product Owner)

```
For each row in uploaded CSV:

  STEP 1 — Match by ticker symbol
    SELECT id FROM companies WHERE UPPER(ticker) = UPPER(csv.ticker)
    IF match → use existing company_id
    IF no match → go to STEP 2

  STEP 2 — Match by company name (fuzzy, case-insensitive)
    SELECT id FROM companies WHERE LOWER(company_name) = LOWER(csv.company_name)
    IF match → use existing company_id, IGNORE csv.ticker (keep DB ticker)
    IF no match → go to STEP 3

  STEP 3 — No match anywhere → add new company
    INSERT INTO companies (ticker, company_name, status) VALUES (csv.ticker, csv.company_name, 'listed')
    Use the new company_id
```

## Holding Type Determination

After company_id is resolved:
```
IF company.status = 'listed' → holding_type = 'active'
  cost_basis = avg_purchase_price × quantity
  INSERT into holdings (company_id, num_shares, avg_purchase_price, holding_type, ...)

IF company.status = 'delisted' or 'defunct' → holding_type = 'claim'
  cost_basis_override = '0.00'
  INSERT into holdings (company_id, num_shares, avg_purchase_price, cost_basis_override, holding_type, ...)
  auto-create ClaimRecord (cost_basis_override = 0, expected_payout = '0.00')
```

## API Response Shape

**POST /api/v1/cost-basis/quick (201):**
```json
{
  "data": {
    "id": 1,
    "company_id": 42,
    "ticker": "DANGCEM",
    "company_name": "Dangote Cement Plc",
    "avg_purchase_price": "245.50",
    "quantity": 500,
    "purchase_date": "2024-01-15",
    "holding_type": "active",
    "num_shares": 500
  },
  "meta": {},
  "error": null
}
```

**POST /api/v1/cost-basis/bulk-csv (201):**
```json
{
  "data": {
    "summary": {
      "total": 50,
      "active_holdings_created": 48,
      "claims_created": 2,
      "new_companies_created": 1,
      "errors": []
    }
  },
  "meta": {},
  "error": null
}
```

## Frontend

**Route:** `/admin/data-upload` (Cost Basis tab/section)

**Components:**
- `<CostBasisQuickForm>` — single-entry form: ticker autocomplete + price + quantity + date
- `<CostBasisCsvUpload>` — CSV drop zone with preview table before commit
- `<CostBasisTemplate>` — download template link
- `<CostBasisResultSummary>` — shows counts after upload
- `<CostBasisList>` — table of all cost-basis records with holding_type badge

**Behavior:**
1. Admin navigates to `/admin/data-upload`
2. Selects "Cost Basis" tab (separate from Prices and Companies)
3. **Single entry**: Type ticker (autocomplete from companies DB), fill price/qty/date, submit
4. **Bulk**: Upload CSV → preview table shows resolved company names + holding_type badge → commit
5. After commit: summary shows "48 active holdings, 2 claims, 1 new company, 0 errors"
6. Can browse all cost-basis records in table below

## Acceptance Checklist

### [DB]
- [ ] Holdings created with correct company_id after ticker matching
- [ ] Holdings with 'listed' company → holding_type = 'active', cost_basis = price × qty
- [ ] Holdings with 'delisted' company → holding_type = 'claim', cost_basis_override = '0.00'
- [ ] ClaimRecord auto-created for delisted/defunct companies
- [ ] New company created in companies table when no ticker or name match exists

### [API]
- [ ] POST /cost-basis/quick with valid ticker → 201, holding_type = 'active'
- [ ] POST /cost-basis/quick with delisted ticker → 201, holding_type = 'claim'
- [ ] POST /cost-basis/quick with unknown ticker → 201, uses company_name fallback
- [ ] POST /cost-basis/quick with fully unknown company → 201, creates new company
- [ ] POST /cost-basis/bulk-csv → 201 with summary
- [ ] POST /cost-basis/quick without admin → 403
- [ ] POST /cost-basis/quick with invalid payload → 422
- [ ] GET /cost-basis → returns list of records
- [ ] Monetary values are strings in all responses

### [UI]
- [ ] Cost Basis section renders under `/admin/data-upload`
- [ ] Single-entry form has ticker autocomplete (populated from companies table)
- [ ] Bulk CSV upload has preview table before commit
- [ ] Template download link works
- [ ] Result summary shows correct counts
- [ ] No console errors
- [ ] Loading state visible during upload

## Page Rename

| Current Path | New Path | Action |
|--------------|----------|--------|
| `/settings/price-entry` | `/admin/data-upload` | Rename with 301 redirect |

Three sections on the renamed page:
1. **Prices** — existing price entry functionality (quick, PDF, CSV)
2. **Companies** — F-NGX-COMPANIES CSV upload
3. **Cost Basis** — F-COST-BASIS form + CSV upload

## Dependencies
- F-016 (User Management) — for `require_role(["ADMIN", "SUPERADMIN"])`
- F-NGX-COMPANIES — companies table must be populated for ticker matching
- No new Python packages needed (CSV parsing is stdlib)

## Sign-Off
- [ ] All [DB] checklist items passing
- [ ] All [API] checklist items passing
- [ ] All [UI] checklist items passing
- [ ] .context/progress-tracker.md updated to COMPLETE
- [ ] HO-XXX.md filed in docs/handovers/
- [ ] AT-XXX.md filed in docs/testing/acceptance/