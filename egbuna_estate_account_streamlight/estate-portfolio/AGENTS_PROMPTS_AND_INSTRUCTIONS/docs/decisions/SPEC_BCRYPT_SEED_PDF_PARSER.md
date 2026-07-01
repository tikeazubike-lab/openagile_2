# Implementation Spec — BCrypt Fix + NGX Seed + PDF Parser
**From**: Claude (The Brain)
**To**: Antigravity / Cursor (Builder)
**Date**: 2026-05-05
**Protocol**: MASTER_CONTEXT.md v4.0
**Branch**: test
**Execute in this exact order — do not skip ahead**

---

## Task 1: bcrypt Downgrade (Execute First — Unblocks Everything)

```
File: backend/requirements.txt
Change: bcrypt==5.0.0  →  bcrypt==4.0.1
```

This is a one-line fix. Commit and push immediately so login is restored
before any other work begins.

```
git add backend/requirements.txt
git commit -m "fix: downgrade bcrypt to 4.0.1 — passlib incompatible with >= 4.1.0"
git push origin test
```

Wait for CI to pass and confirm login works on demo.estate.zubbystudio.shop
before proceeding to Task 2.

---

## Task 2: NGX Company Seed Script

### Design Decisions (Locked)
- Seed **company master data only**: ticker, name, sector, status
- Prices are **not** included in this script — PDF parser handles prices separately
- Source of truth: the NGX Daily Official List PDF the user provides
- Script is **idempotent**: skip companies that already exist (match on ticker)
- Script runs **on the VPS** via `docker compose exec backend python scripts/seed_ngx_companies.py`
- User provides the PDF — Antigravity reads it to extract the company list

### Step 1: Ask User for PDF

Before writing the script, Antigravity must read the NGX PDF the user
has available today. Ask the user to share it. Extract from the PDF:
- All company tickers
- Company full names
- Sectors (if listed in PDF — otherwise mark as "Unknown" for now)
- Status: default all to "listed" unless the PDF explicitly marks otherwise

### Step 2: Build the Seed Script

```python
# backend/scripts/seed_ngx_companies.py
"""
One-time NGX company master data seed.
Reads a hardcoded list of NGX companies extracted from the NGX Daily
Official List PDF. Inserts new companies only — skips existing tickers.

Usage (on VPS):
  docker compose exec backend python scripts/seed_ngx_companies.py
  docker compose exec backend python scripts/seed_ngx_companies.py --dry-run

The company list below must be populated from the NGX PDF before running.
"""
import asyncio
import sys
from sqlalchemy import select
from app.database import get_async_session
from app.models import Company

# ── POPULATE THIS LIST FROM THE NGX PDF ──────────────────────────────────────
# Format: (ticker, name, sector, status)
# status options: listed | delisted | defunct | merged | uncertain
NGX_COMPANIES = [
    # Antigravity populates this from the PDF the user provides
    # Example format:
    # ("DANGCEM", "Dangote Cement PLC", "Industrial Goods", "listed"),
    # ("GTCO", "Guaranty Trust Holding Company PLC", "Financial Services", "listed"),
    # ("ZENITHBANK", "Zenith Bank PLC", "Financial Services", "listed"),
    # ... all companies from PDF
]
# ─────────────────────────────────────────────────────────────────────────────

async def seed(dry_run: bool = False):
    async with get_async_session() as db:
        inserted = 0
        skipped = 0
        errors = []

        for ticker, name, sector, status in NGX_COMPANIES:
            try:
                existing = await db.execute(
                    select(Company).where(Company.ticker == ticker.upper())
                )
                if existing.scalar_one_or_none():
                    skipped += 1
                    continue

                if not dry_run:
                    company = Company(
                        ticker=ticker.upper(),
                        name=name,
                        sector=sector,
                        status=status,
                        obsidian_imported=False,
                    )
                    db.add(company)
                inserted += 1

            except Exception as e:
                errors.append(f"{ticker}: {e}")

        if not dry_run:
            await db.commit()

        mode = "DRY RUN" if dry_run else "LIVE"
        print(f"\nNGX Company Seed — {mode}")
        print(f"  Inserted: {inserted}")
        print(f"  Skipped (already exist): {skipped}")
        print(f"  Errors: {len(errors)}")
        for err in errors:
            print(f"  ❌ {err}")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry_run))
```

### Step 3: Run Order on VPS

```bash
# Always dry-run first
docker compose exec backend python scripts/seed_ngx_companies.py --dry-run

# Confirm output shows expected company count (~150-200 NGX companies)
# Then run live
docker compose exec backend python scripts/seed_ngx_companies.py
```

---

## Task 3: PDF Parser

### Architecture Decision (Locked)

```
User uploads NGX PDF → FastAPI endpoint receives it
→ pdfplumber extracts price table
→ Prices written to price_audit + companies.current_price
→ Summary returned: N updated, M skipped, errors listed

This replaces the manual PDF → CSV → upload workflow entirely.
```

### New Dependency

```
# Add to backend/requirements.txt
pdfplumber==0.11.4   # PDF table extraction — actively maintained
```

### New Endpoint

```
POST /api/v1/prices/upload-pdf
  Body: multipart/form-data, file: .pdf
  Auth: admin only
  Returns: {
    data: {
      extracted_rows: N,
      updated: N,
      skipped: N,       # unknown tickers
      errors: N,
      error_details: [{ ticker, reason }],
      committed: true
    },
    error: null
  }
```

### NGX PDF Structure (from doclib.ngxgroup.com)

The NGX Daily Official List PDF has a consistent table structure:
```
COMPANY NAME | SYMBOL | OPEN | HIGH | LOW | CLOSE | VOLUME | ...
```

The parser targets:
- `SYMBOL` column → ticker
- `CLOSE` column → today's price
- Date is extracted from the PDF filename or first page header

### Parser Implementation

```python
# backend/app/routers/prices.py — add this endpoint

import pdfplumber
import re
from datetime import date as date_type

@router.post("/upload-pdf")
async def upload_ngx_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """
    Parse NGX Daily Official List PDF and update prices directly.
    No manual CSV conversion needed.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files accepted")

    content = await file.read()

    # Write to temp file for pdfplumber (requires file path or bytes)
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    extracted = []
    parse_errors = []

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # Find header row to locate SYMBOL and CLOSE columns
                    header = [
                        (cell or "").strip().upper()
                        for cell in table[0]
                    ]

                    symbol_idx = next(
                        (i for i, h in enumerate(header)
                         if h in ("SYMBOL", "TICKER", "CODE")), None
                    )
                    close_idx = next(
                        (i for i, h in enumerate(header)
                         if h in ("CLOSE", "CLOSING", "CLOSE PRICE")), None
                    )

                    if symbol_idx is None or close_idx is None:
                        continue  # not the price table — skip

                    for row in table[1:]:
                        if not row or len(row) <= max(symbol_idx, close_idx):
                            continue

                        ticker = (row[symbol_idx] or "").strip().upper()
                        price_str = (row[close_idx] or "").strip()

                        # Clean price string (remove commas, spaces)
                        price_str = re.sub(r"[,\s]", "", price_str)

                        if not ticker or not price_str:
                            continue

                        try:
                            price = Decimal(price_str)
                            if price <= 0:
                                raise ValueError("Non-positive price")
                            extracted.append((ticker, price))
                        except (InvalidOperation, ValueError):
                            parse_errors.append({
                                "ticker": ticker,
                                "reason": f"Could not parse price: {price_str!r}"
                            })
    finally:
        os.unlink(tmp_path)

    if not extracted:
        raise HTTPException(
            status_code=422,
            detail="No price data found in PDF. "
                   "Ensure this is an NGX Daily Official List PDF."
        )

    # Pre-load ticker map
    result = await db.execute(
        select(Company).where(Company.deleted_at.is_(None))
    )
    companies = {c.ticker.upper(): c for c in result.scalars().all()}

    today = date_type.today()
    updated = 0
    skipped_unknown = []

    for ticker, price in extracted:
        company = companies.get(ticker)
        if not company:
            skipped_unknown.append({"ticker": ticker, "reason": "Unknown ticker — not in database"})
            continue

        # Write audit record before updating
        db.add(PriceAudit(
            company_id=company.id,
            old_price=company.current_price,
            new_price=price,
            changed_at=today,
            changed_by=current_user.id,
            source="ngx_pdf_upload",
        ))
        company.current_price = price
        company.last_price_update = today
        updated += 1

    await db.commit()

    all_errors = parse_errors + skipped_unknown

    return {
        "data": {
            "extracted_rows": len(extracted),
            "updated": updated,
            "skipped": len(skipped_unknown),
            "parse_errors": len(parse_errors),
            "error_details": all_errors[:50],  # cap at 50 for response size
            "committed": True,
        },
        "error": None,
    }
```

### Frontend: Replace CSV Panel with PDF Upload

Update `_app.settings.price-entry.tsx` right panel:

```
RIGHT PANEL — UPDATED LAYOUT:

┌─ NGX Price Update ───────────────────────────────────────────┐
│                                                               │
│  ┌─ Primary: Upload NGX PDF ──────────────────────────────┐  │
│  │  📄 Upload the NGX Daily Official List PDF directly.   │  │
│  │  No manual conversion needed — prices are extracted    │  │
│  │  automatically.                                        │  │
│  │                                                        │  │
│  │  Download PDF: ngxgroup.com/exchange/data/data-library │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │  ↑  Drop NGX PDF here or click to browse         │  │  │
│  │  │     .pdf only · max 20MB                         │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  [Upload & Parse PDF]  ← lavender button              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  Result (after upload):                                       │
│  ✓ 142 prices updated from NGX PDF                           │
│  ⚠ 8 tickers not in database  [Show details ▼]              │
│  [Upload Another PDF]                                         │
│                                                               │
│  ── OR ─────────────────────────────────────────────────────  │
│                                                               │
│  ┌─ Alternative: Manual CSV Upload ──────────────────────┐   │
│  │  If you prefer CSV format:                            │   │
│  │  Required columns: ticker, price, date                │   │
│  │  [Download CSV Template]  [Upload CSV]                │   │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

PDF upload is the primary workflow. CSV is kept as a fallback for
partial updates or manually corrected prices.

### New TanStack Query Hook

```typescript
// Add to src/api/queries.ts
export function useUploadNGXPdf() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return fetch("/api/v1/prices/upload-pdf", {
        method: "POST",
        credentials: "include",
        body: form,
      }).then((r) => r.json());
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      qc.invalidateQueries({ queryKey: ["holdings"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      qc.invalidateQueries({ queryKey: ["price-audit"] });
    },
  });
}
```

---

## Task 4: Combobox Background Fix

While in `_app.settings.price-entry.tsx`, fix the transparent dropdown:

```typescript
// Find the PopoverContent / Command component rendering company options
// Change:
className="bg-transparent"  // or bg-[var(--card)]

// To:
className="bg-[var(--bg-surface)] border border-[var(--border)] shadow-lg z-50"
```

This uses the CSS variable pattern so it works in both light and dark mode.

---

## Execution Order

```
1. [ ] Fix bcrypt==4.0.1 → commit → push → verify login restored
2. [ ] Ask user to share NGX PDF → extract company list
3. [ ] Build seed_ngx_companies.py with full NGX company list from PDF
4. [ ] Run --dry-run on VPS → confirm count → run live
5. [ ] Add pdfplumber==0.11.4 to requirements.txt
6. [ ] Add POST /api/v1/prices/upload-pdf endpoint to prices.py
7. [ ] Update right panel UI: PDF upload primary, CSV secondary
8. [ ] Add useUploadNGXPdf() hook to queries.ts
9. [ ] Fix combobox transparent background
10.[ ] Commit all → push to test → verify CI passes
11.[ ] Test PDF upload with today's NGX PDF on staging
12.[ ] Write acceptance test handover to Claude
```

---

## Acceptance Test (Fill in After Implementation)

```markdown
## Acceptance Test — BCrypt + Seed + PDF Parser

### BCrypt Fix
- [ ] Login works at demo.estate.zubbystudio.shop
- [ ] No 500 errors in server logs related to passlib/bcrypt

### Company Seed
- [ ] ZENITHBANK appears in company dropdown on Price Entry page
- [ ] Company count in dropdown matches NGX PDF company count
- [ ] Re-running seed script skips existing companies (idempotent)

### PDF Parser
- [ ] Upload today's NGX PDF → prices extracted without error
- [ ] Updated count matches expected number of companies in DB
- [ ] Unknown tickers (not yet in DB) listed in error details
- [ ] Price audit log shows source = 'ngx_pdf_upload'
- [ ] Dashboard + Holdings reflect updated prices after upload

### Combobox Fix
- [ ] Company dropdown has solid background (not transparent)
- [ ] Readable in both light and dark mode
```

---

**After completing all tasks**: send acceptance test results to Claude
before starting the next page (Transactions or Companies CRUD).

**Do not** start any new pages until this handover is received.
