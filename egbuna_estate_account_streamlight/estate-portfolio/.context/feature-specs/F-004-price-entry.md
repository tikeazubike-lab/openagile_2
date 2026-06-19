---

id: F-004

title: Price Entry

status: COMPLETE

owner-backend: Owl Alpha | Nex N2
owner-frontend: Nex N2
Review/Architect role: Deepseek

sprint: Phase 3A (complete)

---

# F-004 — Price Entry

## Goal

Admin updates NGX stock prices daily via NGX Daily Official List PDF

upload (primary) or manual quick entry (secondary). All price changes

are logged to an audit trail with revert capability.

## What Is Built

Backend (backend/app/routers/prices.py):

  GET  /api/v1/prices                        — current prices list

  POST /api/v1/prices/quick                  — single stock manual entry

  POST /api/v1/prices/bulk-csv               — bulk CSV (preview + commit)

  POST /api/v1/prices/upload-pdf             — NGX PDF upload (primary)

  GET  /api/v1/prices/audit                  — last 50 price changes

  POST /api/v1/prices/audit/{id}/revert      — revert a price change

  GET  /api/v1/prices/history/{id}           — price history for one company

Frontend:

  src/routes/_app.settings.price-entry.tsx

  src/api/queries.ts → useQuickPriceUpdate(), useUploadNGXPdf(),

                        useBulkCsvImport(), usePriceAudit(), useRevertPrice()

## NGX PDF Parser

Source: NGX Daily Official List PDF from https://ngxgroup.com/exchange/data/data-library/

URL pattern: https://doclib.ngxgroup.com/DownloadsContent/DAILY%20SUMMARY%20FOR%20{DD-MM-YYYY}.pdf

Parser strategy (right-to-left column extraction):

  Company names have variable word count → left-to-right indexing fails

  Numeric columns at end are strictly formatted → negative indexing is robust

  Dual format: Daily Official List (10-14 cols) + Gainers & Losers (6 cols)

  Fallback: fuzzy company name matching when ticker not found in PDF

PDF upload writes to TWO places:

  1. price_history table (recorded_date from PDF filename, not today)

  2. companies.current_price (updated to latest value)

Date extraction from filename:

  "DAILY SUMMARY FOR 17-05-2026.pdf" → 2026-05-17

  Fallback to today if no recognisable date pattern found

## CSV Format (LOCKED)

Columns: ticker,price,date (exact lowercase headers, no extra columns)

Example:

  ticker,price,date

  DANGCEM,450.00,2026-05-18

  ZENITHBANK,32.50,2026-05-18

Source recorded server-side as 'csv_upload' — not in the file.

Two-stage: POST with commit=false (preview) → POST with commit=true (apply).

Partial commit: valid rows apply even if some rows have errors.

## Price Audit

Every price update writes to price_audit BEFORE updating companies.current_price:

  old_price, new_price, changed_at (date from PDF), source, changed_by

Source values:

  'manual'        — quick entry

  'ngx_pdf_upload'— PDF upload

  'csv_upload'    — CSV import

  'revert_of_N'   — revert (N = original audit_id)

Revert: creates a new audit record — never deletes or modifies existing records

## Page Layout

Left panel (55%):

  Quick Price Update form:

    Company searchable dropdown, New Price input (DM Mono), Date picker

    [Update Price] button (lavender)

    Success toast: "DANGCEM updated ₦420.00 → ₦450.00 (+7.14%)"

  Recent Price Changes audit log (last 20):

    | Date | Ticker | Old | New | Δ% | Source | [Revert] |

    Revert → confirmation dialog → fires revert endpoint

Right panel (45%):

  Primary: Upload NGX PDF

    Drop zone (.pdf only, 20MB max)

    [Upload & Parse PDF] button

    Result: "142 prices updated · 8 tickers not in database [Show ▼]"

  Secondary: Manual CSV Upload

    [Download CSV Template] (uses real tickers from useCompanies())

    Drop zone (.csv only)

    Preview table (valid rows + error rows with reasons)

    [Commit N rows →] button

## Acceptance Checklist

### [DB]

- [ ] After PDF upload, price_history has records with correct date from filename

- [ ] After quick entry, price_audit has old_price and new_price

- [ ] After revert, companies.current_price matches old_price from audit

- [ ] source field correctly set for each update type

### [API]

- [ ] POST /api/v1/prices/quick with valid payload → 200

- [ ] POST /api/v1/prices/quick with future date → 422

- [ ] POST /api/v1/prices/quick with price > 100000 → 422 (sanity cap)

- [ ] POST /api/v1/prices/quick with negative price → 422

- [ ] POST /api/v1/prices/upload-pdf → 200, updated count in response

- [ ] POST /api/v1/prices/bulk-csv?commit=false → preview (no DB change)

- [ ] POST /api/v1/prices/bulk-csv?commit=true → prices updated

- [ ] POST /api/v1/prices/audit/{id}/revert → price restored

- [ ] GET /api/v1/prices/audit → last 50 entries with source badges

### [UI]

- [ ] Page loads at /settings/price-entry without crash

- [ ] Readonly user is redirected away (admin only)

- [ ] Company dropdown is searchable (typeahead)

- [ ] Valid quick entry → toast with old price, new price, delta%

- [ ] Dashboard and Holdings update after price change (query invalidation)

- [ ] PDF drop zone accepts .pdf, rejects .xlsx and .exe

- [ ] Client-side 20MB size guard — error appears before upload

- [ ] Audit log shows last 20 entries with source badges

- [ ] Revert button → confirmation → price reverts → audit log updates

- [ ] Revert button disabled when old_price is null


