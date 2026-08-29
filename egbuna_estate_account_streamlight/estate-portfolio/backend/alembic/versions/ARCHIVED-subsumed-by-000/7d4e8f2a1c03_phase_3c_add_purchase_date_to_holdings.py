"""Phase 3C: add purchase_date to holdings

Revision ID: 7d4e8f2a1c03
Revises: 3f4739d78390
Create Date: 2026-07-03 17:30:00.000000+00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7d4e8f2a1c03'
down_revision: Union[str, None] = '6c0d4f3e5b27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('holdings', sa.Column('purchase_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('holdings', 'purchase_date')
