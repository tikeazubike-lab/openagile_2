"""F-026b: Add reminder_log table for email reminder infrastructure

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-08-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    return conn.dialect.has_table(conn, table)


def upgrade() -> None:
    if not _table_exists("reminder_log"):
        op.create_table(
            "reminder_log",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("requirement_id", sa.Integer(), nullable=False),
            sa.Column("reminder_type", sa.String(20), nullable=False),
            sa.Column("recipient_email", sa.String(255), nullable=False),
            sa.Column("delivery_status", sa.String(20), nullable=False),
            sa.Column("error_detail", sa.Text(), nullable=True),
            sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["requirement_id"], ["registrar_requirements.id"]),
            sa.CheckConstraint("reminder_type IN ('upcoming', 'overdue')", name="chk_reminder_type"),
            sa.CheckConstraint("delivery_status IN ('sent', 'failed')", name="chk_delivery_status"),
        )
        op.execute("""
            CREATE INDEX idx_reminder_log_requirement_date
            ON reminder_log (requirement_id, sent_at);
        """)


def downgrade() -> None:
    op.drop_table("reminder_log")
