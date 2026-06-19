"""
EPM — Dashboard router.
Phase 2B: DB queries and claims integration
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from decimal import Decimal
from datetime import datetime, timezone

from app.deps import get_current_user, get_session
from app.models import User, Holding, Transaction
from app.services.portfolio import calculate_total_assets

router = APIRouter(tags=["Dashboard"])

def _envelope(data: object) -> dict:
    return {"data": data, "meta": {}, "error": None}

@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Fetch all holdings for calculations
    result = await session.execute(
        select(Holding)
        .options(selectinload(Holding.company), selectinload(Holding.claim_records))
        .where(Holding.deleted_at.is_(None))
    )
    all_holdings = result.scalars().all()
    
    active_holdings = [h for h in all_holdings if h.holding_type == 'active']
    claim_holdings = [h for h in all_holdings if h.holding_type == 'claim']
    
    # Collect all claims
    claim_records = []
    for h in claim_holdings:
        claim_records.extend(h.claim_records)
        
    portfolio_totals = calculate_total_assets(active_holdings, claim_records)
    
    total_invested = Decimal("0.00")
    total_holdings = len(all_holdings)
    live_holdings = len(active_holdings)
    draft_holdings = len(claim_holdings)
    
    for h in all_holdings:
        total_invested += h.total_cost

    unrealised_gain_loss = Decimal(portfolio_totals["total_assets"]) - total_invested
    unrealised_gain_pct = float(unrealised_gain_loss / total_invested * 100) if total_invested > 0 else 0.0
    
    claims_summary = {
        "total_claims": len(claim_records),
        "pending": sum(1 for cr in claim_records if cr.claim_status == 'pending'),
        "approved": sum(1 for cr in claim_records if cr.claim_status == 'approved'),
        "paid": sum(1 for cr in claim_records if cr.claim_status == 'paid'),
        "total_expected": str(sum(cr.expected_payout for cr in claim_records if cr.expected_payout) or Decimal("0.00")),
        "total_received": str(sum(cr.actual_payout for cr in claim_records if cr.actual_payout) or Decimal("0.00")),
    }

    # Recent transactions
    tx_res = await session.execute(
        select(Transaction)
        .options(selectinload(Transaction.company))
        .where(Transaction.deleted_at.is_(None))
        .order_by(desc(Transaction.transaction_date))
        .limit(5)
    )
    recent_transactions = []
    for tx in tx_res.scalars().all():
        recent_transactions.append({
            "date": str(tx.transaction_date),
            "ticker": tx.company.ticker if tx.company else None,
            "type": tx.transaction_type,
            "shares": float(tx.num_shares) if tx.num_shares else 0.0,
            "amount": float(tx.net_amount) if tx.net_amount else 0.0,
        })
        
    action_items = []
    if draft_holdings > 0:
        action_items.append({"id": "drafts-h", "label": "holdings pending publish", "count": draft_holdings, "severity": "amber", "href": "/holdings"})

    # Compute Sector Allocation
    sector_sums = {}
    for h in active_holdings:
        sec = h.company.sector if h.company and h.company.sector else "Unknown"
        sector_sums[sec] = sector_sums.get(sec, 0.0) + float(h.current_value or 0)
            
    total_active_val = float(portfolio_totals["active_portfolio_value"])
    
    # Sort sector allocation largest to smallest by value
    sorted_sectors = sorted(sector_sums.items(), key=lambda x: x[1], reverse=True)
    
    sector_allocation = [
        {
            "name": sec,
            "sector": sec,
            "value": str(val),
            "pct": str(round(float(val / total_active_val * 100), 2)) if total_active_val > 0 else "0.00"
        }
        for sec, val in sorted_sectors
    ]

    # Compute Top Holdings
    # We will filter active holdings, sort them by current_value, take top 5.
    sorted_active = sorted(active_holdings, key=lambda h: float(h.current_value or 0), reverse=True)
    
    top_holdings = []
    for h in sorted_active[:5]:
        cost = float(h.total_cost or 0)
        val = float(h.current_value or 0)
        ret = ((val - cost) / cost * 100) if cost > 0 else 0.0
        top_holdings.append({
            "ticker": h.company.ticker if h.company else "N/A",
            "company": h.company.name if h.company else "Unknown",
            "value": str(val) if val else "0.00",
            "num_shares": str(h.num_shares) if h.num_shares else "0.0000",
            "return_pct": str(round(ret, 2))
        })

    response_data = {
        "total_portfolio_value": str(portfolio_totals["total_assets"]),
        "active_portfolio_value": str(portfolio_totals["active_portfolio_value"]),
        "claims_portfolio_value": str(portfolio_totals["claims_portfolio_value"]),
        "total_invested": str(total_invested),
        "unrealised_gain_loss": str(unrealised_gain_loss),
        "unrealised_gain_pct": str(round(unrealised_gain_pct, 2)),
        "total_holdings": str(total_holdings),
        "live_holdings": str(live_holdings),
        "draft_holdings": str(draft_holdings),
        "sector_allocation": sector_allocation,
        "top_holdings": top_holdings,
        "recent_transactions": recent_transactions,
        "action_items": action_items,
        "claims_summary": claims_summary,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    return _envelope(response_data)
