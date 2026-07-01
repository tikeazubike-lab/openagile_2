# Claude Review — Price Entry Page Implementation Plan (Phase 3A)
**From**: Claude (The Brain)
**To**: Deepseek:flash (Implementer)
**Date**: 2026-04-30
**Protocol**: MASTER_CONTEXT.md v4.0
**Input**: Antigravity Phase 3A implementation plan for `/settings/price-entry`

---

## Answers to Open Questions

### CSV Format — LOCKED
```
Columns: ticker, price, date
Example:
  DANGCEM,450.00,2026-04-30
  ZENITHBANK,32.50,2026-04-30
  GTCO,28.75,2026-04-30

Rules:
  - Header row required (exact lowercase column names)
  - date format: YYYY-MM-DD
  - price: numeric, no ₦ symbol, decimal point separator
  - No extra columns needed — source recorded internally as 'csv_upload'

Rationale: Matches Stooq scraper output exactly. Zero transformation
needed between scraper output and app upload. Source tracked in
price_audit table server-side, not in the file.
```

### History Tracking — LOCKED
Price history **must** be logged. Simple overwrite is not sufficient.

Reasons:
1. The `price_audit` table is already in the Phase 2B schema — it exists
2. The revert button (specced in STLC and wireframes) requires audit records
3. The Dashboard "Last Updated" timestamp needs a source of truth
4. Without history, there is no way to know if a price is stale

Implementation: Every `PUT /api/v1/companies/{id}/price` call must:
1. Read the current price from the Company row
2. Write a new row to `price_audit` (company_id, old_price, new_price, changed_at, source)
3. Update `current_price` and `last_price_update` on the Company row
4. All three operations in a single DB transaction

---

## Review of Proposed Changes

### Backend — Corrections Required

#### Issue 1: Wrong router for price updates

Antigravity proposes putting price update logic in `companies.py`.
This is incorrect. Per the API contract (Phase 2 Final Handover Brief Part B):

```
Price endpoints belong in a dedicated prices router:
  GET    /api/v1/prices              — current prices for all companies
  POST   /api/v1/prices/quick        — single stock quick price entry
  POST   /api/v1/prices/bulk-csv     — bulk CSV import (two-stage)
  GET    /api/v1/prices/history/{id} — price history for one company
  GET    /api/v1/prices/audit        — recent 50 price changes
  POST   /api/v1/prices/audit/{id}/revert — revert a price change
```

Companies router is for company master data (name, sector, registrar,
status). Prices router is for price operations. Keep them separated —
this maintains the single-responsibility principle and matches the
frontend hooks already specced in `queries.ts`.

**Action**: Create `backend/app/routers/prices.py` not a price endpoint
inside `companies.py`. Companies router can still be created for the
company list endpoint `GET /api/v1/companies` — that's correct.

#### Issue 2: Missing price_audit write

The proposed `PUT /api/v1/companies/{id}/price` does not mention writing
to `price_audit`. This must be included. See the complete endpoint spec
below.

#### Issue 3: Verification plan is insufficient

`npm run build` and `docker compose build --no-cache epm` verify
compilation only — not behaviour. The verification plan must include
the manual acceptance steps listed in Section 5 of this document.

### Frontend — Correct, with One Addition

The proposed frontend changes are correctly structured. One addition:
the Price Entry page must also show the **price audit log** (last 20
changes) below the quick entry form, with a revert button per row.
This was specced in the wireframe document and must be implemented
alongside the quick entry form, not deferred.

---

## Complete Implementation Spec

### Backend: `backend/app/routers/prices.py` (NEW FILE)

```python
# backend/app/routers/prices.py

from datetime import date as date_type
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.deps import get_current_user, require_admin
from app.models import Company, PriceAudit, User

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])


# ── GET /api/v1/prices ────────────────────────────────────────────────────────
@router.get("")
async def get_current_prices(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Return current price for all active companies."""
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


# ── POST /api/v1/prices/quick ─────────────────────────────────────────────────
@router.post("/quick")
async def quick_price_update(
    payload: dict,   # { company_id: int, price: str, entry_date: str }
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """
    Update a single company's current price.
    Writes to price_audit BEFORE updating Company row.
    All operations in a single transaction.
    """
    company_id = payload.get("company_id")
    new_price_str = payload.get("price")
    entry_date_str = payload.get("entry_date")

    # Validate price
    try:
        new_price = Decimal(str(new_price_str))
        if new_price <= 0:
            raise ValueError("Price must be positive")
        if new_price > 100_000:
            raise HTTPException(
                status_code=422,
                detail="Price exceeds ₦100,000 sanity cap — verify before submitting"
            )
    except (InvalidOperation, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Validate date
    try:
        entry_date = date_type.fromisoformat(entry_date_str)
        if entry_date > date_type.today():
            raise HTTPException(status_code=422, detail="Entry date cannot be in the future")
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Invalid date format — use YYYY-MM-DD")

    # Fetch company
    result = await db.execute(
        select(Company).where(Company.id == company_id).where(Company.deleted_at.is_(None))
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    # Write audit record FIRST (captures old price)
    audit = PriceAudit(
        company_id=company.id,
        old_price=company.current_price,   # None if first price entry
        new_price=new_price,
        changed_at=entry_date,
        changed_by=current_user.id,
        source="manual",
    )
    db.add(audit)

    # Update company price
    company.current_price = new_price
    company.last_price_update = entry_date

    await db.commit()
    await db.refresh(audit)

    return {
        "data": {
            "ticker": company.ticker,
            "old_price": str(audit.old_price) if audit.old_price else None,
            "new_price": str(new_price),
            "entry_date": entry_date_str,
            "audit_id": audit.id,
        },
        "error": None,
    }


# ── POST /api/v1/prices/bulk-csv ─────────────────────────────────────────────
@router.post("/bulk-csv")
async def bulk_csv_import(
    file: UploadFile = File(...),
    commit: bool = Form(False),   # False = preview, True = commit
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """
    Two-stage bulk CSV import.
    Stage 1 (commit=False): parse + validate, return preview
    Stage 2 (commit=True):  apply valid rows, return summary

    CSV format: ticker,price,date (header row required)
    """
    import csv, io
    from datetime import date as date_type

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File must be UTF-8 encoded")

    reader = csv.DictReader(io.StringIO(text))

    # Validate headers
    required_cols = {"ticker", "price", "date"}
    if not reader.fieldnames or not required_cols.issubset(
        set(f.strip().lower() for f in reader.fieldnames)
    ):
        raise HTTPException(
            status_code=422,
            detail=f"CSV must have headers: ticker, price, date"
        )

    # Pre-load all company tickers for fast lookup
    result = await db.execute(
        select(Company.id, Company.ticker, Company.current_price)
        .where(Company.deleted_at.is_(None))
    )
    ticker_map = {row.ticker: row for row in result.fetchall()}

    valid_rows = []
    error_rows = []

    for i, row in enumerate(reader, start=2):  # start=2 (row 1 = header)
        ticker = (row.get("ticker") or "").strip().upper()
        price_str = (row.get("price") or "").strip()
        date_str = (row.get("date") or "").strip()
        errors = []

        # Ticker validation
        if ticker not in ticker_map:
            errors.append(f"Unknown ticker '{ticker}'")

        # Price validation
        try:
            price = Decimal(price_str)
            if price <= 0:
                errors.append("Price must be positive")
            if price > 100_000:
                errors.append("Price exceeds ₦100,000 sanity cap")
        except InvalidOperation:
            errors.append(f"Invalid price '{price_str}'")
            price = None

        # Date validation
        try:
            entry_date = date_type.fromisoformat(date_str)
            if entry_date > date_type.today():
                errors.append("Date is in the future")
        except (ValueError, TypeError):
            errors.append(f"Invalid date '{date_str}' — use YYYY-MM-DD")
            entry_date = None

        if errors:
            error_rows.append({
                "row": i, "ticker": ticker,
                "price": price_str, "date": date_str,
                "errors": errors,
            })
        else:
            valid_rows.append({
                "ticker": ticker, "price": price,
                "date": entry_date,
                "company_id": ticker_map[ticker].id,
                "old_price": ticker_map[ticker].current_price,
            })

    # STAGE 1 — Preview only
    if not commit:
        return {
            "data": {
                "valid": len(valid_rows),
                "errors": len(error_rows),
                "preview_rows": valid_rows[:10],  # first 10 for UI preview
                "error_rows": error_rows,
                "committed": False,
            },
            "error": None,
        }

    # STAGE 2 — Commit valid rows atomically
    committed = 0
    for row in valid_rows:
        result = await db.execute(
            select(Company).where(Company.id == row["company_id"])
        )
        company = result.scalar_one_or_none()
        if not company:
            continue

        audit = PriceAudit(
            company_id=company.id,
            old_price=company.current_price,
            new_price=row["price"],
            changed_at=row["date"],
            changed_by=current_user.id,
            source="csv_upload",
        )
        db.add(audit)
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


# ── GET /api/v1/prices/audit ─────────────────────────────────────────────────
@router.get("/audit")
async def get_price_audit(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Return last 50 price changes across all companies."""
    result = await db.execute(
        select(PriceAudit, Company.ticker, Company.name)
        .join(Company, PriceAudit.company_id == Company.id)
        .order_by(desc(PriceAudit.changed_at))
        .limit(50)
    )
    rows = result.fetchall()
    return {
        "data": [
            {
                "id": row.PriceAudit.id,
                "ticker": row.ticker,
                "company_name": row.name,
                "old_price": str(row.PriceAudit.old_price)
                    if row.PriceAudit.old_price else None,
                "new_price": str(row.PriceAudit.new_price),
                "changed_at": row.PriceAudit.changed_at.isoformat(),
                "source": row.PriceAudit.source,
            }
            for row in rows
        ],
        "meta": {"total": len(rows)},
        "error": None,
    }


# ── POST /api/v1/prices/audit/{id}/revert ────────────────────────────────────
@router.post("/audit/{audit_id}/revert")
async def revert_price_change(
    audit_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Revert a price change by restoring old_price as a new price entry."""
    result = await db.execute(
        select(PriceAudit).where(PriceAudit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit record not found")
    if audit.old_price is None:
        raise HTTPException(
            status_code=422,
            detail="Cannot revert — no previous price recorded"
        )

    result = await db.execute(
        select(Company).where(Company.id == audit.company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Write a new audit record for the revert
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
    return {"data": {"reverted_to": str(audit.old_price)}, "error": None}
```

---

### Backend: `backend/app/routers/companies.py` (NEW FILE)

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
    """List all non-deleted companies with current price."""
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

### Backend: `backend/app/main.py` — Wire New Routers

```python
# Add to existing router includes in main.py:
from app.routers.companies import router as companies_router
from app.routers.prices import router as prices_router

app.include_router(companies_router)
app.include_router(prices_router)
```

---

### Frontend: `src/api/queries.ts` — New Hooks

```typescript
// Add to existing queries.ts

// ── Companies ──────────────────────────────────────────────────────────────
export function useCompanies() {
  return useQuery({
    queryKey: ["companies"],
    queryFn: () =>
      fetch("/api/v1/companies", { credentials: "include" })
        .then((r) => r.json())
        .then((r) => r.data),
  });
}

// ── Prices ─────────────────────────────────────────────────────────────────
export function useQuickPriceUpdate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: {
      company_id: number;
      price: string;
      entry_date: string;
    }) =>
      fetch("/api/v1/prices/quick", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }).then((r) => r.json()),
    onSuccess: () => {
      // Invalidate all price-dependent queries so dashboard + holdings refresh
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}

export function usePriceAudit() {
  return useQuery({
    queryKey: ["price-audit"],
    queryFn: () =>
      fetch("/api/v1/prices/audit", { credentials: "include" })
        .then((r) => r.json())
        .then((r) => r.data),
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

### Frontend: Price Entry Page Layout

The page must implement **both panels** in this session — not just the
quick entry form. The audit log is not a Phase 3B item; it is part of
this page spec and must ship together.

```
/settings/price-entry layout:

LEFT PANEL (55%):
  ┌─ Quick Price Update ──────────────────────────────────────┐
  │  Company dropdown (searchable, from useCompanies())        │
  │  Shows: [TICKER] Company Name — Current: ₦XX.XX           │
  │  New Price input (DM Mono, large, ₦ prefix)               │
  │  Date picker (default today, no future dates)              │
  │  [Update Price] button (lavender, full width)              │
  │  Success toast: "DANGCEM updated → ₦450.00"               │
  ├─ Recent Price Changes ────────────────────────────────────┤
  │  Table (last 20 from usePriceAudit()):                    │
  │  | Date | Ticker | Old | New | Δ% | Source | [Revert] |  │
  │  Source badges: manual / csv_upload / revert_of_N         │
  │  Revert: opens confirmation dialog before firing          │
  └───────────────────────────────────────────────────────────┘

RIGHT PANEL (45%):
  ┌─ Bulk CSV Import ─────────────────────────────────────────┐
  │  STEP 1: Drop zone (accept .csv only)                     │
  │    Stooq reminder note (lavender info box)                │
  │    CSV format reminder: ticker,price,date                 │
  │    [Download Template] link (generates 3-col CSV header)  │
  │                                                           │
  │  STEP 2: Preview table (appears after upload)             │
  │    Valid rows: normal                                      │
  │    Error rows: red left border + error tooltip             │
  │    Summary: "47 valid · 3 errors"                         │
  │    [← Back] [Commit 47 rows →]                           │
  │                                                           │
  │  STEP 3: Result (after commit)                            │
  │    "47 prices updated"                                    │
  │    Error rows list if any skipped                         │
  │    [Import Another] button                                │
  └───────────────────────────────────────────────────────────┘
```

---

## Verification Plan (Complete)

Antigravity's proposed verification plan covers compilation only.
The full verification required:

```
Compilation checks:
  [ ] npm run build — no TypeScript errors
  [ ] docker compose build --no-cache epm — no build errors
  [ ] docker compose up -d — container starts, no crash on startup

API verification (curl on VPS):
  [ ] GET  /api/v1/companies → returns list with current_price
  [ ] GET  /api/v1/prices    → returns price list
  [ ] POST /api/v1/prices/quick (valid payload) → 200, audit row created
  [ ] POST /api/v1/prices/quick (future date) → 422
  [ ] POST /api/v1/prices/quick (price > 100000) → 422
  [ ] POST /api/v1/prices/quick (unknown company_id) → 404
  [ ] POST /api/v1/prices/bulk-csv (commit=false) → preview, no DB change
  [ ] POST /api/v1/prices/bulk-csv (commit=true) → prices updated
  [ ] GET  /api/v1/prices/audit → returns up to 50 entries
  [ ] POST /api/v1/prices/audit/{id}/revert → price reverted

Manual UI verification:
  [ ] Navigate to /settings/price-entry — page renders, no crashes
  [ ] Company dropdown populates with tickers + current prices
  [ ] Update ZENITHBANK price → success toast appears
  [ ] Navigate to /dashboard → ZENITHBANK value reflects new price
  [ ] Navigate to /holdings → ZENITHBANK row reflects new price
  [ ] Price audit log shows the change with old + new price
  [ ] Revert button on audit log → confirmation dialog → price reverts
  [ ] Upload valid CSV (3 rows) → preview shows 3 valid → commit → 3 updated
  [ ] Upload CSV with one bad row → preview shows error row in red → valid rows committable
  [ ] Readonly user cannot access /settings/price-entry (redirected)
```

---

## What Antigravity Must NOT Skip

These items were in the original spec and must ship with this page,
not deferred:

1. **Price audit log** — the table below the quick entry form
2. **Revert button** — with confirmation dialog
3. **CSV validation** — both invalid price and unknown ticker cases
4. **Readonly route guard** — `/settings/price-entry` is admin-only
5. **Query invalidation on success** — dashboard + holdings must refresh
   automatically after a price update without manual page reload

---

**END OF IMPLEMENTATION SPEC**
**Forward to**: Antigravity for implementation
**Copy to**: Codex to add price endpoint tests once implementation is complete
