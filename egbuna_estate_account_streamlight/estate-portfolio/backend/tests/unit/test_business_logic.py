# backend/tests/unit/test_business_logic.py
"""
Business logic unit tests against the current flat architecture.

Targets app/services/portfolio.py, which exposes a single entry point:
calculate_total_assets(active_holdings, claim_records). The legacy
Stage-1A calculator functions (calculate_cost_basis, calculate_return_pct,
calculate_dividend_yield, ...) were removed in the flat-models refactor and
no longer exist — this file tests what the portfolio service actually does.

NOTE: rewritten from the legacy "Stage 1A" version.
"""
from types import SimpleNamespace

from app.services.portfolio import calculate_total_assets


def _holding(value=None, price=None, holding_type="active"):
    """Build a lightweight stand-in for a Holding ORM row."""
    company = SimpleNamespace(current_price=price) if price is not None else None
    return SimpleNamespace(
        holding_type=holding_type,
        current_value=value,
        num_shares=100,
        company=company,
    )


def _claim(status, payout=None):
    """Build a lightweight stand-in for a ClaimRecord ORM row."""
    return SimpleNamespace(
        claim_status=status,
        actual_payout=payout,
        expected_payout=payout,
    )


class TestCalculateTotalAssets:
    def test_active_holdings_sum_current_value(self):
        holdings = [
            _holding(value="5000.00"),
            _holding(value="3000.00"),
        ]
        result = calculate_total_assets(holdings, [])
        assert result["active_portfolio_value"] == "8000.00"
        assert result["total_assets"] == "8000.00"

    def test_non_active_holdings_are_excluded(self):
        holdings = [
            _holding(value="5000.00", holding_type="active"),
            _holding(value="2000.00", holding_type="claim"),
            _holding(value="1000.00", holding_type="draft"),
        ]
        result = calculate_total_assets(holdings, [])
        assert result["active_portfolio_value"] == "5000.00"

    def test_active_holding_without_current_value_uses_company_price(self):
        """When current_value is None, shares × company.current_price is used."""
        holdings = [_holding(value=None, price="15.00")]
        result = calculate_total_assets(holdings, [])
        assert result["active_portfolio_value"] == "1500.00"

    def test_paid_claims_use_actual_payout(self):
        claims = [_claim(status="paid", payout="1000.00")]
        result = calculate_total_assets([], claims)
        assert result["claims_portfolio_value"] == "1000.00"

    def test_approved_pending_claims_use_expected_payout(self):
        claims = [
            _claim(status="approved", payout="500.00"),
            _claim(status="pending", payout="250.00"),
            _claim(status="partially_paid", payout="125.00"),
        ]
        result = calculate_total_assets([], claims)
        assert result["claims_portfolio_value"] == "875.00"

    def test_total_assets_sums_active_and_claims(self):
        holdings = [_holding(value="8000.00")]
        claims = [_claim(status="paid", payout="2000.00")]
        result = calculate_total_assets(holdings, claims)
        assert result["active_portfolio_value"] == "8000.00"
        assert result["claims_portfolio_value"] == "2000.00"
        assert result["total_assets"] == "10000.00"

    def test_empty_inputs_produce_zero_values(self):
        result = calculate_total_assets([], [])
        assert result["active_portfolio_value"] == "0.00"
        assert result["claims_portfolio_value"] == "0.00"
        assert result["total_assets"] == "0.00"

    def test_unpaid_pending_claim_without_payout_is_zero(self):
        claims = [_claim(status="pending", payout=None)]
        result = calculate_total_assets([], claims)
        assert result["claims_portfolio_value"] == "0.00"