# backend/tests/unit/test_business_logic.py
"""
Stage 1A.3 — Business Logic Unit Tests
Tests portfolio.py service functions in complete isolation.
No database, no network, no FastAPI app needed.
"""
from decimal import Decimal

import pytest

from app.services.portfolio import (
    calculate_cost_basis,
    calculate_current_value,
    calculate_dividend_yield,
    calculate_portfolio_total,
    calculate_rebalancing_gap,
    calculate_return_pct,
    calculate_wht_deduction,
)


# ===========================================================================
# 1A.3 — Value & Return Calculations
# ===========================================================================

class TestValueCalculations:
    def test_current_value_calculation(self):
        result = calculate_current_value(shares=100, current_price=Decimal("50.00"))
        assert result == Decimal("5000.00")

    def test_current_value_zero_shares(self):
        result = calculate_current_value(shares=0, current_price=Decimal("50.00"))
        assert result == Decimal("0.00")

    def test_current_value_fractional_price(self):
        result = calculate_current_value(shares=200, current_price=Decimal("12.50"))
        assert result == Decimal("2500.00")

    def test_cost_basis_calculation(self):
        result = calculate_cost_basis(shares=100, avg_purchase_price=Decimal("40.00"))
        assert result == Decimal("4000.00")

    def test_cost_basis_zero_shares(self):
        result = calculate_cost_basis(shares=0, avg_purchase_price=Decimal("40.00"))
        assert result == Decimal("0.00")


class TestReturnPercentage:
    def test_return_pct_positive_gain(self):
        result = calculate_return_pct(
            current_value=Decimal("5000.00"),
            cost_basis=Decimal("4000.00"),
        )
        assert result == pytest.approx(Decimal("25.00"), rel=1e-4)

    def test_return_pct_negative_loss(self):
        result = calculate_return_pct(
            current_value=Decimal("3000.00"),
            cost_basis=Decimal("4000.00"),
        )
        assert result == pytest.approx(Decimal("-25.00"), rel=1e-4)

    def test_return_pct_zero_gain(self):
        result = calculate_return_pct(
            current_value=Decimal("4000.00"),
            cost_basis=Decimal("4000.00"),
        )
        assert result == Decimal("0.00")

    def test_return_pct_zero_cost_basis_does_not_divide_by_zero(self):
        """Zero cost basis (e.g. bonus shares) must return 0, not raise."""
        result = calculate_return_pct(
            current_value=Decimal("1000.00"),
            cost_basis=Decimal("0.00"),
        )
        assert result == Decimal("0.00")

    def test_return_pct_is_two_decimal_places(self):
        result = calculate_return_pct(
            current_value=Decimal("5000.00"),
            cost_basis=Decimal("4000.00"),
        )
        # Confirm it's a Decimal with 2dp precision at most
        assert isinstance(result, Decimal)


# ===========================================================================
# 1A.3 — Dividend Yield
# ===========================================================================

class TestDividendYield:
    def test_dividend_yield_calculation(self):
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("5.00"),
            current_price=Decimal("100.00"),
        )
        assert result == pytest.approx(Decimal("5.00"), rel=1e-4)

    def test_dividend_yield_high_yield(self):
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("15.00"),
            current_price=Decimal("100.00"),
        )
        assert result == pytest.approx(Decimal("15.00"), rel=1e-4)

    def test_dividend_yield_zero_price_does_not_divide_by_zero(self):
        """Zero current price must return 0, not raise ZeroDivisionError."""
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("5.00"),
            current_price=Decimal("0.00"),
        )
        assert result == Decimal("0.00")

    def test_dividend_yield_zero_dividend(self):
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("0.00"),
            current_price=Decimal("100.00"),
        )
        assert result == Decimal("0.00")


# ===========================================================================
# 1A.3 — Rebalancing Gap
# ===========================================================================

class TestRebalancingGap:
    def test_rebalancing_gap_overweight(self):
        result = calculate_rebalancing_gap(
            current_pct=Decimal("35.0"),
            target_pct=Decimal("30.0"),
        )
        assert result == pytest.approx(Decimal("5.0"), rel=1e-4)

    def test_rebalancing_gap_underweight(self):
        result = calculate_rebalancing_gap(
            current_pct=Decimal("18.0"),
            target_pct=Decimal("20.0"),
        )
        assert result == pytest.approx(Decimal("-2.0"), rel=1e-4)

    def test_rebalancing_on_target_within_tolerance(self):
        result = calculate_rebalancing_gap(
            current_pct=Decimal("30.1"),
            target_pct=Decimal("30.0"),
        )
        # Within ±0.5% tolerance — direction is "on_target"
        assert abs(result) <= Decimal("0.5")

    def test_rebalancing_gap_zero(self):
        result = calculate_rebalancing_gap(
            current_pct=Decimal("25.0"),
            target_pct=Decimal("25.0"),
        )
        assert result == Decimal("0.0")


# ===========================================================================
# 1A.3 — WHT Deduction
# ===========================================================================

class TestWHTDeduction:
    def test_wht_deduction_standard_10_percent(self):
        net, wht = calculate_wht_deduction(
            gross=Decimal("1000.00"),
            rate=Decimal("0.10"),
        )
        assert wht == Decimal("100.00")
        assert net == Decimal("900.00")

    def test_wht_deduction_zero_rate(self):
        net, wht = calculate_wht_deduction(
            gross=Decimal("1000.00"),
            rate=Decimal("0.00"),
        )
        assert wht == Decimal("0.00")
        assert net == Decimal("1000.00")

    def test_wht_deduction_custom_rate(self):
        net, wht = calculate_wht_deduction(
            gross=Decimal("500.00"),
            rate=Decimal("0.075"),
        )
        assert wht == pytest.approx(Decimal("37.50"), rel=1e-4)
        assert net == pytest.approx(Decimal("462.50"), rel=1e-4)


# ===========================================================================
# 1A.3 — Portfolio Totals (Draft/Live filtering)
# ===========================================================================

class TestPortfolioTotal:
    def _make_holding(self, value: str, status: str) -> dict:
        return {"current_value": Decimal(value), "status": status}

    def test_portfolio_total_value_sums_live_holdings_only(self):
        holdings = [
            self._make_holding("5000.00", "live"),
            self._make_holding("3000.00", "live"),
            self._make_holding("2000.00", "draft"),  # must be excluded
        ]
        result = calculate_portfolio_total(holdings)
        assert result["total_value"] == Decimal("8000.00")

    def test_portfolio_total_excludes_draft_holdings(self):
        holdings = [
            self._make_holding("1000.00", "draft"),
            self._make_holding("2000.00", "draft"),
        ]
        result = calculate_portfolio_total(holdings)
        assert result["total_value"] == Decimal("0.00")

    def test_portfolio_total_empty_holdings(self):
        result = calculate_portfolio_total([])
        assert result["total_value"] == Decimal("0.00")
        assert result["total_cost"] == Decimal("0.00")

    def test_portfolio_unrealised_gain_computed(self):
        holdings = [
            {
                "current_value": Decimal("5000.00"),
                "cost_basis": Decimal("4000.00"),
                "status": "live",
            }
        ]
        result = calculate_portfolio_total(holdings)
        assert result["unrealised_gain_loss"] == Decimal("1000.00")
