from datetime import date as date_type
from decimal import Decimal, InvalidOperation
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, field_validator
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session, get_current_user, require_admin
from app.models import Company, PriceAudit, PriceHistory, User

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])

MAX_CSV_BYTES = 5 * 1024 * 1024

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

import pdfplumber
import re

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

    # Pre-load ticker map and name map to support both Official List (tickers) and Daily Summary (names)
    result = await db.execute(
        select(Company).where(Company.deleted_at.is_(None))
    )
    all_companies = result.scalars().all()
    companies_by_ticker = {c.ticker.upper(): c for c in all_companies}
    
    def normalize_name(name):
        return re.sub(r'[^A-Z0-9]', '', name.upper())
        
    companies_by_name = {normalize_name(c.name): c for c in all_companies}

    extracted = []
    parse_errors = []

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                for line in text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    parts = line.split()
                    
                    # Data rows start with an S/N digit
                    if len(parts) >= 4 and parts[0].isdigit():
                        
                        # 1. Find the symbol by scanning backwards for the first word containing a letter
                        symbol_index = -1
                        for i in range(len(parts) - 1, 0, -1):
                            if re.search(r'[A-Za-z]', parts[i]):
                                symbol_index = i
                                break
                                
                        if symbol_index == -1 or symbol_index == len(parts) - 1:
                            continue
                            
                        text_parts = parts[1:symbol_index + 1]
                        potential_ticker = text_parts[-1].upper()
                        normalized_pdf_name = re.sub(r'[^A-Z0-9]', '', ' '.join(text_parts).upper())
                        
                        # Match company by ticker first (Official List), then by name (Daily Summary)
                        company = companies_by_ticker.get(potential_ticker)
                        if not company:
                            # Try fuzzy name matching
                            for name_key, comp in companies_by_name.items():
                                if normalized_pdf_name == name_key or normalized_pdf_name.startswith(name_key) or name_key.startswith(normalized_pdf_name):
                                    company = comp
                                    break
                                    
                        # If we still can't find the company, it's an unlisted bond or untracked stock
                        if not company:
                            continue
                            
                        numeric_parts = parts[symbol_index + 1:]
                        
                        # Extract price based on number of numeric columns
                        # Equities Official List: 9 numeric columns (PClose, Open, High, Low, Close...)
                        # Daily Summary: 5 numeric columns (Market Cap, Price, %Change, Trades, Volume)
                        # Gainers/Losers: 3 numeric columns (Close, Change, %Change)
                        if len(numeric_parts) >= 8:
                            price_str = numeric_parts[4]  # Close price is 5th numeric column
                            if price_str == "-":
                                price_str = numeric_parts[0]
                        elif len(numeric_parts) == 5:
                            price_str = numeric_parts[1]  # Price is 2nd numeric column in Daily Summary
                        elif len(numeric_parts) >= 1:
                            price_str = numeric_parts[0]  # Close price is 1st numeric column for Gainers/Losers
                        else:
                            continue
                            
                        # Clean price string (remove commas)
                        price_str = re.sub(r"[,\s]", "", price_str)

                        if not price_str or price_str == "-":
                            continue

                        try:
                            price = Decimal(price_str)
                            if price <= 0:
                                raise ValueError("Non-positive price")
                            extracted.append((company.ticker.upper(), price))
                        except (InvalidOperation, ValueError):
                            parse_errors.append({
                                "ticker": company.ticker.upper(),
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

    def extract_date_from_pdf_filename(filename: str):
        import re
        from datetime import date
        m = re.search(r'(\d{2})[.\-_ ](\d{2})[.\-_ ](\d{4})', filename)
        if m:
            try:
                return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                pass
        m = re.search(r'(\d{2})(\d{2})(\d{4})', filename)
        if m:
            try:
                return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                pass
        return None

    today = extract_date_from_pdf_filename(file.filename) or date_type.today()
    updated = 0

    # Pre-fetch existing PriceHistory for today to prevent UniqueConstraint errors
    hist_result = await db.execute(
        select(PriceHistory).where(PriceHistory.price_date == today)
    )
    existing_history = {h.company_id: h for h in hist_result.scalars().all()}

    for ticker, price in extracted:
        company = companies_by_ticker.get(ticker)
        if not company:
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
        
        # Write or update price_history table
        hist_record = existing_history.get(company.id)
        if hist_record:
            hist_record.close_price = price
            hist_record.source = "ngx_pdf_upload"
        else:
            new_hist = PriceHistory(
                company_id=company.id,
                price_date=today,
                close_price=price,
                source="ngx_pdf_upload",
            )
            db.add(new_hist)
            existing_history[company.id] = new_hist

        company.current_price = price
        company.last_price_update = today
        updated += 1

    await db.commit()

    all_errors = parse_errors

    return {
        "data": {
            "extracted_rows": len(extracted),
            "updated": updated,
            "skipped": 0,
            "parse_errors": len(parse_errors),
            "error_details": all_errors[:50],  # cap at 50 for response size
            "committed": True,
        },
        "error": None,
    }

def _envelope(data, meta=None):
    return {"data": data, "meta": meta if meta is not None else {}, "error": None}

@router.get("/history/{company_id}")
async def get_price_history(
    company_id: int,
    days: int = 30,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime, timedelta, timezone
    
    query = select(PriceHistory).where(PriceHistory.company_id == company_id)
    if days > 0:
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
        query = query.where(PriceHistory.price_date >= cutoff)
        
    query = query.order_by(PriceHistory.price_date.asc())
    result = await db.execute(query)
    
    data = []
    for hist in result.scalars().all():
        data.append({
            "id": hist.id,
            "recorded_date": hist.price_date.isoformat(),
            "price": str(hist.close_price),
            "source": hist.source,
        })
        
    return _envelope(data, meta={"total": len(data)})

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

@router.post("/bulk-csv")
async def bulk_csv_import(
    file: UploadFile = File(...),
    commit: bool = Form(False),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    import csv, io

    content = await file.read()
    if len(content) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 5MB limit")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File must be UTF-8 encoded")

    if not text.strip():
        raise HTTPException(status_code=422, detail="CSV file appears to be empty")

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
    warning_rows = []
    today = date_type.today()

    for i, raw_row in enumerate(reader, start=2):
        row = normalise_row(raw_row)
        ticker = row.get("ticker", "").upper()
        price_str = row.get("price", "")
        date_str = row.get("date", "")
        errors = []
        warnings = []

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
                warnings.append("Date is older than 30 days")
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
                "row": i,
                "ticker": ticker,
                "price": price,
                "date": entry_date,
                "company_id": company_row.id,
                "old_price": company_row.current_price,
            })
            if warnings:
                warning_rows.append({
                    "row": i,
                    "ticker": ticker,
                    "price": price_str,
                    "date": date_str,
                    "warnings": warnings,
                })

    # Dedupe duplicate tickers in a single file (last-write-wins per spec).
    # Keep the last occurrence by row number.
    deduped_by_ticker = {}
    for r in valid_rows:
        deduped_by_ticker[r["ticker"]] = r
    valid_rows = sorted(deduped_by_ticker.values(), key=lambda r: r["row"])

    # STAGE 1 — Preview (commit=False)
    if not commit:
        return {
            "data": {
                "valid": len(valid_rows),
                "errors": len(error_rows),
                "warnings": len(warning_rows),
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
                "warning_rows": warning_rows,
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
