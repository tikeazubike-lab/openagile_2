# backend/tests/integration/test_schema_integrity.py
"""
Stage 2B — Database Schema Integrity Tests.

Verifies the epm_test schema (created from the ORM models) matches the
invariants the app actually depends on: required tables exist, key columns
exist with correct nullability/type, monetary columns are NUMERIC, and
critical constraints are enforced.

NOTE: rewritten from the legacy version, which asserted columns/tables
(holdings.status, dividends.is_scrip, price_audit, watchlist,
sector_targets, corporate_actions, transactions.ticker/broker_fee/status)
that were never implemented in the current schema — in production either.
"""
import pytest
from sqlalchemy import text
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
# Table existence
# ===========================================================================

class TestTableExistence:
    REQUIRED_TABLES = [
        "users",
        "companies",
        "registrars",
        "company_registrars",
        "registrar_requirements",
        "registrar_documents",
        "holdings",
        "claim_records",
        "transactions",
        "dividends",
        "price_history",
        "price_audits",
        "nav_history",
        "admin_audit",
        "reminder_log",
    ]

    @pytest.mark.asyncio
    async def test_all_required_tables_exist(self, db_session: AsyncSession):
        existing = await get_table_names(db_session)
        for table in self.REQUIRED_TABLES:
            assert table in existing, f"Table '{table}' is missing from schema"


# ===========================================================================
# Column existence
# ===========================================================================

class TestColumnExistence:

    @pytest.mark.asyncio
    async def test_holdings_has_holding_type_and_soft_delete(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "holdings")
        assert "holding_type" in cols, "holdings.holding_type column missing"
        assert "average_cost_basis" in cols, "holdings.average_cost_basis column missing"
        assert "deleted_at" in cols, "holdings.deleted_at column missing"
        assert cols["deleted_at"]["nullable"] == "YES", "holdings.deleted_at must be nullable"

    @pytest.mark.asyncio
    async def test_users_has_role_and_hashed_password(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "users")
        assert "role" in cols, "users.role column missing"
        assert "hashed_password" in cols, "users.hashed_password column missing"
        assert "is_active" in cols, "users.is_active column missing"

    @pytest.mark.asyncio
    async def test_dividends_has_source_column(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "dividends")
        assert "source" in cols, "dividends.source column missing"

    @pytest.mark.asyncio
    async def test_price_audits_has_source_and_prices(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "price_audits")
        assert "source" in cols, "price_audits.source column missing"
        assert "old_price" in cols, "price_audits.old_price column missing"
        assert "new_price" in cols, "price_audits.new_price column missing"

    @pytest.mark.asyncio
    async def test_transactions_has_all_required_columns(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "transactions")
        required = [
            "company_id", "transaction_type", "transaction_date",
            "num_shares", "price_per_share", "net_amount", "notes",
            "deleted_at",
        ]
        for col in required:
            assert col in cols, f"transactions.{col} column missing"

    @pytest.mark.asyncio
    async def test_nav_history_has_all_required_columns(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "nav_history")
        for col in ("snapshot_date", "total_value", "total_cost", "gain_loss", "created_at"):
            assert col in cols, f"nav_history.{col} column missing"

    @pytest.mark.asyncio
    async def test_reminder_log_columns(self, db_session: AsyncSession):
        cols = await get_columns(db_session, "reminder_log")
        for col in ("requirement_id", "reminder_type", "recipient_email", "delivery_status", "sent_at"):
            assert col in cols, f"reminder_log.{col} column missing"


# ===========================================================================
# Constraints
# ===========================================================================

class TestConstraints:

    @pytest.mark.asyncio
    async def test_users_username_unique_constraint_enforced(self, db_session: AsyncSession):
        await db_session.execute(
            text(
                "INSERT INTO users (username, name, hashed_password, role) "
                "VALUES ('dupuser', 'Dup User', '$2b$12$fakehash', 'readonly')"
            )
        )
        with pytest.raises(Exception):  # IntegrityError or asyncpg.UniqueViolationError
            await db_session.execute(
                text(
                    "INSERT INTO users (username, name, hashed_password, role) "
                    "VALUES ('dupuser', 'Dup User 2', '$2b$12$fakehash2', 'readonly')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_transactions_check_constraint_enforced(self, db_session: AsyncSession):
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO transactions (company_id, transaction_type, transaction_date) "
                    "VALUES (1, 'swap', CURRENT_DATE)"  # 'swap' not in allowed types
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_reminder_log_check_constraints_enforced(self, db_session: AsyncSession):
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO reminder_log (requirement_id, reminder_type, recipient_email, delivery_status) "
                    "VALUES (1, 'nonsense', 'x@y.com', 'bogus')"
                )
            )
            await db_session.flush()


# ===========================================================================
# Foreign keys
# ===========================================================================

class TestForeignKeys:

    @pytest.mark.asyncio
    async def test_holdings_company_id_fk_references_companies(self, db_session: AsyncSession):
        with pytest.raises(Exception):  # ForeignKeyViolationError
            await db_session.execute(
                text(
                    "INSERT INTO holdings (company_id, num_shares, average_cost_basis, total_cost, holding_type) "
                    "VALUES (99999999, 100, 100.00, 10000.00, 'active')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_price_audits_company_id_fk_references_companies(self, db_session: AsyncSession):
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO price_audits (company_id, new_price, source) "
                    "VALUES (99999999, 100.00, 'manual')"
                )
            )
            await db_session.flush()

    @pytest.mark.asyncio
    async def test_reminder_log_requirement_fk(self, db_session: AsyncSession):
        with pytest.raises(Exception):
            await db_session.execute(
                text(
                    "INSERT INTO reminder_log (requirement_id, reminder_type, recipient_email, delivery_status) "
                    "VALUES (99999999, 'upcoming', 'x@y.com', 'sent')"
                )
            )
            await db_session.flush()


# ===========================================================================
# Monetary type guard
# ===========================================================================

class TestMonetaryColumns:

    @pytest.mark.asyncio
    async def test_monetary_columns_are_numeric_not_varchar(self, db_session: AsyncSession):
        """Critical: monetary values must be NUMERIC not TEXT to avoid precision loss."""
        checks = [
            ("holdings", "average_cost_basis"),
            ("holdings", "total_cost"),
            ("price_history", "price"),
            ("price_audits", "new_price"),
            ("price_audits", "old_price"),
            ("nav_history", "total_value"),
            ("nav_history", "total_cost"),
            ("transactions", "price_per_share"),
            ("transactions", "net_amount"),
        ]
        for table, column in checks:
            cols = await get_columns(db_session, table)
            if column in cols:
                data_type = cols[column]["type"].lower()
                assert "numeric" in data_type or "decimal" in data_type, (
                    f"{table}.{column} is '{data_type}' — must be NUMERIC for monetary precision"
                )