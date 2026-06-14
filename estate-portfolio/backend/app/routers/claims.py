from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.deps import get_session, get_current_user, require_admin
from app.models import ClaimRecord
from pydantic import BaseModel
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

@router.get("")
async def get_claims(
    holding_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    authority: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    stmt = select(ClaimRecord).options(selectinload(ClaimRecord.holding)).where(ClaimRecord.deleted_at.is_(None))
    if holding_id:
        stmt = stmt.where(ClaimRecord.holding_id == holding_id)
    if status:
        stmt = stmt.where(ClaimRecord.claim_status == status)
    if authority:
        stmt = stmt.where(ClaimRecord.claim_authority == authority)
    
    result = await session.execute(stmt)
    return result.scalars().all()

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
