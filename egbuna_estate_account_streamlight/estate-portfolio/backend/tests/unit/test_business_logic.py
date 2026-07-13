# backend/tests/unit/test_business_logic.py
"""
Stage 1A.3 — Business Logic Unit Tests
Tests current service/route code against known inputs.
No database, no network. Pure logic + mocked service calls.
"""
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.holdings import recalculate_holding_value
from app.services.portfolio import calculate_total_assets


# ===========================================================================
# 1A.3 — Value & Return Calculations (via recalculate_holding_value)
# ===========================================================================

class TestValueCalculations:
    def _make_holding(self, shares=100, avg_cost=Decimal("10.00"),
                      total_cost=Decimal("1000.00"), price=Decimal("15.00"),
                      holding_type="active", cost_override=None):
        h = MagicMock()
        h.num_shares = Decimal(str(shares))
        h.average_cost_basis = Decimal(str(avg_cost))
        h.total_cost = Decimal(str(total_cost))
        h.holding_type = holding_type
        h.cost_basis_override = cost_override
        h.company = MagicMock()
        h.company.current_price = Decimal(str(price)) if price is not None else None
        return h

    def test_current_value_calculation(self):
        """recalculate_holding_value computes shares × price correctly."""
        h = self._make_holding(shares=100, price=Decimal("50.00"))
        recalculate_holding_value(h)
        assert h.current_value == Decimal("5000.00")

    def test_current_value_zero_shares(self):
        """Zero shares → current_value = 0."""
        h = self._make_holding(shares=0, price=Decimal("50.00"))
        recalculate_holding_value(h)
        assert h.current_value == Decimal("0.00")

    def test_cost_basis_used_in_gain_calculation(self):
        """Gain = current_value - total_cost (which is shares × avg_cost_basis)."""
        h = self._make_holding(shares=100, avg_cost=Decimal("40.00"),
                               total_cost=Decimal("4000.00"), price=Decimal("50.00"))
        recalculate_holding_value(h)
        assert h.current_value == Decimal("5000.00")
        assert h.unrealized_gain_loss == Decimal("1000.00")  # 5000 - 4000

    def test_cost_basis_zero_shares(self):
        """Zero shares → total_cost = 0, gain = 0."""
        h = self._make_holding(shares=0, avg_cost=Decimal("40.00"),
                               total_cost=Decimal("0.00"), price=Decimal("50.00"))
        recalculate_holding_value(h)
        assert h.current_value == Decimal("0.00")
        assert h.unrealized_gain_loss == Decimal("0.00")


class TestReturnPercentage:
    def _make_holding(self, shares=100, avg_cost=Decimal("10.00"),
                      total_cost=Decimal("1000.00"), price=Decimal("15.00")):
        h = MagicMock()
        h.num_shares = Decimal(str(shares))
        h.average_cost_basis = Decimal(str(avg_cost))
        h.total_cost = Decimal(str(total_cost))
        h.holding_type = "active"
        h.cost_basis_override = None
        h.company = MagicMock()
        h.company.current_price = Decimal(str(price)) if price is not None else None
        return h

    def test_return_pct_positive_gain(self):
        """Gain = (current - cost), return_pct = gain / cost × 100."""
        h = self._make_holding(shares=100, avg_cost=Decimal("40.00"),
                               total_cost=Decimal("4000.00"), price=Decimal("50.00"))
        recalculate_holding_value(h)
        pct = float(h.unrealized_gain_loss / h.total_cost * 100)
        assert pct == pytest.approx(25.0, rel=1e-4)

    def test_return_pct_negative_loss(self):
        h = self._make_holding(shares=100, avg_cost=Decimal("40.00"),
                               total_cost=Decimal("4000.00"), price=Decimal("30.00"))
        recalculate_holding_value(h)
        pct = float(h.unrealized_gain_loss / h.total_cost * 100)
        assert pct == pytest.approx(-25.0, rel=1e-4)

    def test_return_pct_zero_gain(self):
        h = self._make_holding(shares=100, avg_cost=Decimal("40.00"),
                               total_cost=Decimal("4000.00"), price=Decimal("40.00"))
        recalculate_holding_value(h)
        assert h.unrealized_gain_loss == Decimal("0.00")

    def test_return_pct_zero_cost_basis_does_not_divide_by_zero(self):
        """Zero cost basis must not raise ZeroDivisionError."""
        h = self._make_holding(shares=100, avg_cost=Decimal("0"),
                               total_cost=Decimal("0"), price=Decimal("50.00"))
        recalculate_holding_value(h)
        if h.total_cost > 0:
            pct = float(h.unrealized_gain_loss / h.total_cost * 100)
        else:
            pct = 0.0
        assert pct == 0.0


# TestDividendYield moved to test_dividend_yield.py (isolated —
# calculate_dividend_yield import is intentionally broken pending separate decision)


# ===========================================================================
# 1A.3 — Portfolio Totals (via calculate_total_assets)
# ===========================================================================

class TestPortfolioTotal:
    def test_portfolio_total_value_sums_active_holdings(self):
        holdings = [
            MagicMock(holding_type="active", current_value=Decimal("5000.00")),
            MagicMock(holding_type="active", current_value=Decimal("3000.00")),
            MagicMock(holding_type="draft", current_value=Decimal("2000.00")),
        ]
        result = calculate_total_assets(holdings, [])
        assert result["active_portfolio_value"] == "8000.00"

    def test_portfolio_total_excludes_draft_and_claim_holdings(self):
        holdings = [
            MagicMock(holding_type="draft", current_value=Decimal("1000")),
            MagicMock(holding_type="claim", current_value=Decimal("2000")),
        ]
        result = calculate_total_assets(holdings, [])
        assert result["active_portfolio_value"] == "0.00"

    def test_portfolio_total_empty_holdings(self):
        result = calculate_total_assets([], [])
        assert result["active_portfolio_value"] == "0.00"
        assert result["claims_portfolio_value"] == "0.00"
        assert result["total_assets"] == "0.00"
