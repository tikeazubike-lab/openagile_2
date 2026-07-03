# BUG-AT-002 — Acceptance Test: F-COST-BASIS (Historical Cost Basis Upload)

## Related Spec
`.context/feature-specs/F-COST-BASIS.md`

---

### 1. Quick Entry — POST /api/v1/cost-basis/quick

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 1.1 | Submit with valid ticker that exists in companies | 201, holding_type="active", holding created | | |
| 1.2 | Submit with ticker of delisted company | 201, holding_type="claim", ClaimRecord auto-created | | |
| 1.3 | Submit with unknown ticker + company_name | 201, new company created in companies table, holding_type="active" | | |
| 1.4 | Submit with unknown ticker + empty company_name | 201, company created with ticker as name | | |
| 1.5 | Submit with negative price | 422 error | | |
| 1.6 | Submit with zero quantity | 422 error | | |
| 1.7 | Submit without auth | 401 | | |
| 1.8 | Submit as readonly user | 403 | | |
| 1.9 | Verify holding appears in GET /cost-basis | Row exists with ticker, price, quantity, type | | |

### 2. Bulk CSV — POST /api/v1/cost-basis/bulk-csv

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 2.1 | Upload valid CSV with commit=false | 201, preview rows returned, committed=false | | |
| 2.2 | Preview shows holding_type correctly | active vs claim badges match company status | | |
| 2.3 | Commit valid CSV (commit=true) | 201, summary counts match input | | |
| 2.4 | CSV with mixed valid + invalid rows | preview shows both valid and error rows | | |
| 2.5 | CSV with missing required columns | 422 error listing missing columns | | |
| 2.6 | Empty CSV file | 422 error | | |
| 2.7 | CSV with unknown ticker + known company_name | Falls back to name match (Step 2) | | |
| 2.8 | CSV with fully unknown company | Creates new company (Step 3) | | |
| 2.9 | Commit without auth | 401 | | |
| 2.10 | Commit as readonly | 403 | | |
| 2.11 | Verify committed holdings appear in GET /cost-basis | Rows exist with correct data | | |

### 3. List Records — GET /api/v1/cost-basis

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 3.1 | List all cost-basis records | 200, array with id, ticker, price, quantity, holding_type | | |
| 3.2 | Hit without auth | 401 | | |

### 4. Download Template — GET /api/v1/cost-basis/download-template

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 4.1 | Download template | 200, CSV with headers: ticker,company_name,avg_purchase_price,quantity,purchase_date | | |
| 4.2 | Hit without auth | 401 | | |

### 5. Frontend — /settings/data-upload (Cost Basis Tab)

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 5.1 | Cost Basis tab renders | Quick form + CSV upload + records list | | |
| 5.2 | Quick form: type ticker, see company name + holding_type preview | Autocomplete shows matching companies | | |
| 5.3 | Quick form: submit valid data | Success toast, record appears in table below | | |
| 5.4 | Quick form: submit invalid data | Error toast | | |
| 5.5 | CSV: upload file → preview step | Valid/error rows displayed | | |
| 5.6 | CSV: preview shows holding_type badges | "active" green, "claim" yellow | | |
| 5.7 | CSV: commit from preview | Summary screen with counts, records appear in table | | |
| 5.8 | CSV: download template | CSV file downloads with correct headers | | |
| 5.9 | Records table renders | Shows ticker, price, quantity, total_cost, type | | |

---

### 6. DB Integrity Checks

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 6.1 | holdings table has purchase_date column | Column exists, nullable date | | |
| 6.2 | ClaimRecord auto-created for delisted holdings | claim_records table has row linked via holding_id | | |
| 6.3 | New companies created by cost-basis have status="listed" | companies table shows ticker with "listed" | | |
| 6.4 | Migration head is 7d4e8f2a1c03 | `alembic current` returns 7d4e8f2a1c03 | | |

---

**Business Requirement:** Admin must upload historical cost basis data (ticker, price, quantity, purchase date) so the system can calculate current value, unrealized gain/loss, and portfolio performance. Delisted companies auto-classify as claims.
