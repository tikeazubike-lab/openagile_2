"""
EPM — Holdings router.
Phase 2B: Replaced with real async DB queries.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import get_current_user, require_admin, get_session
from app.models import User, Holding

router = APIRouter(tags=["Holdings"])


def _envelope(data: object) -> dict:
    return {"data": data, "meta": {}, "error": None}


@router.get("/holdings")
async def list_holdings(
    holding_type: str = Query("all"),
    company_id: int | None = Query(None, description="Filter by company ID"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all holdings. Readonly users see only LIVE records.
    Admin users see all (LIVE + DRAFT).
    Phase 2B added active vs claim views.
    Phase 3C added company_id filter.
    """
    stmt = select(Holding).options(selectinload(Holding.company), selectinload(Holding.claim_records)).where(Holding.deleted_at.is_(None))
    
    if company_id is not None:
        stmt = stmt.where(Holding.company_id == company_id)
    
    if holding_type in ["active", "claim"]:
        stmt = stmt.where(Holding.holding_type == holding_type)
        
    if current_user.role != "admin":
        stmt = stmt.where(Holding.holding_type == "active")
        
    result = await session.execute(stmt)
    holdings = result.scalars().all()
    
    response_data = []
    for h in holdings:
        if h.holding_type == "claim" and h.cost_basis_override is not None:
            eff_cost = h.cost_basis_override
        else:
            eff_cost = h.num_shares * h.average_cost_basis
            
        if h.holding_type == "claim":
            return_pct = None
        else:
            if eff_cost > 0 and h.current_value is not None:
                return_pct = float(((h.current_value - eff_cost) / eff_cost) * 100)
            elif eff_cost > 0 and h.company and h.company.current_price is not None:
                calc_val = h.num_shares * h.company.current_price
                return_pct = float(((calc_val - eff_cost) / eff_cost) * 100)
            else:
                return_pct = 0.0
                
        claim_summary = None
        if h.holding_type == "claim":
            claims = h.claim_records
            if claims:
                latest = sorted(claims, key=lambda x: x.updated_at, reverse=True)[0]
                total_expected = sum(c.expected_payout for c in claims if c.expected_payout)
                total_actual = sum(c.actual_payout for c in claims if c.actual_payout)
                claim_summary = {
                    "claim_count": len(claims),
                    "latest_status": latest.claim_status,
                    "expected_payout": str(total_expected) if total_expected else None,
                    "actual_payout": str(total_actual) if total_actual else None
                }
            else:
                claim_summary = {
                    "claim_count": 0,
                    "latest_status": "pending",
                    "expected_payout": None,
                    "actual_payout": None
                }
                
        response_data.append({
            "id": h.id,
            "ticker": h.company.ticker if h.company else "",
            "company": h.company.name if h.company else "",
            "sector": h.company.sector if h.company else "",
            "shares": float(h.num_shares),
            "avg_cost": str(h.average_cost_basis),
            "curr_price": str(h.company.current_price) if h.company and h.company.current_price else None,
            "curr_value": str(h.current_value) if h.current_value else None,
            "cost_basis": str(h.total_cost) if h.total_cost else None,
            "div_yield": 0.0,

            "holding_type": h.holding_type,
            "cost_basis_override": str(h.cost_basis_override) if h.cost_basis_override is not None else None,
            "effective_cost_basis": str(eff_cost),
            "return_pct": return_pct,
            "claim_summary": claim_summary
        })

    return _envelope(response_data)


@router.post("/holdings/{holding_id}/publish")
async def publish_holding(
    holding_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Admin-only: publish a draft holding."""
    result = await session.execute(select(Holding).where(Holding.id == holding_id))
    h = result.scalar_one_or_none()
    if h:
        h.holding_type = "active"
        await session.commit()
    return _envelope({"id": holding_id, "holding_type": "active", "message": "Published"})


@router.delete("/holdings/{holding_id}")
async def soft_delete_holding(
    holding_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    from datetime import datetime, timezone
    """Admin-only: soft delete a holding."""
    result = await session.execute(select(Holding).where(Holding.id == holding_id))
    h = result.scalar_one_or_none()
    if h:
        h.deleted_at = datetime.now(timezone.utc)
        await session.commit()
    return _envelope({"id": holding_id, "message": "Deleted"})


from pydantic import BaseModel
from typing import Optional

class HoldingCreate(BaseModel):
    company_id: int
    num_shares: float
    avg_purchase_price: float
    holding_type: Optional[str] = "draft"
    status: Optional[str] = "draft"

@router.post("/holdings")
async def create_holding(
    payload: HoldingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    from sqlalchemy import select
    from fastapi import HTTPException
    
    # Check duplicate
    existing = await session.execute(
        select(Holding).where(Holding.company_id == payload.company_id, Holding.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A holding for this company already exists")
    
    from decimal import Decimal
    total_cost = Decimal(str(payload.num_shares)) * Decimal(str(payload.avg_purchase_price))
    new_holding = Holding(
        company_id=payload.company_id,
        num_shares=payload.num_shares,
        average_cost_basis=payload.avg_purchase_price,
        total_cost=total_cost,
        holding_type=payload.holding_type,
    )
    session.add(new_holding)
    await session.commit()
    await session.refresh(new_holding)
    
    return _envelope({
        "id": new_holding.id,
        "company_id": new_holding.company_id,
        "status": "draft",
        "holding_type": new_holding.holding_type,
        "shares": float(new_holding.num_shares)
    })

from decimal import Decimal, InvalidOperation
from typing import Optional
from pydantic import BaseModel, field_validator

class HoldingUpdate(BaseModel):
    num_shares: Optional[int] = None
    avg_purchase_price: Optional[str] = None
    holding_type: Optional[str] = None
    status: Optional[str] = None

    @field_validator("num_shares")
    @classmethod
    def validate_shares(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Shares must be greater than zero")
        return v

    @field_validator("avg_purchase_price")
    @classmethod
    def validate_avg_price(cls, v):
        if v is None:
            return v
        try:
            d = Decimal(v)
        except (InvalidOperation, TypeError):
            raise ValueError("Average cost must be a valid number")
        if d <= 0:
            raise ValueError("Average cost must be a positive number")
        return v


@router.patch("/holdings/{holding_id}")
async def update_holding(
    holding_id: int,
    payload: HoldingUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    from fastapi import HTTPException
    result = await session.execute(
        select(Holding)
        .where(Holding.id == holding_id)
        .where(Holding.deleted_at.is_(None))
    )
    h = result.scalar_one_or_none()
    if not h:
        raise HTTPException(status_code=404, detail="Holding not found")
        
    if payload.num_shares is not None:
        h.num_shares = payload.num_shares
    if payload.avg_purchase_price is not None:
        h.average_cost_basis = Decimal(payload.avg_purchase_price)
    if payload.holding_type is not None:
        h.holding_type = payload.holding_type
    if payload.status is not None:
        h.status = payload.status
        
    await session.commit()
    await session.refresh(h)
    
    return _envelope({
        "id": h.id,
        "shares": float(h.num_shares),
        "avg_purchase_price": str(h.average_cost_basis),
        "holding_type": h.holding_type,
        "status": h.status
    })
