"""
Unit tests for Holdings Recalculation Service.
Tests recalculate_holding_value and recalculate_all_holdings functions.
"""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.holdings import recalculate_holding_value, recalculate_all_holdings, recalculate_holdings_from_db


class TestRecalculateHoldingValue:
    """Tests for recalculate_holding_value function."""

    def test_recalculate_with_valid_price(self):
        """Test recalculation with valid company price."""
        holding = MagicMock()
        holding.num_shares = Decimal("100")
        holding.average_cost_basis = Decimal("10.00")
        holding.total_cost = Decimal("1000.00")
        holding.holding_type = "active"
        holding.cost_basis_override = None
        holding.company = MagicMock()
        holding.company.current_price = Decimal("15.00")
        
        recalculate_holding_value(holding)
        
        assert holding.current_value == Decimal("1500.00")
        assert holding.unrealized_gain_loss == Decimal("500.00")

    def test_recalculate_with_none_price(self):
        """Test recalculation when company price is None."""
        holding = MagicMock()
        holding.num_shares = Decimal("100")
        holding.average_cost_basis = Decimal("10.00")
        holding.total_cost = Decimal("1000.00")
        holding.holding_type = "active"
        holding.company = MagicMock()
        holding.company.current_price = None
        
        recalculate_holding_value(holding)
        
        assert holding.current_value is None
        assert holding.unrealized_gain_loss is None

    def test_recalculate_claim_with_cost_basis_override(self):
        """Test recalculation for claim holding with cost_basis_override."""
        holding = MagicMock()
        holding.num_shares = Decimal("100")
        holding.average_cost_basis = Decimal("10.00")
        holding.total_cost = Decimal("1000.00")
        holding.holding_type = "claim"
        holding.cost_basis_override = Decimal("800.00")
        holding.company = MagicMock()
        holding.company.current_price = Decimal("15.00")
        
        recalculate_holding_value(holding)
        
        # effective cost should use cost_basis_override for claims
        assert holding.current_value == Decimal("1500.00")
        assert holding.unrealized_gain_loss == Decimal("700.00")  # 1500 - 800

    def test_recalculate_with_missing_company(self):
        """Test recalculation when holding has no company."""
        holding = MagicMock()
        holding.num_shares = Decimal("100")
        holding.average_cost_basis = Decimal("10.00")
        holding.total_cost = Decimal("1000.00")
        holding.holding_type = "active"
        holding.company = None
        
        recalculate_holding_value(holding)
        
        assert holding.current_value is None
        assert holding.unrealized_gain_loss is None


class TestRecalculateAllHoldings:
    """Tests for recalculate_all_holdings function."""

    def test_processes_only_active_holdings(self):
        """Test that only active holdings are processed."""
        active1 = MagicMock()
        active1.holding_type = "active"
        active1.company = MagicMock()
        active1.company.current_price = Decimal("20.00")
        active1.num_shares = Decimal("100")
        active1.average_cost_basis = Decimal("10.00")
        active1.total_cost = Decimal("1000.00")
        active1.holding_type = "active"
        active1.cost_basis_override = None
        
        active2 = MagicMock()
        active2.holding_type = "active"
        active2.company = MagicMock()
        active2.company.current_price = Decimal("30.00")
        active2.num_shares = Decimal("50")
        active2.average_cost_basis = Decimal("5.00")
        active2.total_cost = Decimal("250.00")
        active2.holding_type = "active"
        active2.cost_basis_override = None
        
        claim = MagicMock()
        claim.holding_type = "claim"
        claim.company = MagicMock()
        claim.company.current_price = Decimal("25.00")
        claim.num_shares = Decimal("100")
        claim.average_cost_basis = Decimal("10.00")
        claim.total_cost = Decimal("1000.00")
        claim.holding_type = "claim"
        claim.cost_basis_override = None
        
        draft = MagicMock()
        draft.holding_type = "draft"
        draft.company = MagicMock()
        draft.company.current_price = Decimal("15.00")
        draft.num_shares = Decimal("100")
        draft.average_cost_basis = Decimal("10.00")
        draft.total_cost = Decimal("1000.00")
        draft.holding_type = "draft"
        draft.cost_basis_override = None
        
        holdings = [active1, active2, claim, draft]
        updated = recalculate_all_holdings(holdings)
        
        assert updated == 2
        assert active1.current_value == Decimal("2000.00")
        assert active2.current_value == Decimal("1500.00")
        # claim and draft should not be updated
        assert claim.current_value is None or claim.current_value != Decimal("2500.00")
        assert draft.current_value is None or draft.current_value != Decimal("1500.00")

    def test_empty_list_returns_zero(self):
        """Test that empty list returns zero."""
        updated = recalculate_all_holdings([])
        assert updated == 0


class TestRecalculateHoldingsFromDB:
    """Tests for recalculate_holdings_from_db function."""

    @pytest.mark.asyncio
    async def test_recalculate_from_db_calls_service(self):
        """Test that recalculate_holdings_from_db queries DB and calls recalculate."""
        mock_session = AsyncMock()
        
        # Create mock holdings
        holding1 = MagicMock()
        holding1.holding_type = "active"
        holding1.company = MagicMock()
        holding1.company.current_price = Decimal("20.00")
        holding1.num_shares = Decimal("100")
        holding1.average_cost_basis = Decimal("10.00")
        holding1.total_cost = Decimal("1000.00")
        holding1.holding_type = "active"
        holding1.cost_basis_override = None
        
        # Fix the mock chain - execute returns awaitable that returns result
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [holding1]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        # execute is an async method that should return the mock_result
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        with patch("app.services.holdings.recalculate_all_holdings") as mock_recalc:
            mock_recalc.return_value = 1
            count = await recalculate_holdings_from_db(mock_session)
            
            assert count == 1
            mock_session.execute.assert_awaited_once()
            mock_recalc.assert_called_once_with([holding1])


# Run tests with: pytest tests/unit/test_holdings_service.py -v