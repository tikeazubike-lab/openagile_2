---
id: F-NGX-COMPANIES
title: NGX Listed Companies PDF Upload
status: PLANNED
owner-backend: [opencode]DeepSeek Flash
owner-frontend: [opencode]Kimi
architect: [opencode]DeepSeek Pro
sprint: Phase 3C (URGENT — blocks F-COST-BASIS)
test-domain: COMP
dependencies:
  - F-016 User Management (admin role guards)
  - bcrypt==4.0.1 (pinned)
---

# F-NGX-COMPANIES — NGX Listed Companies PDF Upload

## Goal
Admin uploads a PDF file (NGX Daily Official List) containing currently listed NGX companies with their ticker symbols, company names, and sectors. The system parses the PDF, extracts company data, and populates the `companies` table so that the cost-basis feature (F-COST-BASIS) can reference existing companies and validate tickers.

## Data Source
The official NGX Daily Official List is published as a **PDF**. This is the same PDF format already handled by the existing Price Entry feature (`backend/app/routers/prices.py` using `pdfplumber`). The companies list feature reuses the same PDF parsing infrastructure.

## User Story
As an admin, I want to upload the latest NGX Daily Official List PDF to update the companies database with currently listed equities, so that I can later attach cost-basis data and the system knows which companies are active vs delisted.

## Backend

**Router:** `backend/app/routers/companies.py` (extend existing router — currently minimal, ~30 lines)

**Endpoints:**

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/companies/upload-pdf` | ADMIN, SUPERADMIN | Upload NGX Daily Official List PDF. Full rollback on error. |
| GET | `/api/v1/companies` | Any authenticated | List companies with filters: `?status=listed` and `?search=<name\|ticker>` |
| GET | `/api/v1/companies/download-template` | ADMIN, SUPERADMIN | Download CSV template for manual overrides |

**Model:** `Company` (existing model in `backend/app/models.py`)

**Migration:**
```sql
-- Add status column to companies table if not exists
ALTER TABLE companies ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'listed';
-- Add index for status + search
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_companies_name_lower ON companies(LOWER(company_name));

-- Add ticker column if not exists (may be named differently in current schema)
ALTER TABLE companies ADD COLUMN IF NOT EXISTS ticker VARCHAR(20) UNIQUE;
```

**PDF Parsing:**
- Reuse existing `pdfplumber` (already in `requirements.txt` via Price Entry)
- Parse the NGX Daily Official List PDF format (same format as prices.py already handles)
- Extract per-company: ticker symbol, company name, sector
- Pattern reference: `backend/app/services/pdf_parser.py` or inline in `prices.py` — extend with company extraction logic

## Processing Logic

| Condition | Action |
|-----------|--------|
| ticker EXISTS in DB companies table | UPDATE company_name and sector (companies change names over time) |
| ticker NOT in DB | INSERT new row as `status = 'listed'` |
| PDF parse fails (malformed) | Return 422 with specific error, full rollback |
| New companies found | Add them; old companies NOT in new PDF are NOT auto-delisted (admin reviews manually) |

**Response (201):**
```json
{
  "data": {
    "summary": {
      "total": 155,
      "inserted": 5,
      "updated": 150,
      "errors": []
    }
  },
  "meta": {},
  "error": null
}
```

**Error response (422):**
```json
{
  "data": null,
  "meta": {},
  "error": {
    "code": "PDF_PARSE_ERROR",
    "message": "Could not parse PDF at row 12: missing ticker field."
  }
}
```

## Frontend

**Route:** `/admin/data-upload` (renamed price-entry page, Companies section)

**Components:**
- `<CompanyPdfUpload>` — file drop zone + upload button (reuses same pattern as existing price PDF upload)
- `<UploadResultSummary>` — shows inserted/updated counts after upload
- `<CompanyList>` — table of uploaded companies with search + status filter

**Behavior:**
1. Admin navigates to `/admin/data-upload`
2. Selects "Companies" tab/section
3. Uploads NGX Daily Official List PDF via drag-drop or file picker
4. Sees result summary: "5 new companies, 150 updated, 0 errors"
5. Can browse all registered companies via searchable table

## Acceptance Checklist

### [DB]
- [ ] companies table has `ticker` (unique) and `status` columns
- [ ] Companies parsed from PDF exist in DB with correct ticker, name, sector
- [ ] Existing companies updated (not duplicated) on re-upload of same PDF
- [ ] Full rollback on malformed PDF (no partial inserts)

### [API]
- [ ] POST /companies/upload-pdf with valid PDF → 201 with summary
- [ ] POST with malformed PDF → 422, full rollback
- [ ] POST without admin → 403
- [ ] GET /companies?status=listed → returns only listed companies
- [ ] GET /companies?search=zenith → returns matching rows (case-insensitive)
- [ ] GET /companies -> returns all companies with pagination

### [UI]
- [ ] Upload section renders under `/admin/data-upload` in Companies tab
- [ ] Drag-drop zone accepts .pdf files
- [ ] Result summary shows inserted/updated/errors
- [ ] Company list renders with search and status filter
- [ ] No console errors
- [ ] Loading state visible during upload

## Dependencies
- F-016 (User Management) — for `require_role(["ADMIN", "SUPERADMIN"])`
- `pdfplumber` — already in requirements.txt (used by Price Entry PDF parser)
- Existing `companies.py` router to extend

## Sign-Off
- [ ] All [DB] checklist items passing
- [ ] All [API] checklist items passing
- [ ] All [UI] checklist items passing
- [ ] .context/progress-tracker.md updated to COMPLETE
- [ ] HO-XXX.md filed in docs/handovers/
- [ ] AT-XXX.md filed in docs/testing/acceptance/