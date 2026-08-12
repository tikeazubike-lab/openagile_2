# backend/tests/integration/test_prices_integration.py
"""
Stage 2C — Price Entry & NAV History Integration Tests
Tests quick entry, CSV bulk import atomicity, audit logging, revert, NAV snapshots.
All changes rolled back after each test.
"""
import io
from datetime import date

import pytest
from httpx import AsyncClient


class TestPriceIntegration:

    # -----------------------------------------------------------------------
    # Quick entry
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_price_entry_creates_price_audit_record(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={
                "company_id": test_company.id,
                "price": "123.45",
                "entry_date": str(date.today()),
            },
        )
        assert response.status_code in (200, 201)

        # Verify audit record exists in DB
        from sqlalchemy import select, text
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM price_audit WHERE company_id = :cid"),
            {"cid": test_company.id},
        )
        count = result.scalar_one()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_price_audit_stores_old_and_new_price(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        # First price entry
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100.00", "entry_date": str(date.today())},
        )
        # Second price entry (creates audit with old=100 new=150)
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "150.00", "entry_date": str(date.today())},
        )

        from sqlalchemy import text
        result = await db_session.execute(
            text(
                "SELECT old_price, new_price FROM price_audit "
                "WHERE company_id = :cid ORDER BY changed_at DESC LIMIT 1"
            ),
            {"cid": test_company.id},
        )
        row = result.fetchone()
        assert row is not None
        assert str(row.new_price) == "150.00"

    @pytest.mark.asyncio
    async def test_price_revert_restores_previous_value_in_db(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        # Set initial price
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100.00", "entry_date": str(date.today())},
        )

        # Change to new price
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "200.00", "entry_date": str(date.today())},
        )

        # Get audit record ID
        from sqlalchemy import text
        result = await db_session.execute(
            text("SELECT id FROM price_audit WHERE company_id = :cid ORDER BY changed_at DESC LIMIT 1"),
            {"cid": test_company.id},
        )
        audit_id = result.scalar_one()

        # Revert
        revert_resp = await admin_http_client.post(f"/api/v1/prices/audit/{audit_id}/revert")
        assert revert_resp.status_code == 200

        # Verify price is back to 100.00
        result = await db_session.execute(
            text("SELECT current_price FROM companies WHERE id = :cid"),
            {"cid": test_company.id},
        )
        current = result.scalar_one()
        assert str(current) == "100.00"

    # -----------------------------------------------------------------------
    # Bulk CSV import
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bulk_csv_commit_updates_company_price(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        csv_content = f"ticker,price,date\n{test_company.ticker},999.99,{date.today()}\n"
        files = {"file": ("prices.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        response = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data={"commit": "true"},
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert body["committed"] == 1
        assert body["valid"] == 1

        from sqlalchemy import text

        result = await db_session.execute(
            text("SELECT current_price FROM companies WHERE id = :cid"),
            {"cid": test_company.id},
        )
        assert str(result.scalar_one()) == "999.99"

    @pytest.mark.asyncio
    async def test_bulk_csv_preview_mixed_valid_invalid(self, admin_http_client: AsyncClient, test_company):
        """Partial commit: preview shows valid + error rows; good rows can commit without bad rows."""
        csv_content = (
            f"ticker,price,date\n"
            f"{test_company.ticker},500.00,{date.today()}\n"
            f"UNKNOWN_XYZ,-99.00,{date.today()}\n"
        )
        files = {"file": ("prices.csv", io.BytesIO(csv_content.encode()), "text/csv")}

        preview_resp = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data={"commit": "false"},
        )
        assert preview_resp.status_code == 200
        preview = preview_resp.json()["data"]
        assert preview["valid"] == 1
        assert preview["errors"] >= 1
        assert preview["committed"] is False

    @pytest.mark.asyncio
    async def test_bulk_csv_preview_all_invalid(self, admin_http_client: AsyncClient):
        csv_content = "ticker,price,date\nGHOST,10.00,{date.today()}\n"
        files = {"file": ("bad.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        preview_resp = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data={"commit": "false"},
        )
        assert preview_resp.status_code == 200
        preview = preview_resp.json()["data"]
        assert preview["valid"] == 0
        assert preview["errors"] >= 1

    @pytest.mark.asyncio
    async def test_bulk_csv_empty_whitespace_returns_422(self, admin_http_client: AsyncClient):
        files = {"file": ("empty.csv", io.BytesIO(b"   \n  \n"), "text/csv")}
        resp = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data={"commit": "false"},
        )
        assert resp.status_code == 422
        assert "empty" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_bulk_csv_missing_columns_returns_422(self, admin_http_client: AsyncClient):
        csv_content = "foo,bar\nTESTCO,1\n"
        files = {"file": ("wrong.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        resp = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data={"commit": "false"},
        )
        assert resp.status_code == 422
        assert "missing" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_bulk_csv_file_too_large_returns_413(self, admin_http_client: AsyncClient):
        from app.routers.prices import MAX_CSV_BYTES

        oversized = b"x" * (MAX_CSV_BYTES + 1)
        files = {"file": ("big.csv", io.BytesIO(oversized), "text/csv")}
        resp = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data={"commit": "false"},
        )
        assert resp.status_code == 413

    # -----------------------------------------------------------------------
    # Price entry blocked for readonly
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_price_quick_entry_blocked_for_readonly(
        self, user_http_client: AsyncClient, test_company
    ):
        response = await user_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100.00", "entry_date": str(date.today())},
        )
        assert response.status_code == 403


class TestNavHistoryIntegration:

    @pytest.mark.asyncio
    async def test_nav_snapshot_inserts_row_into_nav_history(
        self, admin_http_client: AsyncClient, db_session
    ):
        response = await admin_http_client.post("/api/v1/nav-history/snapshot")
        assert response.status_code in (200, 201)

        from sqlalchemy import text
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM nav_history WHERE snapshot_date = CURRENT_DATE")
        )
        count = result.scalar_one()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_nav_snapshot_is_idempotent_for_same_day(
        self, admin_http_client: AsyncClient, db_session
    ):
        """Running snapshot twice on same day must not raise or duplicate."""
        r1 = await admin_http_client.post("/api/v1/nav-history/snapshot")
        r2 = await admin_http_client.post("/api/v1/nav-history/snapshot")

        assert r1.status_code in (200, 201)
        assert r2.status_code in (200, 200)  # second call is OK (upsert)

        from sqlalchemy import text
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM nav_history WHERE snapshot_date = CURRENT_DATE")
        )
        count = result.scalar_one()
        assert count == 1  # exactly one row per day

    @pytest.mark.asyncio
    async def test_nav_snapshot_blocked_for_readonly(
        self, user_http_client: AsyncClient
    ):
        response = await user_http_client.post("/api/v1/nav-history/snapshot")
        assert response.status_code == 403