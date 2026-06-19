"""One-time script to populate current_value for all holdings."""
import sys
sys.path.insert(0, '/app')

import asyncio
from decimal import Decimal
from app.database import AsyncSessionLocal
from app.models import Holding, Company
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def fix():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Holding)
            .options(selectinload(Holding.company))
            .where(Holding.deleted_at.is_(None))
        )
        holdings = result.scalars().all()
        updated = 0
        for h in holdings:
            if h.holding_type == 'active' and h.company:
                price = h.company.current_price or Decimal('0')
                shares = h.num_shares or 0
                h.current_value = price * Decimal(str(shares))
                if h.current_value:
                    updated += 1
            elif h.holding_type == 'claim':
                h.current_value = Decimal('0.00')
                updated += 1
        await db.commit()
        print(f'Updated {updated} holdings')
        
        # Verify
        result = await db.execute(
            select(Holding)
            .options(selectinload(Holding.company))
            .where(Holding.deleted_at.is_(None))
        )
        holdings = result.scalars().all()
        for h in holdings[:5]:
            print(f'  id={h.id} type={h.holding_type} current_value={h.current_value}')

if __name__ == '__main__':
    asyncio.run(fix())
