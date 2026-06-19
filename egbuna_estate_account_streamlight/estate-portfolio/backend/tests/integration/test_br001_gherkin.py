# backend/tests/integration/test_br001_gherkin.py
"""
Generated from: BR001_GHERKIN_SPEC.md
Uncle Bob rule: These tests MUST fail before production code is written.
Run with: docker compose exec backend pytest tests/integration/test_br001_gherkin.py -v
All DB ops wrapped in rollback fixture — zero side effects on production schema.
"""
import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import date, timedelta
from httpx import AsyncClient


# ===========================================================================
# FEATURE: Portfolio Valuation (F-001)
# Covers: FR-1, FR-2, FR-5
# ===========================================================================

class TestPortfolioValuation:

    @pytest.mark.asyncio
    async def test_sc001_holding_value_computed_from_shares_and_price(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """
        Spec: portfolio_valuation.feature | SC-001
        Given DANGCEM has current_price 450.00 and I hold 100 shares at avg 400.00
        Then current_value == 45000.00, cost_basis == 40000.00, return_pct == +12.50
        """
        from app.models import Holding
        test_company.current_price = Decimal("450.00")
        holding = Holding(
            company_id=test_company.id,
            num_shares=100,
            avg_purchase_price=Decimal("400.00"),
            holding_type="active",
            status="live",
        )
        db_session.add(holding)
        await db_session.flush()

        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200

        data = response.json()["data"]
        h = next(h for h in data if h["id"] == holding.id)

        # Spec: portfolio_valuation.feature | SC-001 | Then current_value == 45000.00
        assert h["current_value"] == "45000.00"
        # Spec: portfolio_valuation.feature | SC-001 | And cost_basis == 40000.00
        assert h["cost_basis"] == "40000.00"
        # Spec: portfolio_valuation.feature | SC-001 | And return_pct == +12.50
        assert h["return_pct"] == "+12.50"

    @pytest.mark.asyncio
    async def test_sc002_claim_holding_has_zero_cost_basis(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """
        Spec: portfolio_valuation.feature | SC-002
        Given OLDMUTUAL has holding_type 'claim'
        Then cost_basis_override == 0.00 and return_pct is null
        """
        from app.models import Holding
        test_company.status = "defunct"
        holding = Holding(
            company_id=test_company.id,
            num_shares=500,
            avg_purchase_price=Decimal("5.00"),
            holding_type="claim",
            cost_basis_override=Decimal("0.00"),
            status="live",
        )
        db_session.add(holding)
        await db_session.flush()

        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200

        data = response.json()["data"]
        h = next(h for h in data if h["id"] == holding.id)

        # Spec: SC-002 | Then cost_basis_override == 0.00
        assert h["cost_basis_override"] == "0.00"
        # Spec: SC-002 | And return_pct is null (mathematically undefined)
        assert h["return_pct"] is None

    @pytest.mark.asyncio
    async def test_sc003_total_assets_includes_active_and_claims(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """
        Spec: portfolio_valuation.feature | SC-003
        Given active holding value 45000 and pending claim expected_payout 12000
        Then total_assets == 57000.00
        """
        from app.models import Holding, ClaimRecord
        test_company.current_price = Decimal("450.00")
        holding = Holding(
            company_id=test_company.id,
            num_shares=100,
            avg_purchase_price=Decimal("400.00"),
            holding_type="active",
            status="live",
        )
        db_session.add(holding)
        await db_session.flush()

        claim = ClaimRecord(
            holding_id=holding.id,
            claim_status="pending",
            expected_payout=Decimal("12000.00"),
        )
        db_session.add(claim)
        await db_session.flush()

        response = await admin_http_client.get("/api/v1/dashboard")
        assert response.status_code == 200

        data = response.json()["data"]
        # Spec: SC-003 | Then active_portfolio_value == 45000.00
        assert data["active_portfolio_value"] == "45000.00"
        # Spec: SC-003 | And claims_portfolio_value == 12000.00
        assert data["claims_portfolio_value"] == "12000.00"
        # Spec: SC-003 | And total_assets == 57000.00
        assert data["total_assets"] == "57000.00"

    @pytest.mark.asyncio
    async def test_sc004_paid_claim_uses_actual_payout_not_expected(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """
        Spec: portfolio_valuation.feature | SC-004
        Given paid claim with expected 12000 and actual 9500
        Then claims_portfolio_value == 9500.00 (not 12000.00)
        """
        from app.models import Holding, ClaimRecord
        holding = Holding(
            company_id=test_company.id,
            num_shares=100,
            avg_purchase_price=Decimal("5.00"),
            holding_type="claim",
            cost_basis_override=Decimal("0.00"),
            status="live",
        )
        db_session.add(holding)
        await db_session.flush()

        claim = ClaimRecord(
            holding_id=holding.id,
            claim_status="paid",
            expected_payout=Decimal("12000.00"),
            actual_payout=Decimal("9500.00"),
        )
        db_session.add(claim)
        await db_session.flush()

        response = await admin_http_client.get("/api/v1/dashboard")
        data = response.json()["data"]

        # Spec: SC-004 | Then claims_portfolio_value == 9500.00
        assert data["claims_portfolio_value"] == "9500.00"
        # Spec: SC-004 | And NOT 12000.00
        assert data["claims_portfolio_value"] != "12000.00"

    @pytest.mark.asyncio
    async def test_sc005_monetary_values_are_strings_not_floats(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        """
        Spec: portfolio_valuation.feature | SC-005
        Then all monetary fields in holdings response are JSON strings
        """
        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200

        raw = response.text
        data = response.json()["data"]

        for holding in data:
            for field in ("current_value", "cost_basis", "avg_purchase_price", "current_price"):
                if field in holding and holding[field] is not None:
                    # Spec: SC-005 | Then monetary field is a JSON string not a number
                    assert isinstance(holding[field], str), (
                        f"Field '{field}' must be string, got {type(holding[field]).__name__}"
                    )

    @pytest.mark.parametrize("filter_type,expected_type", [
        ("active", "active"),
        ("claim", "claim"),
    ])
    @pytest.mark.asyncio
    async def test_sc006_holdings_filtered_by_holding_type(
        self, admin_http_client: AsyncClient,
        test_live_holding, test_draft_holding,
        filter_type, expected_type
    ):
        """
        Spec: portfolio_valuation.feature | SC-006 (Scenario Outline)
        When GET /api/v1/holdings?holding_type=<filter>
        Then all returned holdings have that holding_type
        """
        response = await admin_http_client.get(
            f"/api/v1/holdings?holding_type={filter_type}"
        )
        assert response.status_code == 200

        data = response.json()["data"]
        # Spec: SC-006 | Then only holdings with matching holding_type returned
        for h in data:
            assert h["holding_type"] == expected_type


# ===========================================================================
# FEATURE: Price Data Entry (F-002)
# Covers: FR-9
# ===========================================================================

class TestPriceDataEntry:

    @pytest.mark.asyncio
    async def test_sc007_quick_price_entry_updates_price_and_writes_audit(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """
        Spec: price_entry.feature | SC-007
        When POST /api/v1/prices/quick with valid payload
        Then current_price updated and price_audit record created with source 'manual'
        """
        from sqlalchemy import select
        from app.models import PriceAudit

        test_company.current_price = Decimal("31.00")
        await db_session.flush()

        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={
                "company_id": test_company.id,
                "price": "32.50",
                "entry_date": str(date.today()),
            }
        )
        # Spec: SC-007 | Then response status 200
        assert response.status_code == 200

        await db_session.refresh(test_company)
        # Spec: SC-007 | And current_price updated in DB
        assert test_company.current_price == Decimal("32.50")

        result = await db_session.execute(
            select(PriceAudit).where(PriceAudit.company_id == test_company.id)
        )
        audit = result.scalar_one_or_none()
        # Spec: SC-007 | And price_audit record exists
        assert audit is not None
        # Spec: SC-007 | And old_price == 31.00
        assert audit.old_price == Decimal("31.00")
        # Spec: SC-007 | And new_price == 32.50
        assert audit.new_price == Decimal("32.50")
        # Spec: SC-007 | And source == 'manual'
        assert audit.source == "manual"

    @pytest.mark.asyncio
    async def test_sc008_quick_entry_rejects_future_date(
        self, admin_http_client: AsyncClient, test_company
    ):
        """Spec: price_entry.feature | SC-008"""
        tomorrow = str(date.today() + timedelta(days=1))
        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "32.50", "entry_date": tomorrow}
        )
        # Spec: SC-008 | Then response status 422
        assert response.status_code == 422
        # Spec: SC-008 | And error contains future date message
        assert "future" in response.text.lower()

    @pytest.mark.asyncio
    async def test_sc009_quick_entry_rejects_negative_price(
        self, admin_http_client: AsyncClient, test_company
    ):
        """Spec: price_entry.feature | SC-009"""
        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "-5.00", "entry_date": str(date.today())}
        )
        # Spec: SC-009 | Then response status 422
        assert response.status_code == 422
        assert "zero" in response.text.lower() or "positive" in response.text.lower()

    @pytest.mark.asyncio
    async def test_sc010_quick_entry_rejects_price_above_sanity_cap(
        self, admin_http_client: AsyncClient, test_company
    ):
        """Spec: price_entry.feature | SC-010"""
        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100001.00", "entry_date": str(date.today())}
        )
        # Spec: SC-010 | Then response status 422 with sanity cap message
        assert response.status_code == 422
        assert "100,000" in response.text or "sanity" in response.text.lower()

    @pytest.mark.asyncio
    async def test_sc012_pdf_upload_skips_unknown_tickers(
        self, admin_http_client: AsyncClient
    ):
        """Spec: price_entry.feature | SC-012"""
        import io
        fake_pdf_content = b"%PDF-1.4 fake content"
        files = {"file": ("ngx_daily.pdf", io.BytesIO(fake_pdf_content), "application/pdf")}
        response = await admin_http_client.post(
            "/api/v1/prices/upload-pdf", files=files
        )
        # Spec: SC-012 | Then no crash occurs (422 acceptable for unparseable PDF)
        assert response.status_code in (200, 422)

    @pytest.mark.asyncio
    async def test_sc013_price_revert_restores_previous_price(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """Spec: price_entry.feature | SC-013"""
        from app.models import PriceAudit

        test_company.current_price = Decimal("32.50")
        audit = PriceAudit(
            company_id=test_company.id,
            old_price=Decimal("31.00"),
            new_price=Decimal("32.50"),
            changed_at=date.today(),
            source="manual",
        )
        db_session.add(audit)
        await db_session.flush()

        response = await admin_http_client.post(
            f"/api/v1/prices/audit/{audit.id}/revert"
        )
        # Spec: SC-013 | Then response status 200
        assert response.status_code == 200

        await db_session.refresh(test_company)
        # Spec: SC-013 | And current_price restored to 31.00
        assert test_company.current_price == Decimal("31.00")

    @pytest.mark.asyncio
    async def test_sc014_readonly_cannot_update_prices(
        self, readonly_http_client: AsyncClient, test_company
    ):
        """Spec: price_entry.feature | SC-014"""
        response = await readonly_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "32.50", "entry_date": str(date.today())}
        )
        # Spec: SC-014 | Then response status 403
        assert response.status_code == 403


# ===========================================================================
# FEATURE: Authentication (F-003)
# Covers: NFR-4
# ===========================================================================

class TestAuthentication:

    @pytest.mark.asyncio
    async def test_sc015_login_sets_30_day_httponly_cookie(
        self, async_client: AsyncClient, test_admin_user
    ):
        """Spec: authentication.feature | SC-015"""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "testpass123"}
        )
        # Spec: SC-015 | Then response status 200
        assert response.status_code == 200

        set_cookie = response.headers.get("set-cookie", "")
        # Spec: SC-015 | And cookie named epm_token is set
        assert "epm_token" in response.cookies
        # Spec: SC-015 | And cookie has HttpOnly attribute
        assert "HttpOnly" in set_cookie
        # Spec: SC-015 | And cookie has SameSite=Strict
        assert "SameSite=Strict" in set_cookie or "samesite=strict" in set_cookie.lower()
        # Spec: SC-015 | And Max-Age == 2592000 (30 days)
        assert "Max-Age=2592000" in set_cookie or "max-age=2592000" in set_cookie.lower()

    @pytest.mark.asyncio
    async def test_sc016_invalid_credentials_return_401(
        self, async_client: AsyncClient, test_admin_user
    ):
        """Spec: authentication.feature | SC-016"""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "WRONGPASSWORD"}
        )
        # Spec: SC-016 | Then response status 401
        assert response.status_code == 401
        # Spec: SC-016 | And no cookie set
        assert "epm_token" not in response.cookies

    @pytest.mark.asyncio
    async def test_sc017_auth_me_returns_user_with_role(
        self, admin_http_client: AsyncClient, test_admin_user
    ):
        """Spec: authentication.feature | SC-017"""
        response = await admin_http_client.get("/api/v1/auth/me")
        assert response.status_code == 200

        data = response.json()["data"]
        # Spec: SC-017 | Then response contains role == 'admin'
        assert data["role"] == "admin"
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_sc018_logout_clears_cookie(
        self, async_client: AsyncClient, test_admin_user
    ):
        """Spec: authentication.feature | SC-018"""
        await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "testpass123"}
        )

        response = await async_client.post("/api/v1/auth/logout")
        # Spec: SC-018 | Then response status 200
        assert response.status_code == 200

        set_cookie = response.headers.get("set-cookie", "")
        # Spec: SC-018 | And epm_token cleared (Max-Age=0)
        assert "epm_token" in set_cookie
        assert "Max-Age=0" in set_cookie or "max-age=0" in set_cookie.lower()

    @pytest.mark.asyncio
    async def test_sc019_logout_idempotent_without_cookie(
        self, async_client: AsyncClient
    ):
        """Spec: authentication.feature | SC-019"""
        response = await async_client.post("/api/v1/auth/logout")
        # Spec: SC-019 | Then response status 200 even without cookie
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sc020_protected_route_requires_auth(
        self, async_client: AsyncClient
    ):
        """Spec: authentication.feature | SC-020"""
        response = await async_client.get("/api/v1/holdings")
        # Spec: SC-020 | Then response status 401
        assert response.status_code == 401


# ===========================================================================
# FEATURE: Dividend Tracking (F-004)
# Covers: FR-6
# ===========================================================================

class TestDividendTracking:

    @pytest.mark.asyncio
    async def test_sc021_dividend_stores_gross_net_and_wht(
        self, admin_http_client: AsyncClient, test_live_holding, db_session
    ):
        """Spec: dividend_tracking.feature | SC-021"""
        response = await admin_http_client.post(
            "/api/v1/dividends",
            json={
                "holding_id": test_live_holding.id,
                "gross_amount": "1000.00",
                "wht_rate": "0.10",
                "payment_date": str(date.today()),
                "dividend_type": "final",
            }
        )
        assert response.status_code == 201

        data = response.json()["data"]
        # Spec: SC-021 | Then gross_amount == 1000.00
        assert data["gross_amount"] == "1000.00"
        # Spec: SC-021 | And net_amount == 900.00
        assert data["net_amount"] == "900.00"
        # Spec: SC-021 | And withholding_tax == 100.00
        assert data["withholding_tax"] == "100.00"

    @pytest.mark.asyncio
    async def test_sc022_annual_summary_aggregates_by_year(
        self, admin_http_client: AsyncClient, test_live_holding, db_session
    ):
        """Spec: dividend_tracking.feature | SC-022"""
        from app.models import Dividend

        for i in range(3):
            db_session.add(Dividend(
                holding_id=test_live_holding.id,
                gross_amount=Decimal("1000.00"),
                net_amount=Decimal("900.00"),
                withholding_tax=Decimal("100.00"),
                payment_date=date(2025, i + 1, 15),
                dividend_type="interim",
                source="manual",
            ))
        await db_session.flush()

        response = await admin_http_client.get("/api/v1/dividends/summary")
        assert response.status_code == 200

        summary = response.json()["data"]
        row_2025 = next((r for r in summary if r["year"] == 2025), None)
        assert row_2025 is not None
        # Spec: SC-022 | Then gross_total == 3000.00 (3 × 1000)
        assert row_2025["gross_total"] == "3000.00"
        # Spec: SC-022 | And wht_total == 300.00
        assert row_2025["wht_total"] == "300.00"
        # Spec: SC-022 | And net_total == 2700.00
        assert row_2025["net_total"] == "2700.00"

    @pytest.mark.asyncio
    async def test_sc023_readonly_can_view_dividends_but_not_create(
        self, readonly_http_client: AsyncClient, test_live_holding
    ):
        """Spec: dividend_tracking.feature | SC-023"""
        # Spec: SC-023 | When GET /api/v1/dividends → 200
        get_response = await readonly_http_client.get("/api/v1/dividends")
        assert get_response.status_code == 200

        # Spec: SC-023 | When POST /api/v1/dividends → 403
        post_response = await readonly_http_client.post(
            "/api/v1/dividends",
            json={
                "holding_id": test_live_holding.id,
                "gross_amount": "1000.00",
                "wht_rate": "0.10",
                "payment_date": str(date.today()),
                "dividend_type": "final",
            }
        )
        assert post_response.status_code == 403

    @pytest.mark.asyncio
    async def test_sc024_wht_rate_configurable_per_dividend_entry(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        """Spec: dividend_tracking.feature | SC-024"""
        response = await admin_http_client.post(
            "/api/v1/dividends",
            json={
                "holding_id": test_live_holding.id,
                "gross_amount": "1000.00",
                "wht_rate": "0.075",
                "payment_date": str(date.today()),
                "dividend_type": "interim",
            }
        )
        assert response.status_code == 201

        data = response.json()["data"]
        # Spec: SC-024 | Then withholding_tax == 75.00 (7.5% of 1000)
        assert data["withholding_tax"] == "75.00"
        # Spec: SC-024 | And net_amount == 925.00
        assert data["net_amount"] == "925.00"
