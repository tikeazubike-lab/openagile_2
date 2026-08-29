"""F-026: company_registrars join table, jurisdiction, security_type, due_date

Revision ID: d1e2f3a4b5c6
Revises: 000
Create Date: 2026-07-27
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "000"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _col_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    return column in {c["name"] for c in sa.inspect(conn).get_columns(table)}


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    return conn.dialect.has_table(conn, table)


def upgrade() -> None:
    # ── company_registrars join table ─────────────────────────────────────
    if not _table_exists("company_registrars"):
        op.create_table(
            "company_registrars",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("registrar_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(20), server_default="primary", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("company_id", "registrar_id"),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["registrar_id"], ["registrars.id"], ondelete="CASCADE"),
            sa.CheckConstraint("role IN ('primary', 'co_registrar')", name="chk_company_registrar_role"),
        )
        op.create_index("ix_company_registrars_company", "company_registrars", ["company_id"])
        op.create_index("ix_company_registrars_registrar", "company_registrars", ["registrar_id"])

        # Backfill from existing companies.registrar_id
        op.execute("""
            INSERT INTO company_registrars (company_id, registrar_id, role, created_at)
            SELECT id, registrar_id, 'primary', NOW()
            FROM companies
            WHERE registrar_id IS NOT NULL AND deleted_at IS NULL
            ON CONFLICT (company_id, registrar_id) DO NOTHING;
        """)

    # ── registrars.jurisdiction ───────────────────────────────────────────
    if not _col_exists("registrars", "jurisdiction"):
        op.add_column(
            "registrars",
            sa.Column("jurisdiction", sa.String(20), server_default="nigeria", nullable=False),
        )

    # ── companies.security_type ───────────────────────────────────────────
    if not _col_exists("companies", "security_type"):
        op.add_column(
            "companies",
            sa.Column("security_type", sa.String(20), server_default="equity", nullable=False),
        )

    # ── registrar_requirements.due_date ───────────────────────────────────
    if not _col_exists("registrar_requirements", "due_date"):
        op.add_column(
            "registrar_requirements",
            sa.Column("due_date", sa.Date(), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("registrar_requirements", "due_date")
    op.drop_column("companies", "security_type")
    op.drop_column("registrars", "jurisdiction")
    op.drop_table("company_registrars")
