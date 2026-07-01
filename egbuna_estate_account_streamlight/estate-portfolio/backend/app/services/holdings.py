from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Holding


def recalculate_holding_value(holding: Holding) -> None:
    """Recalculate holding's current_value and unrealized_gain_loss from company's current price."""
    if holding.company and holding.company.current_price is not None:
        price = Decimal(str(holding.company.current_price))
        shares = Decimal(str(holding.num_shares))
        
        # For claims, use cost_basis_override if available, otherwise use total_cost
        if holding.holding_type == "claim" and holding.cost_basis_override is not None:
            cost = Decimal(str(holding.cost_basis_override))
        else:
            cost = Decimal(str(holding.total_cost))
        
        holding.current_value = shares * price
        holding.unrealized_gain_loss = (shares * price) - cost
    else:
        holding.current_value = None
        holding.unrealized_gain_loss = None


def recalculate_all_holdings(holdings) -> int:
    """Recalculate current_value and unrealized_gain_loss for all active holdings.
    Returns count of updated holdings.
    """
    updated = 0
    for holding in holdings:
        if holding.holding_type == "active":
            recalculate_holding_value(holding)
            updated += 1
    return updated


async def recalculate_holdings_from_db(session: AsyncSession) -> int:
    """Recalculate all active holdings from database."""
    result = await session.execute(
        select(Holding)
        .options(selectinload(Holding.company))
        .where(Holding.deleted_at.is_(None))
        .where(Holding.holding_type == "active")
    )
    holdings = result.scalars().all()
    return recalculate_all_holdings(holdings)