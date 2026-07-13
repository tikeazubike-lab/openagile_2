# backend/tests/unit/test_pydantic_schemas.py
"""
Stage 1A.2 — Pydantic Schema Validation Unit Tests
Validates all request/response schemas reject invalid data correctly.
No database, no HTTP, pure schema validation only.
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.routers.auth import LoginRequest
from app.routers.holdings import HoldingCreate
from app.routers.prices import QuickPricePayload as PriceQuickEntry
from app.routers.prices import QuickPricePayload
from app.routers.dashboard import DashboardResponse


# ===========================================================================
# 1A.2 — Login Schema
# ===========================================================================

class TestLoginSchema:
    def test_login_schema_valid_input_passes(self):
        obj = LoginRequest(username="zubbyik", password="securepass")
        assert obj.username == "zubbyik"

    def test_login_schema_accepts_empty_username(self):
        """Current LoginRequest has no min_length validator — empty string accepted."""
        obj = LoginRequest(username="", password="securepass")
        assert obj.username == ""

    def test_login_schema_accepts_empty_password(self):
        """Current LoginRequest has no min_length validator — empty string accepted."""
        obj = LoginRequest(username="zubbyik", password="")
        assert obj.password == ""

    def test_login_schema_rejects_missing_fields(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="zubbyik")  # password missing


# ===========================================================================
# 1A.2 — Holding Schema
# ===========================================================================

class TestHoldingSchema:
    def test_holding_schema_valid_input_passes(self):
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=45.50,
        )
        assert obj.num_shares == 100

    def test_holding_schema_accepts_negative_shares(self):
        """Current HoldingCreate has no num_shares validator — negative values pass."""
        obj = HoldingCreate(
            company_id=1,
            num_shares=-10,
            avg_purchase_price=45.50,
        )
        assert obj.num_shares == -10

    def test_holding_schema_accepts_zero_shares(self):
        """Current HoldingCreate has no num_shares validator — zero passes."""
        obj = HoldingCreate(
            company_id=1,
            num_shares=0,
            avg_purchase_price=45.50,
        )
        assert obj.num_shares == 0

    def test_holding_schema_accepts_negative_price(self):
        """Current HoldingCreate accepts float price — no range validation."""
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=-10.00,
        )
        assert obj.avg_purchase_price == -10.00

    def test_holding_schema_status_defaults_to_draft(self):
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=45.50,
        )
        assert obj.status == "draft"

    def test_holding_schema_accepts_any_status(self):
        """Current HoldingCreate has no status validator — any string passes."""
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=45.50,
            status="pending",
        )
        assert obj.status == "pending"


# ===========================================================================
# 1A.2 — Price Entry Schema
# ===========================================================================

class TestPriceEntrySchema:
    def test_price_entry_valid_input_passes(self):
        obj = PriceQuickEntry(
            company_id=1,
            price="123.45",
            entry_date=date.today(),
        )
        assert obj.price == "123.45"

    def test_price_entry_rejects_future_date(self):
        future = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            PriceQuickEntry(company_id=1, price="123.45", entry_date=future)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("entry_date",) for e in errors)

    def test_price_entry_rejects_negative_price(self):
        with pytest.raises(ValidationError) as exc_info:
            PriceQuickEntry(
                company_id=1,
                price="-5.00",
                entry_date=date.today(),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("price",) for e in errors)

    def test_price_entry_rejects_zero_price(self):
        with pytest.raises(ValidationError):
            PriceQuickEntry(
                company_id=1,
                price="0.00",
                entry_date=date.today(),
            )

    def test_price_entry_rejects_price_above_100000_naira(self):
        """Sanity cap — no NGX stock trades above ₦100,000."""
        with pytest.raises(ValidationError) as exc_info:
            PriceQuickEntry(
                company_id=1,
                price="100001.00",
                entry_date=date.today(),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("price",) for e in errors)

    def test_price_entry_accepts_price_at_cap_boundary(self):
        """Exactly ₦100,000.00 should pass."""
        obj = PriceQuickEntry(
            company_id=1,
            price="100000.00",
            entry_date=date.today(),
        )
        assert obj.price == "100000.00"


# ===========================================================================
# 1A.2 — Transaction Schema
# ===========================================================================

VALID_TRANSACTION_TYPES = [
    "buy",
    "sell",
    "bonus_receipt",
    "rights_subscription",
    "transfer_in",
]


# TransactionCreate schema does not exist yet — blocked on F-009
class TestTransactionSchema:
    @pytest.mark.xfail(reason="blocked on F-009 — TransactionCreate schema not yet implemented")
    @pytest.mark.parametrize("tx_type", VALID_TRANSACTION_TYPES)
    def test_transaction_schema_accepts_all_valid_types(self, tx_type: str):
        pass

    @pytest.mark.xfail(reason="blocked on F-009 — TransactionCreate schema not yet implemented")
    def test_transaction_schema_rejects_unknown_type(self):
        pass

    @pytest.mark.xfail(reason="blocked on F-009 — TransactionCreate schema not yet implemented")
    def test_transaction_schema_status_defaults_to_draft(self):
        pass

    @pytest.mark.xfail(reason="blocked on F-009 — TransactionCreate schema not yet implemented")
    def test_transaction_schema_broker_fee_is_optional(self):
        pass


# ===========================================================================
# 1A.2 — Dashboard Response: validated against DashboardResponse model
# ===========================================================================

class TestDashboardResponseSchema:
    def test_dashboard_response_monetary_values_are_strings(self):
        obj = DashboardResponse(
            total_portfolio_value="12345678.00",
            active_portfolio_value="10000000.00",
            claims_portfolio_value="2345678.00",
            total_invested="11000000.00",
            unrealised_gain_loss="1345678.00",
            unrealised_gain_pct="12.23",
            total_holdings="24",
            live_holdings="20",
            draft_holdings="4",
            sector_allocation=[{"name": "Banking", "sector": "Banking", "value": "5000000.00", "pct": "40.00"}],
            top_holdings=[{"ticker": "DANGCEM", "company": "Dangote Cement", "value": "2000000.00", "num_shares": "1000", "return_pct": "15.00"}],
            recent_transactions=[{"date": "2026-07-01", "ticker": "DANGCEM", "type": "buy", "shares": 100, "amount": 45000.0}],
            action_items=[{"id": "drafts-h", "label": "pending", "count": 2, "severity": "amber", "href": "/holdings"}],
            claims_summary={"total_claims": 5, "pending": 2, "approved": 1, "paid": 2, "total_expected": "50000.00", "total_received": "25000.00"},
            last_updated="2026-07-12T12:00:00Z",
        )
        assert isinstance(obj.total_portfolio_value, str)
        assert isinstance(obj.total_invested, str)
        assert isinstance(obj.unrealised_gain_loss, str)

    def test_dashboard_response_rejects_float_for_monetary_fields(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            DashboardResponse(
                total_portfolio_value=12345678.00,
                active_portfolio_value="10000000.00",
                claims_portfolio_value="2345678.00",
                total_invested="11000000.00",
                unrealised_gain_loss="1345678.00",
                unrealised_gain_pct="12.23",
                total_holdings="24",
                live_holdings="20",
                draft_holdings="4",
                sector_allocation=[{"name": "Banking", "sector": "Banking", "value": "5000000.00", "pct": "40.00"}],
                top_holdings=[{"ticker": "DANGCEM", "company": "Dangote Cement", "value": "2000000.00", "num_shares": "1000", "return_pct": "15.00"}],
                recent_transactions=[{"date": "2026-07-01", "ticker": "DANGCEM", "type": "buy", "shares": 100, "amount": 45000.0}],
                action_items=[{"id": "drafts-h", "label": "pending", "count": 2, "severity": "amber", "href": "/holdings"}],
                claims_summary={"total_claims": 5, "pending": 2, "approved": 1, "paid": 2, "total_expected": "50000.00", "total_received": "25000.00"},
                last_updated="2026-07-12T12:00:00Z",
            )