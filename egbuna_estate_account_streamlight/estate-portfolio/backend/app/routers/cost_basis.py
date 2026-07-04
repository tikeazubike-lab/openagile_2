import csv
import io
from datetime import date as date_type
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.deps import get_session, get_current_user, require_admin
from app.models import Company, Holding, ClaimRecord, User

router = APIRouter(prefix="/api/v1/cost-basis", tags=["cost-basis"])

MAX_CSV_BYTES = 5 * 1024 * 1024


def _envelope(data, meta=None):
    return {"data": data, "meta": meta if meta is not None else {}, "error": None}


async def _resolve_company(
    db: AsyncSession,
    ticker: str,
    company_name: str,
) -> Company:
    """3-step ticker matching workflow per spec F-COST-BASIS."""
    # STEP 1 — Match by ticker (case-insensitive)
    result = await db.execute(
        select(Company)
        .where(Company.deleted_at.is_(None))
        .where(Company.ticker.ilike(ticker))
    )
    company = result.scalar_one_or_none()
    if company:
        return company

    # STEP 2 — Match by company name (case-insensitive)
    if company_name:
        result = await db.execute(
            select(Company)
            .where(Company.deleted_at.is_(None))
            .where(Company.name.ilike(company_name))
        )
        company = result.scalar_one_or_none()
        if company:
            return company

    # STEP 3 — No match, create new company
    company = Company(
        ticker=ticker.upper(),
        name=company_name or ticker.upper(),
        status="listed",
    )
    db.add(company)
    await db.flush()
    return company


async def _create_holding(
    db: AsyncSession,
    company: Company,
    avg_purchase_price: Decimal,
    quantity: Decimal,
    purchase_date: date_type | None,
) -> Holding:
    """Create holding with correct type and optional ClaimRecord."""
    total_cost = avg_purchase_price * quantity
    is_claim = company.status in ("delisted", "defunct")

    holding = Holding(
        company_id=company.id,
        num_shares=quantity,
        average_cost_basis=avg_purchase_price,
        total_cost=total_cost,
        holding_type="claim" if is_claim else "active",
        cost_basis_override=Decimal("0.00") if is_claim else None,
        purchase_date=purchase_date or date_type.today(),
    )
    db.add(holding)
    await db.flush()

    if is_claim:
        claim = ClaimRecord(
            holding_id=holding.id,
            claim_type="liquidation",
            claim_status="pending",
            expected_payout=Decimal("0.00"),
        )
        db.add(claim)

    return holding


# ─── Quick Entry ─────────────────────────────────────────────────────────────

@router.post("/quick", status_code=201)
async def quick_cost_basis(
    ticker: str = Form(...),
    company_name: str = Form(""),
    avg_purchase_price: str = Form(...),
    quantity: int = Form(...),
    purchase_date: str = Form(""),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    if not ticker.strip():
        raise HTTPException(status_code=422, detail="ticker is required")

    try:
        price = Decimal(avg_purchase_price)
        if price <= 0:
            raise ValueError("Price must be positive")
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=422, detail=f"Invalid price: {avg_purchase_price!r}")

    if quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be positive")

    parsed_date = None
    if purchase_date:
        try:
            parsed_date = date_type.fromisoformat(purchase_date)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail=f"Invalid date: {purchase_date!r}")

    company = await _resolve_company(db, ticker.strip(), company_name.strip())
    holding = await _create_holding(db, company, price, Decimal(str(quantity)), parsed_date)

    await db.commit()
    await db.refresh(holding)

    return _envelope({
        "id": holding.id,
        "company_id": company.id,
        "ticker": company.ticker,
        "company_name": company.name,
        "avg_purchase_price": str(holding.average_cost_basis),
        "quantity": float(holding.num_shares),
        "purchase_date": holding.purchase_date.isoformat() if holding.purchase_date else None,
        "holding_type": holding.holding_type,
        "num_shares": float(holding.num_shares),
    })


# ─── Bulk CSV ────────────────────────────────────────────────────────────────

@router.post("/bulk-csv", status_code=201)
async def bulk_csv_cost_basis(
    file: UploadFile = File(...),
    commit: bool = Form(False),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
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
    if not reader.fieldnames:
        raise HTTPException(status_code=422, detail="CSV file appears to be empty")

    normalised_headers = [h.strip().lower() for h in reader.fieldnames]
    required = {"ticker", "avg_purchase_price", "quantity", "purchase_date"}
    missing = required - set(normalised_headers)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV missing required columns: {', '.join(sorted(missing))}"
        )

    def normalise_row(row: dict) -> dict:
        return {k.strip().lower(): (v or "").strip() for k, v in row.items()}

    valid_rows = []
    error_rows = []

    for i, raw_row in enumerate(reader, start=2):
        row = normalise_row(raw_row)
        ticker = row.get("ticker", "").upper()
        company_name = row.get("company_name", "")
        price_str = row.get("avg_purchase_price", "")
        qty_str = row.get("quantity", "")
        date_str = row.get("purchase_date", "")
        errors = []

        price = None
        try:
            price = Decimal(price_str)
            if price <= 0:
                errors.append("Price must be positive")
        except InvalidOperation:
            errors.append(f"Invalid price '{price_str}'")

        quantity = None
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                errors.append("Quantity must be positive")
        except (ValueError, TypeError):
            errors.append(f"Invalid quantity '{qty_str}'")

        parsed_date = None
        if date_str:
            try:
                parsed_date = date_type.fromisoformat(date_str)
            except (ValueError, TypeError):
                errors.append(f"Invalid date '{date_str}'")

        if errors:
            error_rows.append({
                "row": i,
                "ticker": ticker,
                "company_name": company_name,
                "errors": errors,
            })
        else:
            valid_rows.append({
                "row": i,
                "ticker": ticker,
                "company_name": company_name,
                "price": price,
                "quantity": Decimal(str(quantity)),
                "date": parsed_date,
            })

    if not commit:
        preview = valid_rows[:10]
        resolved = []
        for r in preview:
            company = await _resolve_company(db, r["ticker"], r["company_name"])
            resolved.append({
                "ticker": company.ticker,
                "company_name": company.name,
                "avg_purchase_price": str(r["price"]),
                "quantity": float(r["quantity"]),
                "purchase_date": r["date"].isoformat() if r["date"] else None,
                "holding_type": "claim" if company.status in ("delisted", "defunct") else "active",
            })

        return _envelope({
            "valid": len(valid_rows),
            "errors": len(error_rows),
            "error_rows": error_rows,
            "preview_rows": resolved,
            "committed": False,
        })

    active_holdings = 0
    claims_created = 0
    new_companies = 0
    commit_errors = []

    for r in valid_rows:
        try:
            company = await _resolve_company(db, r["ticker"], r["company_name"])
            if company.id is None:
                new_companies += 1
            holding = await _create_holding(db, company, r["price"], r["quantity"], r["date"])
            if holding.holding_type == "claim":
                claims_created += 1
            else:
                active_holdings += 1
        except Exception as e:
            commit_errors.append({
                "row": r["row"],
                "ticker": r["ticker"],
                "error": str(e),
            })

    await db.commit()

    return _envelope({
        "summary": {
            "total": len(valid_rows),
            "active_holdings_created": active_holdings,
            "claims_created": claims_created,
            "new_companies_created": new_companies,
            "errors": commit_errors,
        }
    })


# ─── List ────────────────────────────────────────────────────────────────────

@router.get("")
async def list_cost_basis(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(Holding)
        .options(selectinload(Holding.company))
        .where(Holding.deleted_at.is_(None))
        .order_by(desc(Holding.created_at))
        .limit(100)
    )
    holdings = result.scalars().all()

    return _envelope([
        {
            "id": h.id,
            "company_id": h.company_id,
            "ticker": h.company.ticker if h.company else None,
            "company_name": h.company.name if h.company else None,
            "avg_purchase_price": str(h.average_cost_basis),
            "quantity": float(h.num_shares),
            "purchase_date": h.purchase_date.isoformat() if h.purchase_date else None,
            "holding_type": h.holding_type,
            "num_shares": float(h.num_shares),
            "total_cost": str(h.total_cost),
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in holdings
    ])


# ─── Template ────────────────────────────────────────────────────────────────

@router.get("/download-template")
async def download_cost_basis_template(
    current_user: User = Depends(require_admin),
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ticker", "company_name", "avg_purchase_price", "quantity", "purchase_date"])
    writer.writerow(["DANGCEM", "Dangote Cement Plc", "245.50", "500", "2024-01-15"])
    writer.writerow(["GTCO", "Guaranty Trust Holding Co", "33.20", "1000", "2024-03-01"])

    from fastapi.responses import StreamingResponse

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cost_basis_template.csv"},
    )
