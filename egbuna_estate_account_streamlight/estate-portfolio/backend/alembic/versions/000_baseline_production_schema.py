"""Baseline: production schema snapshot

Revision ID: 000
Revises:
Create Date: 2026-07-25

This baseline migration captures the full production estate_portfolio schema
as it exists today — including tables that predate the Alembic migration
chain (init_db.sql era) and two legacy Owl-Alpha-era tables (audit_logs,
communication_logs) that have no current code references.

Purpose: make the migration chain reproducible from empty, closing the
disaster-recovery gap where init_db.sql was never committed to the repo.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _col_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    return column in {c["name"] for c in sa.inspect(conn).get_columns(table)}


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    return conn.dialect.has_table(conn, table)


def upgrade() -> None:
    # ── Trigger function ─────────────────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$;
    """)

    # ── users ────────────────────────────────────────────────────────────────
    if not _table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("username", sa.String(50), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("hashed_password", sa.String(255), nullable=False),
            sa.Column("role", sa.String(20), server_default="readonly", nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("username"),
        )
        op.create_index("ix_users_username", "users", ["username"], unique=True)

    # ── registrars ───────────────────────────────────────────────────────────
    if not _table_exists("registrars"):
        op.create_table(
            "registrars",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("email", sa.String(255), nullable=True),
            sa.Column("phone", sa.String(50), nullable=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("website", sa.String(255), nullable=True),
            sa.Column("response_rating", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(20), server_default="active"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("jurisdiction", sa.String(20), server_default="nigeria", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.CheckConstraint(
                "response_rating >= 1 AND response_rating <= 5",
                name="registrars_response_rating_check",
            ),
        )

    # ── companies ────────────────────────────────────────────────────────────
    if not _table_exists("companies"):
        op.create_table(
            "companies",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("ticker", sa.String(20), nullable=False),
            sa.Column("sector", sa.String(100), nullable=True),
            sa.Column("isin", sa.String(12), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="listed"),
            sa.Column("market_cap", sa.Numeric(20, 2), nullable=True),
            sa.Column("outstanding_shares", sa.BigInteger(), nullable=True),
            sa.Column("date_listed", sa.Date(), nullable=True),
            sa.Column("date_delisted", sa.Date(), nullable=True),
            sa.Column("registrar_id", sa.Integer(), nullable=True),
            sa.Column("current_price", sa.Numeric(10, 2), nullable=True),
            sa.Column("last_price_update", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("obsidian_slug", sa.String(255), nullable=True),
            sa.Column("obsidian_imported", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("security_type", sa.String(20), server_default="equity", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("ticker"),
            sa.UniqueConstraint("obsidian_slug"),
            sa.ForeignKeyConstraint(["registrar_id"], ["registrars.id"]),
            sa.CheckConstraint(
                "status IN ('listed','delisted','defunct','merged','uncertain','active','inactive')",
                name="companies_status_check",
            ),
        )
        op.create_index("ix_companies_ticker", "companies", ["ticker"], unique=True)
        op.create_index("idx_companies_status", "companies", ["status"])
        op.create_index("idx_companies_registrar", "companies", ["registrar_id"])

    # ── holdings ─────────────────────────────────────────────────────────────
    if not _table_exists("holdings"):
        op.create_table(
            "holdings",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("num_shares", sa.Numeric(15, 4), nullable=False),
            sa.Column("average_cost_basis", sa.Numeric(10, 2), nullable=False),
            sa.Column("total_cost", sa.Numeric(20, 2), nullable=False),
            sa.Column("current_value", sa.Numeric(20, 2), nullable=True),
            sa.Column("unrealized_gain_loss", sa.Numeric(20, 2), nullable=True),
            sa.Column("certificate_number", sa.String(100), nullable=True),
            sa.Column("allocation_notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("holding_type", sa.String(20), server_default="active", nullable=False),
            sa.Column("cost_basis_override", sa.Numeric(15, 2), nullable=True),
            sa.Column("obsidian_imported", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("obsidian_last_synced", sa.DateTime(timezone=True), nullable=True),
            sa.Column("purchase_date", sa.Date(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        )
        op.create_index("ix_holdings_company_id", "holdings", ["company_id"])
        op.create_index("idx_holdings_company", "holdings", ["company_id"])

    # ── transactions ─────────────────────────────────────────────────────────
    if not _table_exists("transactions"):
        op.create_table(
            "transactions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("holding_id", sa.Integer(), nullable=True),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("transaction_type", sa.String(20), nullable=False),
            sa.Column("transaction_date", sa.Date(), nullable=False),
            sa.Column("settlement_date", sa.Date(), nullable=True),
            sa.Column("num_shares", sa.Numeric(15, 4), nullable=True),
            sa.Column("price_per_share", sa.Numeric(10, 2), nullable=True),
            sa.Column("gross_amount", sa.Numeric(20, 2), nullable=True),
            sa.Column("fees", sa.Numeric(10, 2), server_default="0"),
            sa.Column("net_amount", sa.Numeric(20, 2), nullable=True),
            sa.Column("broker", sa.String(255), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["holding_id"], ["holdings.id"]),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.CheckConstraint(
                "transaction_type IN ('buy','sell','dividend','stock_split','bonus_issue','rights_issue')",
                name="chk_transaction_type",
            ),
        )
        op.create_index("ix_transactions_company_id", "transactions", ["company_id"])
        op.create_index("ix_transactions_transaction_date", "transactions", ["transaction_date"])
        op.create_index("idx_transactions_company", "transactions", ["company_id"])
        op.create_index("idx_transactions_date", "transactions", ["transaction_date"])
        op.create_index("idx_transactions_type", "transactions", ["transaction_type"])

    # ── dividends ────────────────────────────────────────────────────────────
    if not _table_exists("dividends"):
        op.create_table(
            "dividends",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("transaction_id", sa.Integer(), nullable=True),
            sa.Column("declaration_date", sa.Date(), nullable=True),
            sa.Column("ex_dividend_date", sa.Date(), nullable=True),
            sa.Column("payment_date", sa.Date(), nullable=True),
            sa.Column("amount_per_share", sa.Numeric(10, 4), nullable=False),
            sa.Column("shares_held", sa.Numeric(15, 4), nullable=True),
            sa.Column("gross_amount", sa.Numeric(20, 2), nullable=True),
            sa.Column("tax_withheld", sa.Numeric(20, 2), nullable=True),
            sa.Column("net_amount", sa.Numeric(20, 2), nullable=True),
            sa.Column("payment_method", sa.String(50), nullable=True),
            sa.Column("status", sa.String(20), server_default="declared"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.Column("dividend_type", sa.String(50), server_default="final", nullable=False),
            sa.Column("payment_status", sa.String(30), server_default="paid", nullable=False),
            sa.Column("source", sa.String(50), server_default="manual", nullable=False),
            sa.Column("obsidian_imported", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("holding_id", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
            sa.ForeignKeyConstraint(["holding_id"], ["holdings.id"]),
            sa.CheckConstraint(
                "status IN ('declared','pending','paid','cancelled')",
                name="chk_dividend_status",
            ),
        )
        op.create_index("ix_dividends_company_id", "dividends", ["company_id"])
        op.create_index("ix_dividends_payment_date", "dividends", ["payment_date"])
        op.create_index("idx_dividends_company", "dividends", ["company_id"])
        op.create_index("idx_dividends_payment_date", "dividends", ["payment_date"])

    # ── price_history ────────────────────────────────────────────────────────
    if not _table_exists("price_history"):
        op.create_table(
            "price_history",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("price_date", sa.Date(), nullable=False),
            sa.Column("open_price", sa.Numeric(10, 2), nullable=True),
            sa.Column("high_price", sa.Numeric(10, 2), nullable=True),
            sa.Column("low_price", sa.Numeric(10, 2), nullable=True),
            sa.Column("close_price", sa.Numeric(10, 2), nullable=False),
            sa.Column("volume", sa.BigInteger(), nullable=True),
            sa.Column("source", sa.String(50), server_default="ngx_scraper"),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("company_id", "price_date"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        )
        op.create_index(
            "idx_price_history_company_date",
            "price_history",
            ["company_id", sa.text("price_date DESC")],
        )

    # ── claim_records ────────────────────────────────────────────────────────
    if not _table_exists("claim_records"):
        op.create_table(
            "claim_records",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("holding_id", sa.Integer(), nullable=True),
            sa.Column("claim_reference", sa.String(100), nullable=True),
            sa.Column("claim_authority", sa.String(100), nullable=True),
            sa.Column("claim_type", sa.String(50), server_default="liquidation", nullable=False),
            sa.Column("date_filed", sa.Date(), nullable=True),
            sa.Column("date_acknowledged", sa.Date(), nullable=True),
            sa.Column("deadline_date", sa.Date(), nullable=True),
            sa.Column("claim_status", sa.String(30), server_default="pending", nullable=False),
            sa.Column("lifecycle_status", sa.String(12), server_default="unresolved", nullable=False),
            sa.Column("raw_company_name", sa.String(255), nullable=True),
            sa.Column("expected_payout", sa.Numeric(15, 2), nullable=True),
            sa.Column("actual_payout", sa.Numeric(15, 2), nullable=True),
            sa.Column("payout_date", sa.Date(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("documents_reference", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["holding_id"], ["holdings.id"], ondelete="CASCADE"),
            sa.CheckConstraint(
                "claim_status IN ('pending','approved','rejected','partially_paid','paid','lapsed')",
                name="chk_claim_status",
            ),
        )
        op.create_index("ix_claim_records_holding_id", "claim_records", ["holding_id"])
        op.create_index("ix_claim_records_claim_status", "claim_records", ["claim_status"])
        op.create_index("ix_claim_records_lifecycle_status", "claim_records", ["lifecycle_status"])

    # ── obsidian_sync_log ────────────────────────────────────────────────────
    if not _table_exists("obsidian_sync_log"):
        op.create_table(
            "obsidian_sync_log",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("run_by", sa.Integer(), nullable=True),
            sa.Column("vault_path", sa.Text(), nullable=False),
            sa.Column("companies_new", sa.Integer(), server_default="0", nullable=False),
            sa.Column("companies_skip", sa.Integer(), server_default="0", nullable=False),
            sa.Column("holdings_new", sa.Integer(), server_default="0", nullable=False),
            sa.Column("holdings_skip", sa.Integer(), server_default="0", nullable=False),
            sa.Column("dividends_new", sa.Integer(), server_default="0", nullable=False),
            sa.Column("dividends_skip", sa.Integer(), server_default="0", nullable=False),
            sa.Column("errors", sa.Integer(), server_default="0", nullable=False),
            sa.Column("error_details", sa.JSON(), server_default="[]"),
            sa.Column("run_mode", sa.String(20), server_default="manual", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["run_by"], ["users.id"]),
        )

    # ── price_audits ─────────────────────────────────────────────────────────
    if not _table_exists("price_audits"):
        op.create_table(
            "price_audits",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("old_price", sa.Numeric(10, 2), nullable=True),
            sa.Column("new_price", sa.Numeric(10, 2), nullable=False),
            sa.Column("changed_at", sa.Date(), nullable=False),
            sa.Column("changed_by", sa.Integer(), nullable=True),
            sa.Column("source", sa.String(50), server_default="manual", nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        )
        op.create_index("ix_price_audits_company_id", "price_audits", ["company_id"])
        op.create_index("ix_price_audits_changed_at", "price_audits", ["changed_at"])

    # ── registrar_requirements ────────────────────────────────────────────────
    if not _table_exists("registrar_requirements"):
        op.create_table(
            "registrar_requirements",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("registrar_id", sa.Integer(), nullable=False),
            sa.Column("task_name", sa.String(200), nullable=False),
            sa.Column("document_title", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_required", sa.Boolean(), server_default="true", nullable=False),
            sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["registrar_id"], ["registrars.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_registrar_requirements_registrar_id", "registrar_requirements", ["registrar_id"])

    # ── registrar_documents ───────────────────────────────────────────────────
    if not _table_exists("registrar_documents"):
        op.create_table(
            "registrar_documents",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("registrar_requirement_id", sa.Integer(), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=True),
            sa.Column("file_name", sa.String(255), nullable=False),
            sa.Column("file_path", sa.String(512), nullable=False),
            sa.Column("file_size", sa.BigInteger(), server_default="0", nullable=False),
            sa.Column("mime_type", sa.String(100), server_default="application/octet-stream", nullable=False),
            sa.Column("status", sa.String(30), server_default="pending", nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("uploaded_by", sa.Integer(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["registrar_requirement_id"], ["registrar_requirements.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
            sa.CheckConstraint(
                "status IN ('pending','submitted','completed','rejected')",
                name="chk_registrar_document_status",
            ),
        )
        op.create_index("ix_registrar_documents_company_id", "registrar_documents", ["company_id"])
        op.create_index("ix_registrar_documents_registrar_requirement_id", "registrar_documents", ["registrar_requirement_id"])

    # ── registrar_contact_fields ──────────────────────────────────────────────
    if not _table_exists("registrar_contact_fields"):
        op.create_table(
            "registrar_contact_fields",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("registrar_id", sa.Integer(), nullable=False),
            sa.Column("field_type", sa.String(20), nullable=False),
            sa.Column("field_value", sa.Text(), nullable=False),
            sa.Column("label", sa.String(100), nullable=True),
            sa.Column("sort_order", sa.SmallInteger(), server_default="0", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["registrar_id"], ["registrars.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_registrar_contact_fields_registrar_id", "registrar_contact_fields", ["registrar_id"])
        op.create_index(
            "idx_registrar_contact_fields_registrar",
            "registrar_contact_fields",
            ["registrar_id"],
            postgresql_where=sa.text("deleted_at IS NULL"),
        )

    # ── nav_history ──────────────────────────────────────────────────────────
    if not _table_exists("nav_history"):
        op.create_table(
            "nav_history",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("snapshot_date", sa.Date(), nullable=False),
            sa.Column("total_value", sa.Numeric(18, 4), nullable=False),
            sa.Column("total_cost", sa.Numeric(18, 4), nullable=False),
            sa.Column("gain_loss", sa.Numeric(18, 4), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_nav_history_snapshot_date", "nav_history", ["snapshot_date"], unique=True)

    # ── admin_audit ──────────────────────────────────────────────────────────
    if not _table_exists("admin_audit"):
        op.create_table(
            "admin_audit",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("action", sa.String(50), nullable=False),
            sa.Column("entity_type", sa.String(50), nullable=False),
            sa.Column("entity_id", sa.String(50), nullable=True),
            sa.Column("old_value", sa.Text(), nullable=True),
            sa.Column("new_value", sa.Text(), nullable=True),
            sa.Column("performed_by", sa.Integer(), nullable=True),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["performed_by"], ["users.id"]),
        )
        op.create_index("ix_admin_audit_action", "admin_audit", ["action"])
        op.create_index("ix_admin_audit_performed_by", "admin_audit", ["performed_by"])

    # ── chatbot_conversations ────────────────────────────────────────────────
    if not _table_exists("chatbot_conversations"):
        op.create_table(
            "chatbot_conversations",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("matched_intent", sa.String(100), nullable=True),
            sa.Column("extracted_entities", sa.JSON(), nullable=True),
            sa.Column("execution_status", sa.String(20), server_default="matched", nullable=False),
            sa.Column("response", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        )
        op.create_index("ix_chatbot_conversations_user_id", "chatbot_conversations", ["user_id"])

    # ── checklist_runs ────────────────────────────────────────────────────────
    if not _table_exists("checklist_runs"):
        op.create_table(
            "checklist_runs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("admin_id", sa.Integer(), nullable=False),
            sa.Column("results_json", sa.JSON(), nullable=False),
            sa.Column("signoff_markdown", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["admin_id"], ["users.id"]),
        )
        op.create_index("ix_checklist_runs_admin_id", "checklist_runs", ["admin_id"])

    # ── audit_logs (legacy — Owl Alpha era, no current code references) ──────
    if not _table_exists("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("table_name", sa.String(50), nullable=False),
            sa.Column("record_id", sa.Integer(), nullable=False),
            sa.Column("action", sa.String(10), nullable=False),
            sa.Column("old_values", sa.JSON(), nullable=True),
            sa.Column("new_values", sa.JSON(), nullable=True),
            sa.Column("changed_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("changed_by", sa.String(50), server_default="admin"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("idx_audit_table_record", "audit_logs", ["table_name", "record_id"])

    # ── communication_logs (legacy — Owl Alpha era, no current code refs) ────
    if not _table_exists("communication_logs"):
        op.create_table(
            "communication_logs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("entity_type", sa.String(20), nullable=False),
            sa.Column("entity_id", sa.Integer(), nullable=True),
            sa.Column("communication_type", sa.String(20), nullable=False),
            sa.Column("contact_person", sa.String(255), nullable=True),
            sa.Column("communication_date", sa.Date(), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("status", sa.String(20), server_default="open"),
            sa.Column("priority", sa.String(10), server_default="medium"),
            sa.Column("follow_up_date", sa.Date(), nullable=True),
            sa.Column("next_action", sa.Text(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=True),
            sa.Column("attachments", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.CheckConstraint(
                "status IN ('open','pending','resolved','escalated')",
                name="chk_comm_status",
            ),
            sa.CheckConstraint(
                "communication_type IN ('email','phone','in_person','letter')",
                name="chk_comm_type",
            ),
            sa.CheckConstraint(
                "entity_type IN ('registrar','company','sec','ngx','other')",
                name="chk_entity_type",
            ),
            sa.CheckConstraint(
                "priority IN ('low','medium','high')",
                name="chk_priority",
            ),
        )
        op.create_index("idx_comms_date", "communication_logs", ["communication_date"])
        op.create_index("idx_comms_entity", "communication_logs", ["entity_type", "entity_id"])
        op.create_index("idx_comms_status", "communication_logs", ["status"])

    # ── Triggers ─────────────────────────────────────────────────────────────
    op.execute("""
        CREATE TRIGGER update_companies_updated_at
            BEFORE UPDATE ON companies
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_holdings_updated_at
            BEFORE UPDATE ON holdings
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_registrars_updated_at
            BEFORE UPDATE ON registrars
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # ── portfolio_summary (VIEW) ────────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE VIEW portfolio_summary AS
        SELECT c.ticker,
           c.name,
           c.sector,
           c.status,
           h.num_shares,
           h.average_cost_basis,
           h.total_cost,
           c.current_price,
           h.num_shares * COALESCE(c.current_price, 0::numeric) AS current_value,
           h.num_shares * COALESCE(c.current_price, 0::numeric) - h.total_cost AS unrealized_gain_loss,
           (h.num_shares * COALESCE(c.current_price, 0::numeric) - h.total_cost) / NULLIF(h.total_cost, 0::numeric) * 100::numeric AS return_pct
        FROM holdings h
          JOIN companies c ON h.company_id = c.id
        WHERE h.deleted_at IS NULL AND c.deleted_at IS NULL;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS portfolio_summary;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;")
    for table in [
        "communication_logs", "audit_logs", "checklist_runs",
        "chatbot_conversations", "admin_audit", "nav_history",
        "registrar_contact_fields", "registrar_documents",
        "registrar_requirements", "price_audits", "obsidian_sync_log",
        "claim_records", "price_history", "dividends", "transactions",
        "holdings", "companies", "registrars", "users",
    ]:
        op.drop_table(table)
