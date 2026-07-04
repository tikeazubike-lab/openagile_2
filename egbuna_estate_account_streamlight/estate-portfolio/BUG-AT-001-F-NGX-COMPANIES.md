# BUG-AT-001 — Acceptance Test: F-NGX-COMPANIES (NGX Listed Companies PDF Upload)

## Related Spec
`.context/feature-specs/F-NGX-COMPANIES.md`

---

### 1. PDF Upload — POST /api/v1/companies/upload-pdf

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 1.1 | Upload valid NGX Daily Official List PDF | 201, summary shows inserted/updated/total | | |
| 1.2 | Upload same PDF twice | 201, second run shows 0 inserted, N updated (upsert) | | |
| 1.3 | Upload empty PDF | 422 error | | |
| 1.4 | Upload non-PDF file (.txt) | 422 error | | |
| 1.5 | Hit endpoint without auth cookie | 401 | | |
| 1.6 | Hit endpoint as readonly user | 403 | | |
| 1.7 | Verify inserted companies appear in GET /companies | Row exists with ticker, name, sector, status="listed" | | |
| 1.8 | Verify updated company name/sector reflects changes | Old data overwritten | | |

### 2. List Companies — GET /api/v1/companies

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 2.1 | List all companies | 200, array with meta.total | | |
| 2.2 | Filter by `?status=listed` | Only listed companies returned | | |
| 2.3 | Search by ticker `?search=zenith` | Case-insensitive match | | |
| 2.4 | Search by name `?search=dangote` | Case-insensitive match | | |
| 2.5 | Hit without auth | 401 | | |

### 3. Download Template — GET /api/v1/companies/download-template

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 3.1 | Download template | 200, Content-Type: text/csv, filename includes "companies_template" | | |
| 3.2 | Hit without auth | 401 | | |

### 4. Frontend — /settings/data-upload (Companies Tab)

| # | Test | Expected | Actual | Pass? |
|---|------|----------|--------|-------|
| 4.1 | Navigate to /settings/data-upload | Page loads with Companies and Cost Basis tabs | | |
| 4.2 | PDF dropzone renders | Drag-and-drop area visible, accepts .pdf | | |
| 4.3 | Upload PDF via file picker | Loading state, then summary card appears | | |
| 4.4 | Upload summary shows correct inserted/updated | Counts match actual DB changes | | |
| 4.5 | Company list table renders | Shows ticker, name, sector, status columns | | |
| 4.6 | Search filters company list | Typing in search narrows results | | |
| 4.7 | Status dropdown filters | Selecting "listed" shows only listed | | |
| 4.8 | Reject non-PDF file | Toast error "Only .pdf files accepted" | | |

---

**Business Requirement:** Admin must be able to upload NGX Daily Official List PDF to populate companies database so cost-basis feature can reference existing companies and validate tickers.
