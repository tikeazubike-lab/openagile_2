import csv
import io
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.deps import get_session, get_current_user, require_admin
from app.models import Company, User, Registrar
from app.services.pdf_parser import parse_ngx_companies_pdf

router = APIRouter(prefix="/api/v1/companies", tags=["companies"])


def _envelope(data, meta=None):
    return {"data": data, "meta": meta if meta is not None else {}, "error": None}


@router.get("")
async def list_companies(
    status: str | None = Query(None, description="Filter by status: listed, delisted, defunct, etc."),
    search: str | None = Query(None, description="Search by ticker or company name (case-insensitive)"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Company)
        .options(selectinload(Company.registrar))
        .where(Company.deleted_at.is_(None))
    )

    if status:
        query = query.where(Company.status == status)

    if search:
        pattern = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Company.ticker).like(pattern),
                func.lower(Company.name).like(pattern),
            )
        )

    query = query.order_by(Company.ticker)
    result = await db.execute(query)
    companies = result.scalars().all()

    return _envelope(
        data=[
            {
                "id": c.id,
                "ticker": c.ticker,
                "name": c.name,
                "sector": c.sector,
                "status": c.status,
                "current_price": str(c.current_price) if c.current_price else None,
                "last_price_update": c.last_price_update.isoformat()
                    if c.last_price_update else None,
                "registrar_name": c.registrar.name if c.registrar else None,
            }
            for c in companies
        ],
        meta={"total": len(companies)},
    )


@router.post("/upload-pdf", status_code=201)
async def upload_companies_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files accepted")

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=422, detail="Empty file")

    extracted = parse_ngx_companies_pdf(content)

    if not extracted:
        raise HTTPException(
            status_code=422,
            detail="No company data found in PDF. Ensure this is an NGX Daily Official List PDF.",
        )

    # Pre-load existing companies by ticker
    result = await db.execute(
        select(Company).where(Company.deleted_at.is_(None))
    )
    existing_companies = result.scalars().all()
    companies_by_ticker = {c.ticker.upper(): c for c in existing_companies}

    inserted = 0
    updated = 0
    errors = []

    for entry in extracted:
        ticker = entry["ticker"].upper()
        company_name = entry["name"]
        sector = entry.get("sector")

        if not ticker or not company_name:
            errors.append(f"Skipped row: missing ticker or company name")
            continue

        existing = companies_by_ticker.get(ticker)

        if existing:
            changed = False
            if existing.name != company_name:
                existing.name = company_name
                changed = True
            if sector and existing.sector != sector:
                existing.sector = sector
                changed = True
            if changed:
                updated += 1
        else:
            company = Company(
                ticker=ticker,
                name=company_name,
                sector=sector,
                status="listed",
            )
            db.add(company)
            companies_by_ticker[ticker] = company
            inserted += 1

    await db.commit()

    return {
        "data": {
            "summary": {
                "total": len(extracted),
                "inserted": inserted,
                "updated": updated,
                "errors": errors,
            }
        },
        "meta": {},
        "error": None,
    }


@router.get("/download-template")
async def download_companies_template(
    current_user: User = Depends(require_admin),
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ticker", "company_name", "sector", "status"])
    writer.writerow(["DANGCEM", "Dangote Cement Plc", "Industrial Goods", "listed"])
    writer.writerow(["GTCO", "Guaranty Trust Holding Co", "Banking", "listed"])
    writer.writerow(["ZENITHBANK", "Zenith Bank Plc", "Banking", "listed"])

    from fastapi.responses import StreamingResponse

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=companies_template.csv"},
    )


@router.get("/{company_id}")
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Company)
        .options(selectinload(Company.registrar))
        .where(Company.id == company_id, Company.deleted_at.is_(None))
    )
    result = await db.execute(query)
    c = result.scalar_one_or_none()

    if not c:
        raise HTTPException(status_code=404, detail="Company not found")

    return _envelope(
        {
            "id": c.id,
            "ticker": c.ticker,
            "name": c.name,
            "sector": c.sector,
            "status": c.status,
            "current_price": str(c.current_price) if c.current_price else None,
            "last_price_update": c.last_price_update.isoformat()
                if c.last_price_update else None,
            "isin": c.isin,
            "market_cap": str(c.market_cap) if c.market_cap else None,
            "outstanding_shares": c.outstanding_shares,
            "date_listed": c.date_listed.isoformat() if c.date_listed else None,
            "registrar": {"id": c.registrar.id, "name": c.registrar.name}
                if c.registrar else None,
        }
    )
