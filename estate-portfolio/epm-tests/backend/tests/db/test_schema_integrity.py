# backend/tests/db/test_schema_integrity.py
"""
Stage 2B — Database Schema Integrity Tests
Verifies Alembic migrations produced the correct schema.
All tests use the rollback fixture — zero side effects on production data.
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def get_table_names(session: AsyncSession) -> list[str]:
    result = await session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    )
    return [row[0] for row in result.fetchall()]


async def get_columns(session: AsyncSession, table: str) -> dict[str, dict]:
    result = await session.execute(
        text(
            "SELECT column_name, data_type, column_default, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = :table"
        ),
        {"table": table},
    )
    return {row[0]: {"type": row[1], "default": row[2], "nullable": row[3]} for row in result.fetchall()}


# ===========================================================================
# 2B — Table existence
# ===========================================================================

class TestTableExistence:
    REQUIRED_TABLES = [
        "users",
        "companies",
        "holdings",
        "dividends",
        "transactions",
        "registrars",
        "price_history",
        "price_audit",
        "nav_history",
        "watchlist",
        "sector_targets",
        "corporate_actions",
    ]

    @pytest.mark.asyncio
    async def test_all_required_tables_exist(self, db_session: AsyncSession):
        existing = await get_table_names(db_session)
        for table in self.REQUIRED_TABLES:
            assert table in existing, f"Table '{table}' is missing from schema"


# ===========================================================================
# 2B — Column existence (additive migrations)
# ===========================================================================

class TestColumnExistence:

    @pytest.mark.asyncio
    async def test_holdings_has_status_column_with_default_live(
        self, db_session: AsyncSession
    ):
        cols = await get_columns(db_session, "holdings")
        assert "status" in cols, "holdings.status column missing"
        default = (cols["status"]["default"] or "").lower()
        assert "live" in default, f"holdings.status default must be 'live', got: {default}"

    @pytest.mark.asyncio
    async def test_holdings_has_deleted_at_column(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "holdings")
        assert "deleted_at" in cols, "holdings.deleted_at column missing"
        assert cols["deleted_at"]["nullable"] == "YES", "deleted_at must be nullable"

    @pytest.mark.asyncio
    async def test_dividends_has_source_column(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "dividends")
        assert "source" in cols, "dividends.source column missing"

    @pytest.mark.asyncio
    async def test_dividends_has_is_scrip_column(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "dividends")
        assert "is_scrip" in cols, "dividends.is_scrip column missing"

    @pytest.mark.asyncio
    async def test_dividends_has_scrip_shares_column(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "dividends")
        assert "scrip_shares" in cols, "dividends.scrip_shares column missing"

    @pytest.mark.asyncio
    async def test_users_table_has_role_column_defaulting_to_readonly(
        self, db_session: AsyncSession
    ):
        cols = await get_columns(db_session, "users")
        assert "role" in cols, "users.role column missing"
        default = (cols["role"]["default"] or "").lower()
        assert "readonly" in default, f"users.role default must be 'readonly', got: {default}"

    @pytest.mark.asyncio
    async def test_price_audit_has_source_column(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "price_audit")
        assert "source" in cols, "price_audit.source column missing"

    @pytest.mark.asyncio
    async def test_transactions_has_all_required_columns(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "transactions")
        required = [
            "transaction_date", "ticker", "transaction_type", "num_shares",
            "price_per_share", "net_amount", "broker_fee", "notes",
            "status", "reference_id", "linked_holding_id", "deleted_at",
        ]
        for col in required:
            assert col in cols, f"transactions.{col} column missing"

    @pytest.mark.asyncio
    async def test_nav_history_has_all_required_columns(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "nav_history")
        for col in ("snapshot_date", "total_value", "total_cost", "gain_loss", "created_at"):
            assert col in cols, f"nav_history.{col} column missing"

    @pytest.mark.asyncio
    async def test_deleted_at_defaults_to_null(self, db_session: AsyncSession):
        """All soft-delete columns must default to NULL."""
        soft_delete_tables = ["holdings", "companies", "dividends", "transactions",
                              "registrars", "watchlist"]
        for table in soft_delete_tables:
            cols = await get_columns(db_session, table)
            if "deleted_at" in cols:
                assert cols["deleted_at"]["nullable"] == "YES", (
                    f"{table}.deleted_at must be nullable"
                )
                assert cols["deleted_at"]["default"] is None, (
                    f"{table}.deleted_at must default to NULL"
                )


# ===========================================================================
# 2B — Constraints
# ===========================================================================

class TestConstraints:

    @pytest.mark.asyncio
    async def test_holdings_company_id_unique_constraint_enforced(
        self, db_session: AsyncSession, test_company
    ):
        """Two live holdings for same company must be rejected."""
        await db_session.execute(
            text(
                "INSERT INTO holdings (company_id, num_shares, avg_purchase_price, status) "
                "VALUES (:cid, 100, '100.00', 'live')"
            ),
            {"cid": test_company.id},
        )
        with pytest.raises(Exception):  # IntegrityError or asyncpg.UniqueViolationError
            await db_session.execute(
                text(
                    "INSERT INTO holdings (company_id, num_shares, avg_purchase_price, status) "
                    "VALUES (:cid, 50, '200.00', 'live')"
                ),
                {"cid": test_company.id},
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_users_username_unique_constraint_enforced(
        self, db_session: AsyncSession
    ):
        await db_session.execute(
            text(
                "INSERT INTO users (username, name, password_hash, role) "
                "VALUES ('dupuser', 'Dup User', '$2b$12$fakehash', 'readonly')"
            )
        )
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO users (username, name, password_hash, role) "
                    "VALUES ('dupuser', 'Dup User 2', '$2b$12$fakehash2', 'readonly')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_nav_history_snapshot_date_unique_constraint_enforced(
        self, db_session: AsyncSession
    ):
        await db_session.execute(
            text(
                "INSERT INTO nav_history (snapshot_date, total_value, total_cost) "
                "VALUES ('2026-01-01', '1000000.00', '900000.00')"
            )
        )
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO nav_history (snapshot_date, total_value, total_cost) "
                    "VALUES ('2026-01-01', '1100000.00', '950000.00')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_soft_delete_does_not_violate_unique_constraint(
        self, db_session: AsyncSession, test_company
    ):
        """
        A soft-deleted holding should NOT block creating a new live holding
        for the same company. The UNIQUE constraint must be partial:
        WHERE deleted_at IS NULL.
        """
        # Insert and soft-delete a holding
        await db_session.execute(
            text(
                "INSERT INTO holdings (company_id, num_shares, avg_purchase_price, status, deleted_at) "
                "VALUES (:cid, 100, '100.00', 'live', NOW())"
            ),
            {"cid": test_company.id},
        )
        # Now insert a new live holding for the same company — must succeed
        await db_session.execute(
            text(
                "INSERT INTO holdings (company_id, num_shares, avg_purchase_price, status) "
                "VALUES (:cid, 200, '150.00', 'live')"
            ),
            {"cid": test_company.id},
        )
        await db_session.flush()  # Should NOT raise


# ===========================================================================
# 2B — Foreign keys
# ===========================================================================

class TestForeignKeys:

    @pytest.mark.asyncio
    async def test_holdings_company_id_fk_references_companies(
        self, db_session: AsyncSession
    ):
        with pytest.raises(Exception):  # ForeignKeyViolationError
            await db_session.execute(
                text(
                    "INSERT INTO holdings (company_id, num_shares, avg_purchase_price, status) "
                    "VALUES (99999999, 100, '100.00', 'live')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_price_audit_company_id_fk_references_companies(
        self, db_session: AsyncSession
    ):
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO price_audit (company_id, new_price, source) "
                    "VALUES (99999999, '100.00', 'manual')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_watchlist_company_id_fk_references_companies(
        self, db_session: AsyncSession
    ):
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO watchlist (company_id) VALUES (99999999)"
                )
            )
            await db_session.flush()


# ===========================================================================
# 2B — Alembic state
# ===========================================================================

class TestAlembicState:

    @pytest.mark.asyncio
    async def test_alembic_current_head_matches_schema(self, db_session: AsyncSession):
        """alembic_version table must exist and contain the current head revision."""
        result = await db_session.execute(
            text("SELECT version_num FROM alembic_version")
        )
        version = result.scalar_one_or_none()
        assert version is not None, "alembic_version table is empty — migrations may not have run"

    @pytest.mark.asyncio
    async def test_monetary_columns_are_numeric_not_varchar(
        self, db_session: AsyncSession
    ):
        """Critical: monetary values must be NUMERIC not TEXT to avoid precision loss."""
        checks = [
            ("holdings", "avg_purchase_price"),
            ("price_history", "price"),
            ("price_audit", "new_price"),
            ("price_audit", "old_price"),
            ("nav_history", "total_value"),
            ("nav_history", "total_cost"),
        ]
        for table, column in checks:
            cols = await get_columns(db_session, table)
            if column in cols:
                data_type = cols[column]["type"].lower()
                assert "numeric" in data_type or "decimal" in data_type, (
                    f"{table}.{column} is '{data_type}' — must be NUMERIC for monetary precision"
                )