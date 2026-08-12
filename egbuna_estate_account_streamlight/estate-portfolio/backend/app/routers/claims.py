from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.deps import get_session, get_current_user, require_admin
from app.models import ClaimRecord, Holding, Company, Registrar
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime, timezone
from decimal import Decimal

router = APIRouter(prefix="/api/v1/claims", tags=["Claims"])

class ClaimRecordCreate(BaseModel):
    holding_id: int
    claim_reference: Optional[str] = None
    claim_authority: Optional[str] = None
    claim_type: str = "liquidation"
    date_filed: Optional[date] = None
    date_acknowledged: Optional[date] = None
    deadline_date: Optional[date] = None
    claim_status: str = "pending"
    expected_payout: Optional[Decimal] = None
    actual_payout: Optional[Decimal] = None
    payout_date: Optional[date] = None
    notes: Optional[str] = None
    documents_reference: Optional[str] = None

class ClaimRecordUpdate(BaseModel):
    claim_reference: Optional[str] = None
    claim_authority: Optional[str] = None
    claim_type: Optional[str] = None
    date_filed: Optional[date] = None
    date_acknowledged: Optional[date] = None
    deadline_date: Optional[date] = None
    claim_status: Optional[str] = None
    expected_payout: Optional[Decimal] = None
    actual_payout: Optional[Decimal] = None
    payout_date: Optional[date] = None
    notes: Optional[str] = None
    documents_reference: Optional[str] = None


class HoldingBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    num_shares: Optional[Decimal]
    company_ticker: Optional[str]
    company_name: Optional[str]
    registrar_name: Optional[str]


class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    holding_id: int
    claim_reference: Optional[str]
    claim_authority: Optional[str]
    claim_type: str
    claim_status: str
    expected_payout: Optional[Decimal]
    actual_payout: Optional[Decimal]
    payout_date: Optional[date]
    notes: Optional[str]
    holding: Optional[HoldingBrief]


def _envelope(data: object) -> dict:
    return {"data": data, "meta": {}, "error": None}


@router.get("")
async def get_claims(
    holding_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    authority: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(ClaimRecord)
        .options(
            selectinload(ClaimRecord.holding)
            .selectinload(Holding.company)
            .selectinload(Company.registrar)
        )
        .where(ClaimRecord.deleted_at.is_(None))
    )
    if holding_id:
        stmt = stmt.where(ClaimRecord.holding_id == holding_id)
    if status:
        status_list = [s.strip() for s in status.split(",")]
        stmt = stmt.where(ClaimRecord.claim_status.in_(status_list))
    if authority:
        stmt = stmt.where(ClaimRecord.claim_authority == authority)

    result = await session.execute(stmt)
    records = result.scalars().all()

    response_data = []
    for c in records:
        holding = c.holding
        company = holding.company if holding else None
        response_data.append({
            "id": c.id,
            "holding_id": c.holding_id,
            "claim_reference": c.claim_reference,
            "claim_authority": c.claim_authority,
            "claim_type": c.claim_type,
            "claim_status": c.claim_status,
            "expected_payout": c.expected_payout,
            "actual_payout": c.actual_payout,
            "payout_date": c.payout_date,
            "notes": c.notes,
            "holding": {
                "id": holding.id if holding else None,
                "num_shares": holding.num_shares if holding else None,
                "company_ticker": company.ticker if company else None,
                "company_name": company.name if company else None,
                "registrar_name": company.registrar.name if company and company.registrar else None,
            } if holding else None,
        })

    return _envelope(response_data)

@router.post("")
async def create_claim(
    claim_in: ClaimRecordCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin)
):
    new_claim = ClaimRecord(**claim_in.model_dump())
    session.add(new_claim)
    await session.commit()
    await session.refresh(new_claim)
    return new_claim

@router.put("/{claim_id}")
async def update_claim(
    claim_id: int,
    claim_in: ClaimRecordUpdate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin)
):
    result = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id, ClaimRecord.deleted_at.is_(None)))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    update_data = claim_in.model_dump(exclude_unset=True)
    
    # Business rule: when claim_status -> 'paid', actual_payout must be provided
    new_status = update_data.get("claim_status", claim.claim_status)
    if new_status == "paid":
        actual = update_data.get("actual_payout", claim.actual_payout)
        if actual is None:
            raise HTTPException(status_code=400, detail="actual_payout must be provided when claim_status is 'paid'")

    for key, value in update_data.items():
        setattr(claim, key, value)

    await session.commit()
    await session.refresh(claim)
    return claim

@router.delete("/{claim_id}")
async def delete_claim(
    claim_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_admin)
):
    result = await session.execute(select(ClaimRecord).where(ClaimRecord.id == claim_id, ClaimRecord.deleted_at.is_(None)))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return {"message": "Claim deleted successfully"}
