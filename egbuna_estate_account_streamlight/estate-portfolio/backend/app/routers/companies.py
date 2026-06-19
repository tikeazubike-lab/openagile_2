from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_session, get_current_user
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
