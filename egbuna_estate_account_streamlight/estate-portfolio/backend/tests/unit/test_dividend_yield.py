# backend/tests/unit/test_dividend_yield.py
"""
Deferred — blocked on BUG-HOLD-DIVYIELD-001.
Dividend yield calc not implemented, no dividend history data model exists yet.
"""
from decimal import Decimal

import pytest

# Import is intentionally broken — function not yet implemented.
# Catch at module level so the file can collect; tests are xfailed below.
try:
    from app.services.portfolio import calculate_dividend_yield
    _IMPORT_OK = True
except ImportError:
    calculate_dividend_yield = None
    _IMPORT_OK = False


pytestmark = pytest.mark.xfail(
    not _IMPORT_OK,
    reason="blocked on BUG-HOLD-DIVYIELD-001 — dividend yield calc not implemented, no dividend history data model exists yet",
    strict=False,
)


class TestDividendYield:
    def test_dividend_yield_calculation(self):
        if not _IMPORT_OK:
            pytest.xfail("blocked on BUG-HOLD-DIVYIELD-001")
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("5.00"),
            current_price=Decimal("100.00"),
        )
        assert result == pytest.approx(Decimal("5.00"), rel=1e-4)

    def test_dividend_yield_high_yield(self):
        if not _IMPORT_OK:
            pytest.xfail("blocked on BUG-HOLD-DIVYIELD-001")
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("15.00"),
            current_price=Decimal("100.00"),
        )
        assert result == pytest.approx(Decimal("15.00"), rel=1e-4)

    def test_dividend_yield_zero_price_does_not_divide_by_zero(self):
        if not _IMPORT_OK:
            pytest.xfail("blocked on BUG-HOLD-DIVYIELD-001")
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("5.00"),
            current_price=Decimal("0.00"),
        )
        assert result == Decimal("0.00")

    def test_dividend_yield_zero_dividend(self):
        if not _IMPORT_OK:
            pytest.xfail("blocked on BUG-HOLD-DIVYIELD-001")
        result = calculate_dividend_yield(
            annual_dividend_per_share=Decimal("0.00"),
            current_price=Decimal("100.00"),
        )
        assert result == Decimal("0.00")
