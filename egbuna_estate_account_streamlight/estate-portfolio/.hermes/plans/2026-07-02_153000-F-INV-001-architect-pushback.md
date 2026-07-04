# Spec Correction: F-INV-001 — Architect Push-Back

> **From:** Hermes (Workflow Governance)  
> **To:** [opencode]DeepSeek Pro (Architecture Lead)  
> **Date:** 2026-07-02  
> **Reference:** `BUG-TRIAGE-001-test-run-2026-07-03.md` §"New Feature Spec Required"  
> **Status:** CORRECTION — F-INV-001 as written is incorrect. Two separate features required.

---

## Why F-INV-001 Is Wrong As Spec'd

Claude's triage spec'd F-INV-001 as a single one-off task:

> "Admin uploads a CSV (or uses a simple form) containing: ticker | avg_purchase_price | total_shares | purchase_date"

This conflates two independent domains:

| What Claude Combined | What's Actually Required |
|----------------------|--------------------------|
| Uploading current NGX listed companies | **Separate feature** — companies list comes from a different source and has different purpose |
| Uploading historical cost basis | **Separate feature** — references the companies list, auto-filters delisted |

The companies list must exist **first** so that cost-basis upload can:
- Validate tickers against currently listed companies
- Auto-identify delisted/defunct tickers → route to claims
- Match by name when ticker doesn't exist

---

## Feature 1: F-NGX-COMPANIES — Upload Current NGX Listed Companies

### Source
Companies list comes from a **PDF upload** (likely the NGX Daily Official List or a dedicated ETF companies PDF). Not a CSV.

### Purpose
Populate/maintain the `companies` table with currently listed NGX equities. Excludes delisted/defunct companies (those go to claims).

### Workflow (admin only)
```
1. Admin uploads PDF (companies list)
2. Backend parses PDF → extracts ticker + company_name + sector
3. New tickers: INSERT into companies table
4. Existing tickers: UPDATE sector/name if changed
5. Missing tickers (delisted from PDF): Flagged for review, moved to claims
6. Return summary: { added: N, updated: N, delisted: N }
```

### Output (what the cost-basis feature consumes)
A clean `companies` table with:
- `ticker` (unique, upper case)
- `company_name`
- `sector`
- `status` = `'listed'`

---

## Feature 2: F-COST-BASIS — Upload Historical Cost Basis

### Location
Built into the **existing Price Entry page** — but the page needs renaming to something like `/admin/data-upload` or `/settings/data-upload`. The cost-basis upload button is **separate** from the price upload button, but lives on the same page.

### Form UI Pattern
Same pattern as the existing Quick Price Entry form:
- **Ticker**: Autocomplete dropdown (populated from `companies` table — Feature 1)
- **Company Name**: Displayed after ticker selection
- **Avg Purchase Price**: Numeric input (₦)
- **Quantity**: Numeric input (shares)
- **Purchase Date**: Date picker
- **Bulk option**: CSV upload with columns: `ticker, company_name, avg_purchase_price, quantity, purchase_date`

### Ticker Matching Rule (critical — from Product Owner)

```
For each row in the uploaded CSV:

  STEP 1 — Match by ticker symbol
    IF ticker EXISTS in companies table → use existing company_id
    IF ticker does NOT exist → go to STEP 2

  STEP 2 — Match by company name
    IF company_name from CSV matches a company in the DB
      (fuzzy match: case-insensitive, strip whitespace)
      → use the existing company_id (ignore the CSV ticker, keep DB ticker)
    IF no match → go to STEP 3

  STEP 3 — Add new company
    INSERT the company_name + ticker into companies table as a new entry
    → use the new company_id

  STEP 4 — Determine holding type
    IF company.status = 'listed' → holding_type = 'active'
    IF company.status = 'delisted' or not in main list → holding_type = 'claim'
      (cost_basis_override = 0, payout tracked via ClaimRecord)
```

### Claim Handling
When a ticker maps to a delisted/defunct company:
- Auto-create a **ClaimRecord** with `cost_basis_override = 0`
- Do NOT block the upload — claims are expected for legacy Nigerian portfolios
- Flag in the upload summary: "N claim(s) auto-created for delisted tickers"

---

## Dependency Graph

```
F-NGX-COMPANIES (PDF upload)
    ↓                         
F-COST-BASIS (form/CSV)     ← step 1 reads from companies table
    ↓
HOLD-VIEW-BE-E2E-001        ← unblocked (cost basis exists)
PRIC-UPDATE-BE-E2E-001      ← unblocked (price → value chain works)
```

---

## Updated Priority Sequence

```
1. HO-026 (confirm HO-024 complete)
2. AT-004 (14/14 pass)
3. F-016 (User Management)                    ← defines admin role
4. F-NGX-COMPANIES (PDF companies list)       ← URGENT, blocks cost-basis
5. F-COST-BASIS (form/CSV upload)             ← unblocks E2E tests
6. Rename price-entry page to /admin/data-upload (or similar)
7. Re-run HOLD-VIEW-BE-E2E-001 and PRIC-UPDATE-BE-E2E-001
8. BUG-DASH-NOTIFY-001 (bell fix)
9. F-007 (NAV History)
```

---

## Open Questions (need architect + PO resolution)

| # | Question | Recommended Answer | Owner |
|---|----------|-------------------|-------|
| 1 | PDF source for companies list? | NGX Daily Official List PDF (same format as price upload) | Product Owner |
| 2 | Rename price-entry page to what? | `/admin/data-upload` with sections: Prices, Companies, Cost Basis | Product Owner |
| 3 | Cost basis CSV: include company_name? | Yes — required for no-ticker-match fallback | Product Owner |
| 4 | Auto-create claims or flag for review? | Auto-create with summary report; admin can adjust | Architect |
| 5 | PDF parser: reuse existing pdfplumber? | Yes — same NGX PDF format already handled by `prices.py` | Architect |

---

## Request

DeepSeek Pro (Architect): Please rewrite the F-INV-001 spec as **two separate specs**:
- **F-NGX-COMPANIES** — PDF companies list upload
- **F-COST-BASIS** — Admin form/CSV for historical cost basis

Incorporate the ticker matching workflow and claim auto-creation logic above.

---

*Push-back prepared by Hermes (Workflow Governance) per `Master_context_Claude_web_2.txt`.*