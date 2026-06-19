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

from app.schemas.auth import LoginRequest
from app.schemas.holdings import HoldingCreate
from app.schemas.prices import PriceQuickEntry
from app.schemas.transactions import TransactionCreate
from app.schemas.dashboard import DashboardResponse


# ===========================================================================
# 1A.2 — Login Schema
# ===========================================================================

class TestLoginSchema:
    def test_login_schema_valid_input_passes(self):
        obj = LoginRequest(username="zubbyik", password="securepass")
        assert obj.username == "zubbyik"

    def test_login_schema_rejects_empty_username(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="", password="securepass")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("username",) for e in errors)

    def test_login_schema_rejects_empty_password(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(username="zubbyik", password="")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

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
            avg_purchase_price="45.50",
        )
        assert obj.num_shares == 100

    def test_holding_schema_rejects_negative_shares(self):
        with pytest.raises(ValidationError) as exc_info:
            HoldingCreate(
                company_id=1,
                num_shares=-10,
                avg_purchase_price="45.50",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("num_shares",) for e in errors)

    def test_holding_schema_rejects_zero_shares(self):
        with pytest.raises(ValidationError):
            HoldingCreate(
                company_id=1,
                num_shares=0,
                avg_purchase_price="45.50",
            )

    def test_holding_schema_rejects_negative_price(self):
        with pytest.raises(ValidationError) as exc_info:
            HoldingCreate(
                company_id=1,
                num_shares=100,
                avg_purchase_price="-10.00",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("avg_purchase_price",) for e in errors)

    def test_holding_schema_status_defaults_to_draft(self):
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price="45.50",
        )
        assert obj.status == "draft"

    def test_holding_schema_rejects_invalid_status(self):
        with pytest.raises(ValidationError):
            HoldingCreate(
                company_id=1,
                num_shares=100,
                avg_purchase_price="45.50",
                status="pending",  # invalid — only draft|live
            )


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
        assert obj.price == Decimal("123.45")

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
        assert obj.price == Decimal("100000.00")


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


class TestTransactionSchema:
    @pytest.mark.parametrize("tx_type", VALID_TRANSACTION_TYPES)
    def test_transaction_schema_accepts_all_valid_types(self, tx_type: str):
        obj = TransactionCreate(
            transaction_date=date.today(),
            ticker="DANGCEM",
            transaction_type=tx_type,
            num_shares=100,
            price_per_share="123.45",
            net_amount="12345.00",
            status="draft",
        )
        assert obj.transaction_type == tx_type

    def test_transaction_schema_rejects_unknown_type(self):
        with pytest.raises(ValidationError) as exc_info:
            TransactionCreate(
                transaction_date=date.today(),
                ticker="DANGCEM",
                transaction_type="swap",  # invalid
                num_shares=100,
                price_per_share="123.45",
                net_amount="12345.00",
                status="draft",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("transaction_type",) for e in errors)

    def test_transaction_schema_status_defaults_to_draft(self):
        obj = TransactionCreate(
            transaction_date=date.today(),
            ticker="GTCO",
            transaction_type="buy",
            num_shares=50,
            price_per_share="30.00",
            net_amount="1500.00",
        )
        assert obj.status == "draft"

    def test_transaction_schema_broker_fee_is_optional(self):
        obj = TransactionCreate(
            transaction_date=date.today(),
            ticker="GTCO",
            transaction_type="buy",
            num_shares=50,
            price_per_share="30.00",
            net_amount="1500.00",
        )
        assert obj.broker_fee is None


# ===========================================================================
# 1A.2 — Dashboard Response: monetary fields must be strings
# ===========================================================================

class TestDashboardResponseSchema:
    def test_dashboard_response_monetary_values_are_strings(self):
        """API spec: monetary values serialised as strings, not floats."""
        obj = DashboardResponse(
            total_portfolio_value="12345678.00",
            total_invested="11000000.00",
            unrealised_gain_loss="1345678.00",
            unrealised_gain_pct="+12.23",
            total_holdings=24,
            sector_allocation=[],
            top_holdings=[],
            recent_transactions=[],
            last_updated="2026-04-20T18:00:00Z",
        )
        assert isinstance(obj.total_portfolio_value, str)
        assert isinstance(obj.total_invested, str)
        assert isinstance(obj.unrealised_gain_loss, str)

    def test_dashboard_response_rejects_float_for_monetary_fields(self):
        """Floats must be rejected — precision loss risk."""
        with pytest.raises(ValidationError):
            DashboardResponse(
                total_portfolio_value=12345678.00,  # float — must fail
                total_invested="11000000.00",
                unrealised_gain_loss="1345678.00",
                unrealised_gain_pct="+12.23",
                total_holdings=24,
                sector_allocation=[],
                top_holdings=[],
                recent_transactions=[],
                last_updated="2026-04-20T18:00:00Z",
            )