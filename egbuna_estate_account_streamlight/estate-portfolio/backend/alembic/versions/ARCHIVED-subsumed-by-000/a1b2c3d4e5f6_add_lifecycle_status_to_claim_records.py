"""Add lifecycle_status column to claim_records

Revision ID: a1b2c3d4e5f6
Revises: 8e5f9a3b2c04
Create Date: 2026-07-06 12:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8e5f9a3b2c04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'claim_records',
        sa.Column('lifecycle_status', sa.String(12),
                  nullable=False,
                  server_default='unresolved'),
    )
    op.create_check_constraint(
        "chk_lifecycle_status",
        "claim_records",
        "lifecycle_status IN ('unresolved', 'unclaimed', 'claimed')",
    )
    op.create_index(
        'ix_claim_records_lifecycle_status',
        'claim_records',
        ['lifecycle_status'],
    )


def downgrade() -> None:
    op.drop_index('ix_claim_records_lifecycle_status', table_name='claim_records')
    op.drop_constraint('chk_lifecycle_status', 'claim_records', type_='check')
    op.drop_column('claim_records', 'lifecycle_status')
