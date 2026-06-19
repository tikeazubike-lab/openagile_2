from decimal import Decimal
from typing import TypedDict, Any

class PortfolioTotal(TypedDict):
    active_portfolio_value: str
    claims_portfolio_value: str
    total_assets: str

def calculate_total_assets(active_holdings: list[Any], claim_records: list[Any]) -> PortfolioTotal:
    """
    Active portfolio value: sum of (shares * current_price) for live, active holdings
    Claims value: sum of actual_payout (if paid) or expected_payout (if pending/approved/partially_paid)
                  for claim holdings that have a ClaimRecord

    Total assets = active_value + claims_value
    """
    active_value = Decimal("0.00")
    for h in active_holdings:
        # For simplicity, assuming current_value is populated on the holding object
        # Alternatively we can compute: h.num_shares * (h.company.current_price or 0)
        # We will use h.current_value if available, else compute from shares and price
        if h.holding_type == "active":
            if h.current_value is not None:
                active_value += Decimal(str(h.current_value))
            else:
                price = getattr(h.company, "current_price", Decimal("0.00")) or Decimal("0.00")
                active_value += Decimal(str(h.num_shares)) * Decimal(str(price))

    claims_value = Decimal("0.00")
    for cr in claim_records:
        if cr.claim_status == "paid" and cr.actual_payout is not None:
            claims_value += Decimal(str(cr.actual_payout))
        elif cr.claim_status in ("approved", "partially_paid", "pending") and cr.expected_payout is not None:
            claims_value += Decimal(str(cr.expected_payout))

    return {
        "active_portfolio_value": str(active_value),
        "claims_portfolio_value": str(claims_value),
        "total_assets": str(active_value + claims_value),
    }
