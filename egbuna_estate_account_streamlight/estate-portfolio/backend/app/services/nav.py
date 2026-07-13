"""
EPM — NAV calculation service (F-007).

Computes total portfolio value at a given date by summing
(num_shares × carry-forward price) across all active holdings.
"""
import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select, func as sa_func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Holding, PriceHistory

logger = logging.getLogger(__name__)


class NavResult:
    total_value: Decimal
    total_cost: Decimal
    gain_loss: Decimal

    def __init__(self, total_value: Decimal, total_cost: Decimal, gain_loss: Decimal):
        self.total_value = total_value
        self.total_cost = total_cost
        self.gain_loss = gain_loss


async def calculate_nav(target_date: date, session: AsyncSession) -> NavResult:
    """
    Calculate NAV for a given date.

    1. Fetch all active, non-deleted holdings with their companies.
    2. For each holding, get the most recent close_price on or before target_date.
    3. Skip holdings where num_shares == 0.
    4. Skip holdings where no price exists at all for the company.
    5. Sum total_value, total_cost, derive gain_loss.
    """
    result = await session.execute(
        select(Holding)
        .options(selectinload(Holding.company))
        .where(Holding.deleted_at.is_(None))
        .where(Holding.holding_type == "active")
    )
    holdings = result.scalars().all()

    total_value = Decimal("0.0000")
    total_cost = Decimal("0.0000")

    for holding in holdings:
        shares = Decimal(str(holding.num_shares))
        if shares == Decimal("0"):
            continue

        cost = Decimal(str(holding.total_cost)) if holding.total_cost else Decimal("0.0000")
        total_cost += cost

        price = await _get_carry_forward_price(holding.company_id, target_date, session)

        if price is None:
            logger.warning(
                "No price found for company_id=%s on or before %s — skipping holding %s",
                holding.company_id, target_date, holding.id,
            )
            continue

        total_value += shares * price

    gain_loss = total_value - total_cost
    return NavResult(
        total_value=total_value,
        total_cost=total_cost,
        gain_loss=gain_loss,
    )


async def _get_carry_forward_price(
    company_id: int, target_date: date, session: AsyncSession,
) -> Decimal | None:
    """Get the most recent close_price on or before target_date for a company."""
    subq = (
        select(sa_func.max(PriceHistory.price_date))
        .where(PriceHistory.company_id == company_id)
        .where(PriceHistory.price_date <= target_date)
        .scalar_subquery()
    )
    result = await session.execute(
        select(PriceHistory.close_price)
        .where(PriceHistory.company_id == company_id)
        .where(PriceHistory.price_date == subq)
    )
    row = result.one_or_none()
    if row is None:
        return None
    return Decimal(str(row[0]))
