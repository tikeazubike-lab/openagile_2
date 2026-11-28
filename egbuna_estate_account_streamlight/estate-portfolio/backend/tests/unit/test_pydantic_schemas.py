# backend/tests/unit/test_pydantic_schemas.py
"""
Pydantic schema validation unit tests against the current flat architecture.

Schemas are defined inline in the routers (app/routers/auth.py,
app/routers/holdings.py, app/routers/prices.py) rather than in a separate
app/schemas package. No database, no HTTP — pure schema validation.

NOTE: rewritten from the legacy "Stage 1A" version, which imported
app.schemas.auth etc. (modules that never existed in this repo's tracked
history). TransactionCreate and DashboardResponse no longer exist as
schemas — dropped.
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.routers.auth import LoginRequest
from app.routers.holdings import HoldingCreate, HoldingUpdate
from app.routers.prices import QuickPricePayload


# ===========================================================================
# Login Schema (app/routers/auth.py)
# ===========================================================================

class TestLoginSchema:
    def test_login_schema_valid_input_passes(self):
        obj = LoginRequest(username="zubbyik", password="securepass")
        assert obj.username == "zubbyik"

    def test_login_schema_requires_password_field(self):
        """Empty strings are accepted by the schema; absence of a field is not."""
        with pytest.raises(ValidationError):
            LoginRequest(username="zubbyik")  # password missing

    def test_login_schema_requires_username_field(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="securepass")  # username missing


# ===========================================================================
# Holding Schema (app/routers/holdings.py)
# ===========================================================================

class TestHoldingSchema:
    def test_holding_schema_valid_input_passes(self):
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=45.50,
        )
        assert obj.num_shares == 100

    def test_holding_schema_status_defaults_to_draft(self):
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=45.50,
        )
        assert obj.status == "draft"
        assert obj.holding_type == "draft"

    def test_holding_schema_rejects_missing_company_id(self):
        with pytest.raises(ValidationError):
            HoldingCreate(num_shares=100, avg_purchase_price=45.50)

    def test_holding_schema_rejects_non_numeric_shares(self):
        with pytest.raises(ValidationError):
            HoldingCreate(company_id=1, num_shares="many", avg_purchase_price=45.50)

    def test_holding_schema_accepts_explicit_status(self):
        obj = HoldingCreate(
            company_id=1,
            num_shares=100,
            avg_purchase_price=45.50,
            status="live",
            holding_type="active",
        )
        assert obj.status == "live"
        assert obj.holding_type == "active"


class TestHoldingUpdateSchema:
    def test_holding_update_all_optional(self):
        obj = HoldingUpdate()
        assert obj.num_shares is None

    def test_holding_update_rejects_non_positive_shares(self):
        with pytest.raises(ValidationError) as exc_info:
            HoldingUpdate(num_shares=0)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("num_shares",) for e in errors)

    def test_holding_update_rejects_negative_avg_price(self):
        with pytest.raises(ValidationError) as exc_info:
            HoldingUpdate(avg_purchase_price="-10.00")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("avg_purchase_price",) for e in errors)


# ===========================================================================
# Price Entry Schema (app/routers/prices.py)
# ===========================================================================

class TestPriceEntrySchema:
    def test_price_entry_valid_input_passes(self):
        obj = QuickPricePayload(
            company_id=1,
            price="123.45",
            entry_date=date.today(),
        )
        assert obj.price == "123.45"
        assert obj.company_id == 1

    def test_price_entry_rejects_future_date(self):
        future = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            QuickPricePayload(company_id=1, price="123.45", entry_date=future)
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("entry_date",) for e in errors)

    def test_price_entry_rejects_negative_price(self):
        with pytest.raises(ValidationError) as exc_info:
            QuickPricePayload(
                company_id=1,
                price="-5.00",
                entry_date=date.today(),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("price",) for e in errors)

    def test_price_entry_rejects_zero_price(self):
        with pytest.raises(ValidationError):
            QuickPricePayload(
                company_id=1,
                price="0.00",
                entry_date=date.today(),
            )

    def test_price_entry_rejects_price_above_100000_naira(self):
        """Sanity cap — no NGX stock trades above ₦100,000."""
        with pytest.raises(ValidationError) as exc_info:
            QuickPricePayload(
                company_id=1,
                price="100001.00",
                entry_date=date.today(),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("price",) for e in errors)

    def test_price_entry_accepts_price_at_cap_boundary(self):
        """Exactly ₦100,000.00 should pass."""
        obj = QuickPricePayload(
            company_id=1,
            price="100000.00",
            entry_date=date.today(),
        )
        assert Decimal(obj.price) == Decimal("100000.00")

    def test_price_entry_rejects_non_numeric_price(self):
        with pytest.raises(ValidationError):
            QuickPricePayload(
                company_id=1,
                price="abc",
                entry_date=date.today(),
            )