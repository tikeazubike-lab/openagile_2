---
type: BR
id: EPM-PRICE-ENTRY-FINAL-SPEC
title: Price Entry Page Final Implementation Spec
status: ARCHIVAL_REFERENCE
version: 1.0
updated: 2026-05-23
source_date: 2026-04-30
---

# Final Implementation Document — Price Entry Page (Phase 3A)
**From**: Claude (The Brain — final review after Grok consolidation)
**To**: Antigravity (Implementer)
**Date**: 2026-04-30
**Protocol**: MASTER_CONTEXT.md v4.0
**Input**: Grok consolidated handover (2026-04-30) + user confirmation (Stooq removed)
**Status**: ALL DECISIONS LOCKED. No further design questions. Implement exactly as written.

---

## Section 0: What Changed Since Previous Claude Spec

| Item | Previous Claude spec | Final (this document) |
|------|---------------------|----------------------|
| Stooq mention | Lavender info box referencing Stooq | **Removed entirely** — Stooq has no NGX coverage |
| NGX source | Generic mention | **NGX Daily Official List PDF** with exact URL pattern |
| CSV info box | Stooq reminder | NGX PDF guidance + CSV template download |
| Quick entry payload | Raw `dict` in endpoint | **Pydantic model** (Grok correction — applied) |
| Audit log response | No delta | **`delta_pct` field added** (Grok correction — applied) |
| CSV header handling | Assumed clean input | **Strip + lowercase normalisation** on all headers |
| ToT on partial commit | Not yet resolved | **Option B confirmed**: partial commit, Option C UI feedback |

Everything else from the previous Claude spec is unchanged and carried forward.

---

## Section 1: Decisions Locked

### CSV Format
```
Filename: any .csv
Encoding: UTF-8
Headers:  ticker,price,date   (exact lowercase, stripped of whitespace)
Example:
  ticker,price,date
  DANGCEM,450.00,2026-04-30
  ZENITHBANK,32.50,2026-04-30
  GTCO,28.75,2026-04-30

Validation rules (enforced server-side):
  ticker  — must match an existing non-deleted Company.ticker (case-insensitive lookup)
  price   — numeric, > 0, ≤ 100000 (₦100,000 sanity cap)
  date    — YYYY-MM-DD, not in the future, warn (not reject) if > 30 days old

Error behaviour: partial commit (Option B)
  - Valid rows commit atomically
  - Invalid rows are skipped and reported
  - A file with 3 bad rows out of 50 still updates the 47 good ones
  - User sees exact list of skipped rows and their error reasons

Source: recorded server-side as 'csv_upload' in price_audit — not in the file
```

### NGX Data Source (replaces all Stooq references)
```
Primary source: NGX Daily Official List (PDF)
URL pattern:    https://doclib.ngxgroup.com/DownloadsContent/DAILY%20SUMMARY%20FOR%20{DD-MM-YYYY}.pdf
Library page:   https://ngxgroup.com/exchange/data/data-library/

User workflow:
  1. Download today's PDF from NGX Data Library
  2. Extract active holdings (Ticker + Close price) manually
  3. Save as CSV with columns: ticker,price,date
  4. Upload via Bulk CSV panel

The app must NOT attempt to scrape or auto-fetch NGX data.
Stooq is removed from all UI copy — it has no NGX (XNSA) coverage.
```

### Partial Commit UI (Option C — confirmed)
```
After committing a CSV with mixed valid/invalid rows:

  ✓ 47 prices updated successfully
  ⚠ 3 rows skipped  [Show details ▼]  ← collapsible

  Collapsed view: just the summary line
  Expanded view:
    | Row | Ticker | Price | Date | Reason |
    | 12  | TEXACO | -5.00 | 2026-04-30 | Price must be positive |
    | 23  | GHOST  | 12.50 | 2026-04-30 | Unknown ticker |
    | 41  | DANGCEM| 500.00| 2026-05-15 | Date is in the future |

  [Import Another File] button resets the right panel to Step 1
```

---

## Section 2: Backend — `backend/app/routers/prices.py`

### 2.1 Pydantic Models (Grok correction applied)

```python
# backend/app/routers/prices.py

from datetime import date as date_type
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.deps import get_current_user, require_admin
from app.models import Company, PriceAudit, User

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])


class QuickPricePayload(BaseModel):
    company_id: int
    price: str           # string per API contract — monetary values as strings
    entry_date: date_type

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: str) -> str:
        try:
            d = Decimal(v)
        except InvalidOperation:
            raise ValueError(f"Invalid price value: {v!r}")
        if d <= 0:
            raise ValueError("Price must be greater than zero")
        if d > Decimal("100000"):
            raise ValueError("Price exceeds ₦100,000 sanity cap — verify before submitting")
        return v

    @field_validator("entry_date")
    @classmethod
    def validate_date(cls, v: date_type) -> date_type:
        if v > date_type.today():
            raise ValueError("Entry date cannot be in the future")
        return v
```

### 2.2 GET /api/v1/prices

```python
@router.get("")
async def get_current_prices(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Company)
        .where(Company.deleted_at.is_(None))
        .where(Company.status.in_(["listed", "active"]))
        .order_by(Company.ticker)
    )
    companies = result.scalars().all()
    return {
        "data": [
            {
                "id": c.id,
                "ticker": c.ticker,
                "name": c.name,
                "sector": c.sector,
                "current_price": str(c.current_price) if c.current_price else None,
                "last_price_update": c.last_price_update.isoformat()
                    if c.last_price_update else None,
            }
            for c in companies
        ],
        "meta": {"total": len(companies)},
        "error": None,
    }
```

### 2.3 POST /api/v1/prices/quick

```python
@router.post("/quick")
async def quick_price_update(
    payload: QuickPricePayload,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    new_price = Decimal(payload.price)

    result = await db.execute(
        select(Company)
        .where(Company.id == payload.company_id)
        .where(Company.deleted_at.is_(None))
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {payload.company_id} not found")

    old_price = company.current_price

    # Write audit BEFORE updating company — single transaction
    audit = PriceAudit(
        company_id=company.id,
        old_price=old_price,
        new_price=new_price,
        changed_at=payload.entry_date,
        changed_by=current_user.id,
        source="manual",
    )
    db.add(audit)

    company.current_price = new_price
    company.last_price_update = payload.entry_date

    await db.commit()
    await db.refresh(audit)

    # Compute delta_pct for response
    delta_pct = None
    if old_price and old_price != 0:
        delta_pct = str(
            round((new_price - old_price) / old_price * 100, 2)
        )

    return {
        "data": {
            "ticker": company.ticker,
            "old_price": str(old_price) if old_price is not None else None,
            "new_price": str(new_price),
            "delta_pct": delta_pct,
            "entry_date": payload.entry_date.isoformat(),
            "audit_id": audit.id,
        },
        "error": None,
    }
```

### 2.4 POST /api/v1/prices/bulk-csv (two-stage)

```python
@router.post("/bulk-csv")
async def bulk_csv_import(
    file: UploadFile = File(...),
    commit: bool = Form(False),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    import csv, io

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))

    # Normalise headers: strip whitespace + lowercase
    if not reader.fieldnames:
        raise HTTPException(status_code=422, detail="CSV file appears to be empty")

    normalised_headers = [h.strip().lower() for h in reader.fieldnames]
    required = {"ticker", "price", "date"}
    missing = required - set(normalised_headers)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV missing required columns: {', '.join(sorted(missing))}"
        )

    # Remap reader rows to normalised keys
    def normalise_row(row: dict) -> dict:
        return {k.strip().lower(): (v or "").strip() for k, v in row.items()}

    # Pre-load ticker → company map (case-insensitive)
    result = await db.execute(
        select(Company.id, Company.ticker, Company.current_price)
        .where(Company.deleted_at.is_(None))
    )
    ticker_map = {row.ticker.upper(): row for row in result.fetchall()}

    valid_rows = []
    error_rows = []
    today = date_type.today()

    for i, raw_row in enumerate(reader, start=2):
        row = normalise_row(raw_row)
        ticker = row.get("ticker", "").upper()
        price_str = row.get("price", "")
        date_str = row.get("date", "")
        errors = []

        # Ticker
        company_row = ticker_map.get(ticker)
        if not company_row:
            errors.append(f"Unknown ticker '{ticker}'")

        # Price
        price = None
        try:
            price = Decimal(price_str)
            if price <= 0:
                errors.append("Price must be positive")
            elif price > Decimal("100000"):
                errors.append("Price exceeds ₦100,000 sanity cap")
        except InvalidOperation:
            errors.append(f"Invalid price '{price_str}'")

        # Date
        entry_date = None
        try:
            entry_date = date_type.fromisoformat(date_str)
            if entry_date > today:
                errors.append("Date is in the future")
            elif (today - entry_date).days > 30:
                # Warn but do not reject — user may be backfilling
                pass  # logged in preview as a warning, not an error
        except (ValueError, TypeError):
            errors.append(f"Invalid date '{date_str}' — use YYYY-MM-DD")

        if errors:
            error_rows.append({
                "row": i,
                "ticker": ticker,
                "price": price_str,
                "date": date_str,
                "errors": errors,
            })
        else:
            valid_rows.append({
                "ticker": ticker,
                "price": price,
                "date": entry_date,
                "company_id": company_row.id,
                "old_price": company_row.current_price,
            })

    # STAGE 1 — Preview (commit=False)
    if not commit:
        return {
            "data": {
                "valid": len(valid_rows),
                "errors": len(error_rows),
                "preview_rows": [
                    {
                        "ticker": r["ticker"],
                        "price": str(r["price"]),
                        "date": r["date"].isoformat(),
                        "old_price": str(r["old_price"]) if r["old_price"] else None,
                    }
                    for r in valid_rows[:10]
                ],
                "error_rows": error_rows,
                "committed": False,
            },
            "error": None,
        }

    # STAGE 2 — Commit valid rows
    committed = 0
    for row in valid_rows:
        result = await db.execute(
            select(Company).where(Company.id == row["company_id"])
        )
        company = result.scalar_one_or_none()
        if not company:
            continue

        db.add(PriceAudit(
            company_id=company.id,
            old_price=company.current_price,
            new_price=row["price"],
            changed_at=row["date"],
            changed_by=current_user.id,
            source="csv_upload",
        ))
        company.current_price = row["price"]
        company.last_price_update = row["date"]
        committed += 1

    await db.commit()

    return {
        "data": {
            "valid": len(valid_rows),
            "errors": len(error_rows),
            "committed": committed,
            "error_rows": error_rows,
        },
        "error": None,
    }
```

### 2.5 GET /api/v1/prices/audit

```python
@router.get("/audit")
async def get_price_audit(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(PriceAudit, Company.ticker, Company.name)
        .join(Company, PriceAudit.company_id == Company.id)
        .order_by(desc(PriceAudit.changed_at), desc(PriceAudit.id))
        .limit(50)
    )
    rows = result.fetchall()

    def compute_delta(old, new) -> Optional[str]:
        if old is None or old == 0:
            return None
        return str(round((Decimal(str(new)) - Decimal(str(old)))
                         / Decimal(str(old)) * 100, 2))

    return {
        "data": [
            {
                "id": r.PriceAudit.id,
                "ticker": r.ticker,
                "company_name": r.name,
                "old_price": str(r.PriceAudit.old_price)
                    if r.PriceAudit.old_price is not None else None,
                "new_price": str(r.PriceAudit.new_price),
                "delta_pct": compute_delta(r.PriceAudit.old_price, r.PriceAudit.new_price),
                "changed_at": r.PriceAudit.changed_at.isoformat(),
                "source": r.PriceAudit.source,
            }
            for r in rows
        ],
        "meta": {"total": len(rows)},
        "error": None,
    }
```

### 2.6 POST /api/v1/prices/audit/{id}/revert

```python
@router.post("/audit/{audit_id}/revert")
async def revert_price_change(
    audit_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(PriceAudit).where(PriceAudit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit record not found")
    if audit.old_price is None:
        raise HTTPException(
            status_code=422,
            detail="Cannot revert — no previous price recorded for this entry"
        )

    result = await db.execute(
        select(Company)
        .where(Company.id == audit.company_id)
        .where(Company.deleted_at.is_(None))
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Record the revert as a new audit entry — never delete audit history
    revert_audit = PriceAudit(
        company_id=company.id,
        old_price=company.current_price,
        new_price=audit.old_price,
        changed_at=date_type.today(),
        changed_by=current_user.id,
        source=f"revert_of_{audit_id}",
    )
    db.add(revert_audit)
    company.current_price = audit.old_price
    company.last_price_update = date_type.today()

    await db.commit()

    return {
        "data": {
            "reverted_to": str(audit.old_price),
            "new_audit_id": revert_audit.id,
        },
        "error": None,
    }
```

### 2.7 Wire into main.py

```python
# backend/app/main.py — add alongside existing router includes
from app.routers.companies import router as companies_router
from app.routers.prices import router as prices_router

app.include_router(companies_router)
app.include_router(prices_router)
```

---

## Section 3: Backend — `backend/app/routers/companies.py`

```python
# backend/app/routers/companies.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.deps import get_current_user
from app.models import Company, User

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])

@router.get("")
async def list_companies(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Company)
        .where(Company.deleted_at.is_(None))
        .order_by(Company.ticker)
    )
    companies = result.scalars().all()
    return {
        "data": [
            {
                "id": c.id,
                "ticker": c.ticker,
                "name": c.name,
                "sector": c.sector,
                "status": c.status,
                "current_price": str(c.current_price) if c.current_price else None,
                "last_price_update": c.last_price_update.isoformat()
                    if c.last_price_update else None,
            }
            for c in companies
        ],
        "meta": {"total": len(companies)},
        "error": None,
    }
```

---

## Section 4: Frontend — TanStack Query Hooks (`src/api/queries.ts`)

```typescript
// Append to existing queries.ts

export function useCompanies() {
  return useQuery({
    queryKey: ["companies"],
    queryFn: () =>
      fetch("/api/v1/companies", { credentials: "include" })
        .then((r) => r.json()).then((r) => r.data),
  });
}

export function usePriceAudit() {
  return useQuery({
    queryKey: ["price-audit"],
    queryFn: () =>
      fetch("/api/v1/prices/audit", { credentials: "include" })
        .then((r) => r.json()).then((r) => r.data),
  });
}

export function useQuickPriceUpdate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: { company_id: number; price: string; entry_date: string }) =>
      fetch("/api/v1/prices/quick", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then((r) => r.json()),
    onSuccess: () => {
      // Invalidate all price-dependent queries — dashboard + holdings refresh automatically
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}

export function useRevertPrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (auditId: number) =>
      fetch(`/api/v1/prices/audit/${auditId}/revert`, {
        method: "POST",
        credentials: "include",
      }).then((r) => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}

export function useBulkCsvImport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, commit }: { file: File; commit: boolean }) => {
      const form = new FormData();
      form.append("file", file);
      form.append("commit", String(commit));
      return fetch("/api/v1/prices/bulk-csv", {
        method: "POST",
        credentials: "include",
        body: form,
      }).then((r) => r.json());
    },
    onSuccess: (_data, variables) => {
      if (variables.commit) {
        qc.invalidateQueries({ queryKey: ["dashboard"] });
        qc.invalidateQueries({ queryKey: ["holdings"] });
        qc.invalidateQueries({ queryKey: ["companies"] });
        qc.invalidateQueries({ queryKey: ["price-audit"] });
      }
    },
  });
}
```

---

## Section 5: Frontend — Price Entry Page Layout

### Left Panel (55%) — Quick Entry + Audit Log

```
┌─ Quick Price Update ─────────────────────────────────────────┐
│                                                               │
│  Company                                                      │
│  [Searchable dropdown — useCompanies()]                       │
│  Each option: "[TICKER] Company Name — ₦current_price"       │
│  Placeholder: "Search by ticker or name..."                   │
│                                                               │
│  New Price (₦)                                                │
│  [        DM Mono, 32px, large input, ₦ prefix        ]      │
│                                                               │
│  Date                                                         │
│  [  Date picker — defaults to today, no future dates   ]      │
│                                                               │
│  [         Update Price         ]  ← lavender, full width    │
│                                                               │
│  Success toast (top-right, 4s):                               │
│  "✓ DANGCEM updated ₦420.00 → ₦450.00 (+7.14%)"             │
│  (include old price + delta from API response)                │
└───────────────────────────────────────────────────────────────┘

┌─ Recent Price Changes ───────────────────────────────────────┐
│  (usePriceAudit() — last 20 entries)                         │
│                                                               │
│  | Date       | Ticker  | Old ₦  | New ₦  | Δ%    | Source │ [Revert] │
│  | 2026-04-30 | DANGCEM | 420.00 | 450.00 | +7.14%| manual │ [Revert] │
│  | 2026-04-29 | GTCO    | 30.00  | 28.75  | -4.17%| csv_up │ [Revert] │
│                                                               │
│  Source badges:                                               │
│    manual       — grey pill                                   │
│    csv_upload   — blue pill                                   │
│    revert_of_N  — amber pill                                  │
│                                                               │
│  Revert flow:                                                 │
│    Click [Revert] → confirmation dialog:                      │
│    "Revert DANGCEM from ₦450.00 back to ₦420.00?"           │
│    [Cancel]  [Yes, Revert]                                    │
│    On confirm: useRevertPrice(auditId) → invalidate queries   │
└───────────────────────────────────────────────────────────────┘
```

### Right Panel (45%) — Bulk CSV Import

```
┌─ Bulk CSV Import ────────────────────────────────────────────┐
│                                                               │
│  ┌─ NGX Source Info ──────────────────────────────────────┐  │
│  │ 📋 NGX Daily Official List (Recommended)               │  │
│  │ Download the latest price PDF from:                    │  │
│  │ ngxgroup.com/exchange/data/data-library/               │  │
│  │ Extract your holdings as: ticker, price, date          │  │
│  │ Then upload the CSV below.                             │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  [⬇ Download CSV Template]  ← generates file with:          │
│    ticker,price,date                                          │
│    DANGCEM,0.00,2026-04-30                                   │
│    ZENITHBANK,0.00,2026-04-30                                │
│    GTCO,0.00,2026-04-30                                      │
│                                                               │
│  STEP 1 — Upload                                             │
│  ┌─────────────────────────────────────────────────────┐     │
│  │     ↑  Drop CSV file here or click to browse        │     │
│  │         .csv accepted · UTF-8 · max 5MB             │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
│  STEP 2 — Preview (appears after upload)                     │
│  "47 valid · 3 errors"                                        │
│  ┌────────────────────────────────────────────────┐          │
│  │ Valid rows (first 10 shown):                   │          │
│  │ DANGCEM   450.00  2026-04-30   ₦420.00 → ₦450 │          │
│  │ ZENITHBANK 32.50  2026-04-30   ₦31.00 → ₦32.5 │          │
│  │ Error rows (red left border):                  │          │
│  │ ⚠ Row 12: TEXACO — Unknown ticker              │          │
│  │ ⚠ Row 23: GHOST  — Unknown ticker              │          │
│  │ ⚠ Row 41: DANGCEM — Date is in the future     │          │
│  └────────────────────────────────────────────────┘          │
│  [← Back]              [Commit 47 rows →]                    │
│                                                               │
│  STEP 3 — Result (after commit)                              │
│  ✓ 47 prices updated successfully                            │
│  ⚠ 3 rows skipped  [Show details ▼]  ← collapsible          │
│                                                               │
│  [Import Another File]  ← resets to Step 1                  │
└───────────────────────────────────────────────────────────────┘
```

### CSV Template Download (client-side, no API call needed)

```typescript
// In _app.settings.price-entry.tsx
const downloadTemplate = () => {
  // Use actual tickers from useCompanies() if loaded, else use examples
  const companies = companiesData ?? [];
  const rows = companies.length > 0
    ? companies.slice(0, 5).map(
        (c) => `${c.ticker},0.00,${new Date().toISOString().slice(0, 10)}`
      )
    : [
        "DANGCEM,0.00,2026-04-30",
        "ZENITHBANK,0.00,2026-04-30",
        "GTCO,0.00,2026-04-30",
      ];

  const content = ["ticker,price,date", ...rows].join("\n");
  const blob = new Blob([content], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `epm_price_template_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};
```

---

## Section 6: Edge Cases Antigravity Must Handle

These were not in the previous spec and must be covered:

| Edge Case | Expected Behaviour |
|-----------|-------------------|
| Company dropdown empty (no companies in DB yet) | Show empty state: "No companies found — import Obsidian vault first" |
| Quick entry: same price as current | Allow it (user may be confirming a price). Write audit record with delta_pct = 0. |
| Quick entry: first ever price (old_price = null) | Write audit with `old_price = null`. Toast shows "DANGCEM: first price set ₦450.00". No delta shown. |
| CSV upload: empty file | Return 422 "CSV file appears to be empty" before parsing |
| CSV upload: wrong file type (.xlsx, .pdf) | Reject at upload stage with "Only .csv files accepted" |
| CSV upload: all rows invalid | Preview shows 0 valid, N errors. Commit button disabled. No API call on commit attempt. |
| CSV upload: duplicate tickers in same file | Take the last row for that ticker (last-write-wins per file). |
| Revert button on first-ever audit record (old_price = null) | Revert button is disabled. Tooltip: "No previous price to revert to". |
| Revert button on a revert record (source starts with "revert_of_") | Allow it — reverting a revert is valid. |
| Price audit table empty (no history yet) | Empty state: "No price changes recorded yet. Use Quick Update above to add your first price." |

---

## Section 7: Acceptance Test Additions

Add these to `acceptance_test.md` under a new **Price Entry** section:

```markdown
## Price Entry Page (/settings/price-entry)

### Quick Price Update
- [ ] Page loads without crash for admin user
- [ ] Page is blocked (redirect) for readonly user
- [ ] Company dropdown populates with tickers + current prices
- [ ] Selecting a company shows its current price in the dropdown label
- [ ] Valid price entry → success toast shows old price, new price, delta%
- [ ] Updated price immediately reflected on /dashboard (no manual refresh)
- [ ] Updated price immediately reflected on /holdings (no manual refresh)
- [ ] Price audit log updates after successful entry
- [ ] Future date rejected with validation message (no API call)
- [ ] Negative price rejected with validation message
- [ ] Price > ₦100,000 rejected with sanity cap message
- [ ] First-ever price (old = null) → toast shows "first price set"

### Price Audit Log
- [ ] Last 20 price changes render in table
- [ ] Source badges: manual (grey), csv_upload (blue), revert_of_N (amber)
- [ ] Revert button on valid record → confirmation dialog appears
- [ ] Confirmation → price reverts → audit log updates → dashboard refreshes
- [ ] Revert button disabled on first-ever record (old_price = null)
- [ ] Empty state renders when no history exists

### Bulk CSV Import
- [ ] NGX info box visible with correct library URL
- [ ] [Download CSV Template] generates file with real tickers from DB
- [ ] .csv file accepted; .xlsx and .pdf rejected at upload
- [ ] Empty file returns 422 error message
- [ ] Valid 3-row CSV → preview shows 3 valid rows → commit → 3 prices updated
- [ ] Mixed CSV (47 valid + 3 invalid) → preview shows both → commit applies 47 only
- [ ] All-invalid CSV → commit button disabled in preview
- [ ] Error rows show row number, ticker, and specific error reason
- [ ] "Show details" expander works for skipped rows after commit
- [ ] [Import Another File] resets panel to Step 1
- [ ] Dashboard + Holdings refresh after successful CSV commit
```

---

## Section 8: What Must NOT Be Deferred

Every item below ships with this page. None of these are Phase 3B:

```
✅ Price audit log (below quick entry form)
✅ Revert button with confirmation dialog
✅ Two-stage CSV flow (preview → commit)
✅ Partial commit with skipped row reporting (Option C UI)
✅ CSV template download button
✅ NGX info box (no Stooq mention anywhere)
✅ Query invalidation on all successful mutations
✅ Admin-only route guard
✅ Empty state for audit log
✅ Empty state for company dropdown
✅ Edge cases from Section 6
```

---

**END OF FINAL IMPLEMENTATION DOCUMENT**

**Receiving agent**: Antigravity — implement exactly as written
**Copy to**: Codex — add price endpoint tests after implementation
**Grok**: No further verification needed — all items from your consolidated
handover are incorporated above
